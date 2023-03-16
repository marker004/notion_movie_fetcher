from __future__ import annotations
from typing import Literal, Optional, cast
from pydantic import BaseModel, Field, validator
from constants import RELEVANT_STREAMING_SERVICES
from shared_items.utils import pp, reversor


class LetterboxdMovie(BaseModel):
    film_id: str = Field(alias="data-film-id")
    title: str = Field(alias="data-film-name")
    release_year: int = Field(alias="data-film-release-year")
    letterboxd_url: str = Field(alias="data-film-link")
    justwatch_watch_option: Optional[WatchOption] = None
    runtime: Optional[str] = None
    genres: Optional[list[str]] = []

    def formatted_location(self) -> str:
        if self.justwatch_watch_option:
            if self.justwatch_watch_option.is_streaming():
                return self.justwatch_watch_option.name
            else:
                return f"{self.justwatch_watch_option.type.capitalize()} ${self.justwatch_watch_option.price}"
        else:
            return ''


class LetterboxdResponseCollection(BaseModel):
    movies: list[LetterboxdMovie]


watch_option_types = {
    'flatrate': 1,
    'free': 1,
    'ads': 2,
}

# JustWatch things below
class WatchOption(BaseModel):
    name: str
    format: str
    type: str
    price: Optional[str]

    @property
    def type_orderer(self) -> int:
        return watch_option_types.get(self.type, 3)

    @validator("price", pre=True)
    def assure_default_price(cls, value):
        return value or "0"

    def is_streaming(self) -> bool:
        return self.type == 'flatrate' or self.type == 'ads' or self.type == 'free'

    def is_rental(self) -> bool:
        return self.type == 'rent'

    def is_buy(self) -> bool:
        return self.type == 'buy'


class WatchOptionGrouping(BaseModel):
    stream: list[WatchOption]
    rent: list[WatchOption]
    buy: list[WatchOption]

    @staticmethod
    def ordered_watch_types() -> list[str]:
        return ["stream", "rent", "buy"]


class WatchOptionCollection(BaseModel):
    type: Literal["stream", "rent", "buy"]
    watch_options: list[WatchOption]

    def best_option(self) -> Optional[WatchOption]:
        if self.type == "stream":
            streaming_names = [
                service["clear_name"] for service in RELEVANT_STREAMING_SERVICES
            ]
            return next(
                (
                    option
                    for option in self.watch_options
                    if option.name in streaming_names
                ),
                None,
            )
        else:
            return self.watch_options[0] if self.watch_options else None

    @validator("watch_options")
    def order_watch_options(cls, value):
        value = cast(list[WatchOption], value)
        return sorted(value, key=lambda k: (k.price, k.type_orderer))


class LetterboxdJustwatchResult(BaseModel):
    best: WatchOptionGrouping
    four_k: WatchOptionGrouping = Field(alias="4k")
    hd: WatchOptionGrouping
    sd: WatchOptionGrouping

    @staticmethod
    def ordered_collections() -> list[str]:
        return ["four_k", "hd", "sd"]

    def ordered_watch_options(self) -> dict[str, list]:
        all_watch_options: dict[str, list] = dict(
            (el, []) for el in WatchOptionGrouping.ordered_watch_types()
        )
        for collection in self.ordered_collections():
            for type in WatchOptionGrouping.ordered_watch_types():
                cast_collection = cast(WatchOptionGrouping, getattr(self, collection))
                watch_options = cast(list[WatchOption], getattr(cast_collection, type))
                all_watch_options[type] += watch_options

        return all_watch_options

    def ordered_watch_collections(self) -> dict[str, WatchOptionCollection]:
        return {
            watch_type: WatchOptionCollection(
                type=watch_type, watch_options=option_list
            )
            for watch_type, option_list in self.ordered_watch_options().items()
        }

    def best_option(self) -> Optional[WatchOption]:
        ordered_watch_collections = self.ordered_watch_collections()
        return (
            ordered_watch_collections["stream"].best_option()
            or ordered_watch_collections["rent"].best_option()
            or ordered_watch_collections["buy"].best_option()
        )