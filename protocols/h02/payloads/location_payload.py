from dataclasses import dataclass

from protocols.payloads import BaseLocationPayload

@dataclass(frozen=True)
class H02Location(BaseLocationPayload):
    maker: str
    device_serial_number: str
    time: str
    valid: bool
    speed: float
    accessories_off: bool
    direction: str
    mobile_country_code: str
    mobile_network_code: str
    local_area_code: str
    cell_id: str
    cut_fuel: bool
    shock_alarm: bool
    battery_cut_off: bool

