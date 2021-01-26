from main import check_budget, remove_properties_from_player, get_landlord, pay_rent
from random import choice, randrange

import pytest


@pytest.fixture
def players():
    players = [
            {"Name": "José", "Personality": "Impulsive", "Budget": 15000},
            {"Name": "Maria", "Personality": "Exigent", "Budget": 15000},
            {"Name": "João", "Personality": "Cautious", "Budget": 15000},
            {"Name": "Marta", "Personality": "Random", "Budget": 15000},
    ]
    return players


@pytest.fixture
def properties():
    properties = [f"Placeholder {num}" for num in range(20)]
    random_property_values = [randrange(200, 4500) for _ in range(20)]
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


@pytest.fixture
def game_data():
    game_data = {
        "Timeout": 0,
        "Total Turns": 0,
        "Traits": {
            "Impulsive": 0,
            "Exigent": 0,
            "Cautious": 0,
            "Random": 0,
        },
    }
    return game_data


def test_check_budget(players, properties):
    # Removing a player each iteration
    starting_amount = len(players)
    current_index = 0
    for player in [players]:
        player[current_index]["Budget"] *= -1
        current_index += 1
        result = check_budget(players, properties)
        assert len(result) == starting_amount - current_index


def test_remove_properties_from_player(properties):
    owned_properties = properties
    for property in owned_properties:
        property["Owner"] = "Test Player"
    player = {"Name": "Test Player"}
    assert remove_properties_from_player(player, owned_properties) == properties


def test_pay_rent(players, properties):
    renter = players[0]
    landlord = players[1]
    # Old landlord budget.
    landlord_budget = [player["Budget"] for player in players if player == landlord][0]
    # Old renter budget.
    renter_budget = [player["Budget"] for player in players if player == renter][0]
    for property in properties:
        # Assign property to landlord
        property["Owner"] = landlord["Name"]
        # Check if landlord budget increased and renter budget decreased.
        assert (
            pay_rent(renter, property, players)[0] > landlord_budget
            and pay_rent(renter, property, players)[1] < renter_budget
        )


def test_get_landlord(players, properties):
    for skip, property in enumerate(properties):
        if skip % 2 == 0:
            random_player = choice(players)["Name"]
            has_landlord = property["Owner"] = random_player
            get_landlord(players, has_landlord)
        has_landlord = None


if __name__ == "__main__":
    pytest.main()
