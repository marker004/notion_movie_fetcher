from typing import TypedDict


class PartialProvider(TypedDict):
    clear_name: str
    short_name: str


RELEVANT_STREAMING_SERVICES: list[PartialProvider] = [
    {"clear_name": "Netflix", "short_name": "nfx"},
    {"clear_name": "Amazon Prime Video", "short_name": "amp"},
    {"clear_name": "Disney Plus", "short_name": "dnp"},
    {"clear_name": "Apple TV Plus", "short_name": "atp"},
    {"clear_name": "Apple iTunes", "short_name": "itu"},
    {"clear_name": "Hulu", "short_name": "hlu"},
    {"clear_name": "HBO Max", "short_name": "hbm"},
    {"clear_name": "HBO Max Free", "short_name": "hmf"},
    {"clear_name": "Peacock", "short_name": "pct"},
    {"clear_name": "Peacock Premium", "short_name": "pcp"},
    {"clear_name": "Amazon Video", "short_name": "amz"},
    {"clear_name": "Google Play Movies", "short_name": "ply"},
    {"clear_name": "YouTube", "short_name": "yot"},
    {"clear_name": "Paramount Plus", "short_name": "pmp"},
    {"clear_name": "The Roku Channel", "short_name": "rkc"},
    {"clear_name": "YouTube Free", "short_name": "yfr"},
    {"clear_name": "Hoopla", "short_name": "hop"},
    {"clear_name": "Vudu", "short_name": "vdu"},
    {"clear_name": "VUDU Free", "short_name": "vuf"},
    {"clear_name": "PBS", "short_name": "pbs"},
    {"clear_name": "Shudder", "short_name": "shd"},
    {"clear_name": "Pluto TV", "short_name": "ptv"},
    {"clear_name": "Plex", "short_name": "plx"},
    {"clear_name": "Tubi TV", "short_name": "tbv"},
    {"clear_name": "Kanopy", "short_name": "knp"},
]
