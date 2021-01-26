import logging
from random import randrange, sample


def check_budget(players, properties):
    """Check each player's budget in order to eliminate losers, in case there are any.
    Condition: budget < 0
    """
    try:
        remaining_players = [player for player in players if player["Budget"] >= 0]
        # If anyone was eliminated, remove properties from that player.
        if len(players) > len(remaining_players):
            loser = [player for player in players if player not in remaining_players][0]
            remove_properties_from_player(loser, properties)
    # This should never occur, but a log is saved in case it ever does.
    except IndexError:
        logging.error("Exception occurred in check_budget()", exc_info=True)
        return None
    return remaining_players


def remove_properties_from_player(player, properties):
    """Remove ownership from eliminated player by checking each property."""
    for property in properties:
        if property["Owner"] == player["Name"]:
            property["Owner"] = None
    return properties


def buy_property(player, property):
    """Attempt to buy property according to each player buy condition.
    Players must have the required budget in order to purchase a property.

    Impulsive: Buys any property.

    Exigent: Buys any property costing above 500.

    Cautious: Buys as long as 80 credits remain after purchase.

    Random: Buys any property with a 50% chance.
    """
    try:
        if player["Personality"] == "Impulsive":
            property["Owner"] = player["Name"]
            player["Budget"] -= property["Value"]
        elif player["Personality"] == "Exigent" and property["Value"] > 500:
            property["Owner"] = player["Name"]
            player["Budget"] -= property["Value"]
        elif (
            player["Personality"] == "Cautious"
            and player["Budget"] - property["Value"] >= 80
        ):
            property["Owner"] = player["Name"]
            player["Budget"] -= property["Value"]
        elif player["Personality"] == "Random":
            # 50% chance to try.
            if randrange(2):
                property["Owner"] = player["Name"]
                player["Budget"] -= property["Value"]
    # This should never occur, but a log is saved in case it ever does.
    except KeyError:
        logging.error("Exception occurred in buy_property()", exc_info=True)


def pay_rent(player, property, players):
    """Pay rent in case current property already has an owner."""
    has_landlord = property["Owner"]
    rent_price = property["Rent"]
    if has_landlord:
        landlord = get_landlord(players, has_landlord)
        # Pay the landlord and deduce rent price from visitor.
        if landlord in players:
            landlord["Budget"] += rent_price
            player["Budget"] -= rent_price
        return landlord["Budget"], player["Budget"]


def get_landlord(players, has_landlord):
    """Checks whether or not the current property is owned by the player we are checking.

    Receives the value contained in property["Owner"] then checks it against our pool of players.

    Returns the specified landlord, in case there is one, or None.
    """
    try:
        landlord = [player for player in players if player["Name"] == has_landlord][0]
    # This should never occur, but a log is saved in case it ever does.
    except IndexError:
        logging.error("Exception occurred in get_landlord()", exc_info=True)
        return None
    return landlord


def create_game_table(properties, random_property_values):
    """Receives a list of 20 properties and random values which are used
    to assign a value to each property, then returns a dict(the table itself)
    in the following format:

    {
        "Estate": estate -> property,
        "Value": value -> randomly generated,
        "Rent": rent -> value * 0.10,
        "Owner": owner -> initially None
    }
    """
    table = []
    for estate, value in zip(properties, random_property_values):
        table_cell = {
            "Estate": estate,
            "Value": value,
            "Rent": round(value * 0.10),
            "Owner": None,
        }
        table.append(table_cell)
    return table


def play_game(game_data, players, property_catalog):
    current_cell, turns = 0, 0
    remaining_players = players
    while turns < 1000 and len(remaining_players) > 1:
        for player in players:
            # Check remaining players after each turn so there's no chance of 0 players remaining.
            remaining_players = check_budget(players, property_catalog)
            # If there is only one remaining player, game is over.
            if len(remaining_players) == 1 or len(players) != len(remaining_players):
                players = remaining_players
                break
            # If current player was eliminated, skip to next player.
            elif len(players) != len(remaining_players):
                players = remaining_players
                continue
            # Start at 1 so the players are always moving ahead,
            # otherwise there could be multiple rolled 0s in a row.
            move = randrange(1, 7)
            current_cell += move
            # Check if players went through entire table and if so, start over.
            if current_cell > 20:
                [player["Budget"] + 100 for player in remaining_players]
                current_cell %= 10
            property = property_catalog[
                current_cell - 1  # List starts at 0, must subtract 1.
            ]
            # Pay rent if property has an owner.
            if property["Owner"]:
                pay_rent(player, property, players)
            # Else check if it's possible to buy the property.
            elif player["Budget"] >= property["Value"]:
                buy_property(player, property)
            turns += 1
            # Game timeout condition.
            if turns == 1000:
                game_data["Timeout"] += 1
                break
    # Get winner. Also satisfies both timeout win condition(highest budget)
    # and tie breaker(by player order).
    winner = max(players, key=lambda player: player["Budget"])["Personality"]
    game_data["Traits"][winner] += 1
    game_data["Total Turns"] += turns


if __name__ == "__main__":
    # Config logger to save a log.txt file to root dir
    logging.basicConfig(filename="log.txt", filemode="w", level=logging.DEBUG)
    # Game data. Gets incremented as games are played.
    game_data = {
        "Timeout": 0,  # Finished by timeout
        "Total Turns": 0,
        "Traits": {
            "Impulsive": 0,  # Wins
            "Exigent": 0,  # Wins
            "Cautious": 0,  # Wins
            "Random": 0,  # Wins
        },
    }
    # Get list of properties from a txt in the current folder.
    # This was only done to make the program/code easier to visualize.
    try:
        with open("propriedades.txt", "r") as f:
            properties = f.read().splitlines()
    # Generate dummy data in case there is no .txt file.
    except (IOError, FileNotFoundError):
        properties = [f"Placeholder {num}" for num in range(20)]
    total_games = 300
    for _ in range(total_games):
        # Every player and their respective budgets.
        players = [
            {"Name": "Player One", "Personality": "Impulsive", "Budget": 300},
            {"Name": "Player Two", "Personality": "Exigent", "Budget": 300},
            {"Name": "Player Three", "Personality": "Cautious", "Budget": 300},
            {"Name": "Player Four", "Personality": "Random", "Budget": 300},
        ]
        # Shuffle players, this is done at the start of each match.
        starting_order = sample(players, len(players))
        # Generate random values for each property at the start of each match.
        random_property_values = [randrange(200, 4500) for _ in range(20)]
        # Generate the game table.
        table = create_game_table(properties, random_property_values)
        play_game(game_data, starting_order, table)
    print(
        f"\nTerminadas por time out: {game_data['Timeout']}\n"
        f"\nMédia de turnos: {game_data['Total Turns'] / total_games:.2f}\n"
        f"\nPorcentagem de vitória por personalidade:\n"
        f"Impulsivo: {game_data['Traits']['Impulsive'] / total_games * 100:.2f}%\n"
        f"Exigente: {game_data['Traits']['Exigent'] / total_games * 100:.2f}%\n"
        f"Cauteloso: {game_data['Traits']['Cautious'] / total_games * 100:.2f}%\n"
        f"Aleatório: {game_data['Traits']['Random'] / total_games * 100:.2f}%\n"
        f"\nComportamento mais vencedor: {max(game_data['Traits'], key=game_data['Traits'].get)}\n"
    )
