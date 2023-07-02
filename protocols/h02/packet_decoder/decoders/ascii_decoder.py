import re
from typing import Literal

from protocols.exceptions import RegExMatchError

from protocols.h02.payloads import H02Location

REGEX_PATTERN = re.compile(r'^\*HQ,(\d{10}),(V\d),(\d{6}),(A|V),(-?\d{4}.\d{4}),(N|S),(-?\d{4,5}.\d{4}),(E|W),(\d{1,3}.\d{2}),(\d{1,3}),(\d{6}),([0-9A-Fa-f]{8}),(\d+),(\d+),(\d+),(\d+)(,\d+)?#$')

def decode_h02_ascii_packet(data_packet: bytes) -> H02Location:
    """Decode ASCII location data packet sent by a device that uses H02 protocol.

    Args:
        data_packet:
            Raw bytes sent by a device

    Returns:
        H02Location data class that contains all necessary fields for the data packet to be saved in the backend.

    Raises:
        RegExMatchError: If `REGEX_PATTERN` does not match decoded `data_packet` or regex pattern in one of the `decode_{param}` functions does not receive parameter in expected format.
        UnicodeDecodeError: If `raw_bytes` could not be decoded by UTF-8 codec.
    """
    try:
        raw_data = data_packet.decode()
    except UnicodeDecodeError:
        raise

    match = REGEX_PATTERN.match(raw_data)

    if match is None:
        raise RegExMatchError(f'H02 protocol\'s ASCII mode pattern could not match "{raw_data}".')

    vehicle_status = match.group(12)

    latitude = decode_latitude(match.group(5))
    longitude = decode_longitude(match.group(7))
    maker = 'HQ'
    device_serial_number = match.group(1)
    time = match.group(3)
    valid = match.group(4) == 'A'
    speed = decode_speed(match.group(9))
    accessories_off = decode_bitmask(vehicle_status, 3, 3)
    direction = match.group(10)
    mobile_country_code = match.group(13)
    mobile_network_code = match.group(14)
    local_area_code = match.group(15)
    cell_id = match.group(16)
    cut_fuel = decode_bitmask(vehicle_status, 1, 4)
    shock_alarm = decode_bitmask(vehicle_status, 2, 2)
    battery_cut_off = decode_bitmask(vehicle_status, 2, 4)

    return H02Location(latitude, longitude, raw_data, maker, device_serial_number, time, valid, speed, accessories_off, direction, mobile_country_code, mobile_network_code, local_area_code, cell_id, cut_fuel, shock_alarm, battery_cut_off)

def decode_latitude(latitude: str) -> float:
    """Decode latitude sent by a H02 protocol device.

    Decode H02 protocol latitude format `MMDD.DDDD` e.g. `4431.3212`
    is `44` degrees and `31.3212` minutes.

    Args:
        latitude: Latitude in the H02 packet sent by the device.

    Returns:
        Latitude converted to a float that can be used with longitude to display a point on a map.

    Raises:
        RegExMatchError: If regex pattern does not match `latitude` parameter. 
    """
    h02_latitude_pattern = re.compile(r'^(-?\d{2})(\d{2}.\d{4})$')
    match = h02_latitude_pattern.match(latitude)

    if match is None:
        raise RegExMatchError(f'Could not decode H02 protocol\'s latitude parameter: "{latitude}"') 

    degrees = int(match.group(1))
    minutes = float(match.group(2))

    result: float = degrees + minutes / 60
    result_formatted = format(result, '.6f')

    return float(result_formatted)

def decode_longitude(longitude: str) -> float:
    """Decode longitude sent by a H02 protocol device.

    Decode H02 protocol longitude format `MMMDD.DDDD` e.g. `12044.2892`
    is `120` degrees and `44.2892` minutes.

    Args:
        longitude: Longitude in the H02 packet sent by the device.

    Returns:
        Longitude converted to a float that can be used with latitude to display a point on a map.

    Raises:
        RegExMatchError: If regex pattern does not match `longitude` parameter. 
    """
    h02_longitude_pattern = re.compile(r'^(-?(\d{3}|0?\d{2}))(\d{2}.\d{4})$')
    match = h02_longitude_pattern.match(longitude)

    if match is None:
        raise RegExMatchError(f'Could not decode H02 protocol\'s longitude parameter: "{longitude}".') 

    degrees = int(match.group(1))
    minutes = float(match.group(3))

    result = degrees + minutes / 60
    formatted_result = format(result, '.6f')

    return float(formatted_result)

def decode_speed(speed: str) -> float:
    """Decode speed parameter of H02 protocol.

    Convert and return speed of device. Convert from knots/h to km/h.
    e.g. `speed=14` in km/h is `14 * 1.852`km/h.

    Args:
        speed: Speed parameter from the packet.

    Returns:
        Speed converted to km/h.
    """
    kmh = float(speed) * 1.852
    kmh_formatted = format(kmh, '05.2f')

    return float(kmh_formatted)

def decode_bitmask(
        vehicle_status: str, 
        target_byte_order: Literal[1, 2, 3, 4],
        target_bit_order: Literal[1, 2, 3, 4, 5, 6, 7, 8]
    ) -> bool:
    """Decode bitmask of H02 protocol's `vehicle_status` parameter.

    Decode bitmask of H02 protocol's `vehicle_status` parameter. Protocol adopts negative logic, so `0 = True`.
    For example if `accessories_off` is `0` it means `accessories_off = True`, and vice-versa, `accessories_off = 1` means
    `accessories_off = False`. `cut_fuel = 0` means vehicle is in cut fuel state, etc...

    Args:
        vehicle_status:
            `vehicle_status` part of the packet sent by H02 protocol device.
        target_byte_order:
            Order of the target byte in the `vehicle_status`.
        target_bit_order:
            Order of the target parameter bit in the byte (byte here means byte with order as provided by `target_byte_order` parameter).

    Returns:
        `True` if target bit is 0, `False` otherwise.
    """
    byte: int 

    match target_byte_order:
        case 1:
            byte = int(vehicle_status[0:2], 16)
        case 2:
            byte = int(vehicle_status[2:4], 16)
        case 3:
            byte = int(vehicle_status[4:6], 16)
        case 4:
            byte = int(vehicle_status[6:8], 16)

    mask = 0b1 << target_bit_order - 1

    return not byte & mask

