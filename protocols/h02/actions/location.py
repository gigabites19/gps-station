import re
from protocols.base_location import BaseLocation
from helpers.chunks import get_chunks


class Location(BaseLocation):
    # TODO: this is already defined elsewhere
    LOCATION_REGEX = r'^\*([A-Z]+),(\d{10}),(V\d),(\d{6}),(A|B|V),(-?\d{4}.\d{4}),(N|S),(-?\d{5}.\d{4}),(E|W),(\d{1,3}.\d{2}),(\d{1,3}),(\d{6}),([0-9A-Fa-f]+),(\d+),(\d+),(\d+),(\d+)#$'

    def __init__(self, regex_match: re.Match, _raw_data: str) -> None:
        """
        Initializes all the parameters that don't need any transformation and can be grabbed straight out of regex.

        :param _maker: Manufacturer of the device
        :param _device_serial_number: factory set device ID
        :param _validity: Sent in data's validity, it's either valid or it's not.
        :param _direction: Direction, azimuth at 000 is pointing to north.
        :param _mobile_country_code: Mobile country code, 282 is for Georgia
        :param _mobile_network_code: Operator ID, i.e. Geocell, Beeline, Magti etc... 02 is Geocell.
        :param _local_area_code: Code of the area the device is in at the moment
        :param _cell_id: Base Transceiver Station ID
        """

        # This is a location data sent as a command confirmation.
        if regex_match.group(3) == 'V4':
            # Transform command confirmation data packet to look like a normal location data and
            regex_match = re.match(self.LOCATION_REGEX, re.sub(r'V4,S20,(OK|DONE),\d{6}', 'V1', _raw_data))

        self.regex_match = regex_match
        self._raw_data = _raw_data

        # FIXME: this is clunky
        self.vehicle_status_bytes = [i for i in get_chunks(regex_match.group(13), 2)]
        self.vehicle_status_first_byte = self.vehicle_status_bytes[0]
        self.vehicle_status_second_byte = self.vehicle_status_bytes[1]
        self.vehicle_status_third_byte = self.vehicle_status_bytes[2]
        self.vehicle_status_fourth_byte = self.vehicle_status_bytes[3]

        self._maker = self.regex_match.group(1)
        self._device_serial_number = self.regex_match.group(2)
        self._time = self.regex_match.group(4)
        self._direction = self.regex_match.group(11)
        self._mobile_country_code = self.regex_match.group(14)
        self._mobile_network_code = self.regex_match.group(15)
        self._local_area_code = self.regex_match.group(16)
        self._cell_id = self.regex_match.group(17)

    @property
    def _valid(self) -> bool:
        if self.regex_match.group(5) == 'A':
            return True

        return False

    @property
    def _accessories_off(self) -> bool:
        """
        Checks the bit telling us about the ACC status, either it's on or off.

        :returns: State of the ACC
        :rtype: int
        """
        acc = self.get_bit_state(self.vehicle_status_third_byte, 3)

        return acc

    @property
    def _speed(self) -> float:
        """
        Protocol sends the speed data in knots/h

        :returns: knots/h converted to km/h
        :rtype: float
        """
        raw_speed = self.regex_match.group(10)

        kmh = float(raw_speed) * 1.852
        kmh_formatted = format(kmh, '05.2f')

        if not self._accessories_off:
            return float(kmh_formatted)

        return 0.00

    @property
    def _latitude(self) -> float:
        """
        Data sent in is in the format of DDMM.MMMM where D = degrees and M = minutes.
        i.e. 4413.5467 is 44 degrees and 13.5467 minutes.

        :returns: DDMM.MMMM converted to Decimal Degrees
        :rtype: float
        """
        latitude_raw = self.regex_match.group(6)
        pattern = re.compile(r'(-?\d{2})(\d{2}.\d{4})')
        match = re.match(pattern, latitude_raw)

        degrees = int(match.group(1))
        minutes = float(match.group(2))

        result = degrees + minutes/60
        result_formatted = format(result, '.6f')

        return float(result_formatted)

    @property
    def _longitude(self) -> float:
        """
        Data sent in is in the format od DDDMM.MMMM where D = degrees and M = minutes.
        i.e. 12754.4324 is 127 degrees and 54.4324 minutes.

        :returns: DDDMM.MMMM converted to Decimal Degrees
        :rtype: float
        """
        longitude_raw = self.regex_match.group(8)
        pattern = re.compile(r'(-?\d{3})(\d{2}.\d{4})')
        match = re.match(pattern, longitude_raw)

        degrees = int(match.group(1))
        minutes = float(match.group(2))

        result = degrees + minutes/60
        formatted_result = format(result, '.6f')

        return float(formatted_result)

    @property
    def _cut_fuel(self) -> bool:
        cut_fuel = self.get_bit_state(self.vehicle_status_first_byte, 4)

        return cut_fuel

    def get_bit_state(self, hex_byte: str, attribute_bit_location: int) -> bool:
        """
        Used for getting values from hex bitmask sent in by the protocol.

        Protocol sends in total of "4" bytes (it's not really hex, just ASCII representation),
        Each byte corresponds to 8 values (not all of them, some are just there...
        see documentation for more). i.e. server could send in 'FFFF9FFF', first byte is FF, second byte is FF,
        third byte is 9F, and last fourth byte is FF. The attributes of our interest can be in any of those.
        If we convert FF to decimal we get 255, or 11111111 in binary.
        Protocol adopts negative logic, so when bit is 1 it means false, thus 0 is true.

        :param hex_byte: hex byte, i.e. two values, e.g. F9
        :type hex_byte: str
        :param attribute_bit_location: Location of the attribute that interests us, see the H02 documentation.
        :type attribute_bit_location: int
        :returns: Value of attribute, either active or inactive
        :rtype: int
        """
        byte_val = int(hex_byte, 16)

        mask = 0b1 << attribute_bit_location - 1

        # Protocol adopts negative logic, 0 = valid
        return not byte_val & mask

    @property
    def gprs_blocked(self) -> bool:
        gprs_blocked = self.get_bit_state(self.vehicle_status_first_byte, 3)

        return gprs_blocked
