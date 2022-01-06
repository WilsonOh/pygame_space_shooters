import json


with open("sav_data.json") as sav:
    data = json.load(sav)


def write_data(player, player_name):
    player_acc = float(f"{(player.number_hit/player.total_shots * 100):.2f}")
    if data['players'][player_name]['accuracy'] < player_acc and \
            player.get_number_hit > data['players'][player_name]['high_score']:
        data['players'][player_name]['accuracy'] = player_acc
    if data['players'][player_name]['high_score'] < player.number_hit:
        data['players'][player_name]['high_score'] = player.number_hit
    if data['players'][player_name]['highest_level'] < player.highest_level:
        data['players'][player_name]['highest_level'] = player.highest_level
    with open("sav_data.json", 'w') as updated:
        json.dump(data, updated, indent=2)


def create_data(player_name):
    data['players'][player_name] = {}
    data['players'][player_name]['accuracy'] = 0.00
    data['players'][player_name]['high_score'] = 0
    data['players'][player_name]['highest_level'] = 1
    with open("sav_data.json", 'w') as updated:
        json.dump(data, updated, indent=2)


def clear_name(name):
    if name in data['players']:
        del data['players'][name]
        with open("sav_data.json", 'w') as updated:
            json.dump(data, updated, indent=2)
        print(f"{name} got removed successfully")
    else:
        print(f"Player {name} does not exist")

