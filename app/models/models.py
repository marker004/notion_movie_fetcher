from pydantic import BaseModel
from typing import Optional
from shared_items.utils import pp, strip_all_punctuation, reversor

from constants import RELEVANT_STREAMING_SERVICES


class Provider(BaseModel):
    addon_packages: Optional[list[str]]
    clear_name: str
    data: dict
    display_priority: int
    icon_blur_hash: str
    icon_url: str
    id: int
    monetization_types: Optional[list[str]]
    parent_packages: Optional[list[str]]
    priority: int
    short_name: str
    slug: str
    technical_name: str


class ProviderCollection(BaseModel):
    providers: list[Provider]

    def relevant_providers(self) -> list[Provider]:
        relevant_streaming_ids_short_names = list(
            map(lambda x: x["short_name"], RELEVANT_STREAMING_SERVICES)
        )

        return [
            provider
            for provider in self.providers
            if provider.short_name in relevant_streaming_ids_short_names
        ]


class Offer(BaseModel):
    country: str
    currency: Optional[str]
    jw_entity_id: str
    monetization_type: str
    package_short_name: str
    presentation_type: str
    provider_id: int
    urls: dict
    retail_price: Optional[float]
    providers: Optional[list[Provider]]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def price(self) -> Optional[str]:
        return None if self.streaming else str(self.retail_price)

    @property
    def streaming(self) -> bool:
        return self.monetization_type == "flatrate"

    @property
    def rental(self) -> bool:
        return self.monetization_type == "rent"

    @property
    def watch_type(self) -> str:
        return "streaming" if self.streaming else "rental"

    @property
    def hd(self) -> bool:
        return self.presentation_type == "hd"

    @property
    def four_k(self) -> bool:
        return self.presentation_type == "4k"

    @property
    def watchable(self) -> bool:
        return self.four_k or self.hd

    @property
    def relevant(self) -> bool:
        return self.package_short_name in [
            provider.short_name for provider in (self.providers or [])
        ]

    @property
    def for_me(self) -> bool:
        return (self.streaming or self.rental) and self.watchable and self.relevant

    def streaming_service(self) -> str:
        return next(
            (
                x.clear_name
                for x in (self.providers or [])
                if x.short_name == self.package_short_name
            )
        )

    @property
    def human_text(self) -> str:
        return (
            self.streaming_service() if self.streaming else f"Rent ${self.retail_price}"
        )


class Upcoming(BaseModel):
    package_id: int
    release_type: str
    release_window_days: int
    release_window_from: str
    release_window_to: str


class JustWatchSearchResult(BaseModel):
    title: str
    full_path: str
    full_paths: dict
    jw_entity_id: str
    object_type: str
    id: int
    original_release_year: int
    poster: Optional[str]
    poster_blur_hash: Optional[str]
    scoring: Optional[list[dict]]
    offers: Optional[list[Offer]]

    def equal_by_title(self, title: str) -> bool:
        return strip_all_punctuation(self.title.lower()) == strip_all_punctuation(
            title.lower()
        )


class Movie(BaseModel):
    title: str
    full_path: str
    full_paths: dict
    jw_entity_id: str
    object_type: str
    id: int
    original_release_year: int
    poster: str
    poster_blur_hash: str
    scoring: list[dict]
    offers: Optional[list[Offer]]
    backdrops: list[dict]
    short_description: str
    original_title: str
    localized_release_date: Optional[str]
    clips: list[dict]
    credits: list[dict]
    external_ids: list[dict]
    upcoming: Optional[list[Upcoming]]
    genre_ids: list[int]
    age_certification: Optional[str]
    runtime: int
    production_countries: list[str]
    promoted_bundles: Optional[list[dict]]
    permanent_audiences: Optional[list[str]]

    def __init__(self, relevant_providers: list[Provider], **kwargs):
        if kwargs.get("offers"):
            kwargs["offers"] = [
                Offer(**x, providers=relevant_providers) for x in kwargs["offers"]
            ]
        super().__init__(**kwargs)

    @property
    def just_watch_url(self) -> str:
        return f"https://justwatch.com{self.full_path}"

    def relevant_offers(self) -> list[Offer]:
        if not self.offers:
            return []

        return [offer for offer in self.offers if offer.for_me]

    def sorted_relevant_offers(self) -> list[Offer]:
        return sorted(
            self.relevant_offers(),
            key=lambda k: (reversor(k.watch_type), k.presentation_type, k.price),
        )

    @property
    def best_offer(self) -> Offer:
        return self.sorted_relevant_offers()[0]
