from dataclasses import dataclass

@dataclass(frozen=True) # TODO: require subclasses to define `protocol` field
class BaseLocationPayload:
    latitude: float
    longitude: float
    raw_data: str

