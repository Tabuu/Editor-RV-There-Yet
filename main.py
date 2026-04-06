from sys import argv as args

import struct


def load_game(file_name: str) -> bytes:
    with open(file_name, 'rb') as file:
        while (data := file.read()):
            return data


def save_game(data: bytes, file_name: str):
    with open(file_name, 'wb') as file:
        file.write(data)


def get_int_property_offset(data: bytes, property_name: str) -> int:
    name_to_bits = property_name.encode('ascii')
    type_to_bits = 'IntProperty'.encode('ascii')
    
    found_index = data.find(name_to_bits)
    if found_index == -1:
        return -1

    prop_index = data.find(type_to_bits, found_index)
    value_index = prop_index + len(type_to_bits) + 7 # (IntProperty = 11 bytes, + 5 = 16 bytes of type name, + 2 bytes for data length as a short, = 7)

    return value_index


def get_int_property(data: bytes, property_name: str) -> int:
    offset = get_int_property_offset(data, property_name)
    if offset == -1:
        return 0
    return struct.unpack_from('>I', data, offset)[0]


def set_int_property(data: bytes, property_name: str, value: int) -> bytes:
    offset = get_int_property_offset(data, property_name)
    if offset > -1:
        new_data = bytearray(data)
        struct.pack_into('>I', new_data, offset, value)
        return new_data
    print(f'Error: Could not find property {property_name}')


def get_all_known_values(data: bytes) -> dict:
    properties = [
        'CurrentCheckpoint',
        'EpicPens',
        'VehicleParts',
        'DamageType.Engine',
        'DamageType.Tire.RR',
        'DamageType.Tire.RL',
        'DamageType.Tire.FR',
        'DamageType.Tire.FL',
        'DamageType.Frame',
        # 'DamageType.Player.Fire',
    ]

    return {k: get_int_property(data, k) for k in properties}


def get_game_files(file_path: str) -> (str, str):
    split = file_path.split('.')
    meta = f'.{split[-2]}.meta.sav'
    return file_path, meta


def main():
    input_game_file, input_meta_file = get_game_files(args[1])
    output_game_file, output_meta_file = get_game_files(args[2])

    game_file = load_game(input_game_file)
    meta_file = load_game(input_meta_file)

    print(*[f'{k:25}:{v:6d}' for k,v in get_all_known_values(game_file).items()], sep='\n')

    # game_file = set_int_property(game_file, 'DamageType.Engine', 100)
    game_file = set_int_property(game_file, 'CurrentCheckpoint', 10)

    save_game(game_file, output_game_file)
    save_game(meta_file, output_meta_file)


if __name__ == "__main__":
    main()