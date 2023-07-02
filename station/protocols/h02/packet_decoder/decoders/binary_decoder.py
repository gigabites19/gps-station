from typing import List

from protocols.h02.payloads.location_payload import H02Location

from .ascii_decoder import decode_bitmask, decode_latitude, decode_longitude, decode_speed

def decode_h02_binary_packet(raw_bytes: bytes) -> H02Location:
    """Decode binary location data packet sent by a device that uses H02 protocol.

    Decode binary data packet, also referred to as "starard mode" packet in the H02 protocol documentation.

    Args:
        raw_bytes:
            Raw bytes sent by a device.

    Returns:
        H02Location data class that contains all necessary fields for the data packet to be saved in the backend.

    Raises:
        RegExMatchError: If one of the `decode_{param}` functions does not receive its argument in expected format.
    """
    bytes_list = list(raw_bytes)

    vehicle_status = bytes_to_hex(bytes_list[0x19:0x1D])

    latitude = bytes_to_hex(bytes_list[0x0C:0x10])
    latitude = decode_latitude(f'{latitude[0:4]}.{latitude[4:]}')
    longitude = bytes_to_hex(bytes_list[0x11:0x16])
    valid = (int(longitude[-1], 16) & 0b1 << 1) != 0  # check H02 docs for clarification (15th byte in standard mode)
    longitude = decode_longitude(f'{longitude[0:5]}.{longitude[5:-1]}')
    raw_data = ','.join([str(i) for i in bytes_list])
    maker = 'HQ'
    device_serial_number = bytes_to_hex(bytes_list[0x01:0x06])
    time = bytes_to_hex(bytes_list[0x06:0x09])
    speed = decode_speed(bytes_to_hex(bytes_list[0x16:0x19])[0:3])
    accessories_off = decode_bitmask(vehicle_status, 3, 3)
    direction = '100'  # NOTE: not using this anyways, probably should be removed from database
    mobile_country_code = '000' # NOTE: standard mode does not specify this value
    mobile_network_code = '00' # NOTE: standard mode does not specify this value
    local_area_code = '000' # NOTE: standard mode does not specify this value
    cell_id = '0000' # NOTE: standard mode does not specify this value
    cut_fuel = decode_bitmask(vehicle_status, 1, 4)
    shock_alarm = decode_bitmask(vehicle_status, 2, 2)
    battery_cut_off = decode_bitmask(vehicle_status, 2, 4)

    return H02Location(latitude, longitude, raw_data, maker, device_serial_number, time, valid, speed, accessories_off, direction, mobile_country_code, mobile_network_code, local_area_code, cell_id, cut_fuel, shock_alarm, battery_cut_off)

def bytes_to_hex(byte_nums: List[int]) -> str:
    """Convert list of integers (each representing a byte) to their hex representation and stick them together.

    Args:
        byte_nums:
            List of integers, each integer represents a byte.

    Returns:
        Hexadecimal value of each byte combined into a single string.
        Single-digit values are padded with 0. e.g. `9` => `09`.
    """
    result = ''
    
    for byte in byte_nums:
        hex_value = hex(byte).split('0x')[1]

        if len(hex_value) == 1:
            # single-digit values must be padded for correct interpretation of H02 protocol standard mode
            result += f'0{hex_value}'
        else:
            result += hex_value

    return result

