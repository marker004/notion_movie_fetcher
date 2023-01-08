from pydantic import BaseModel
from typing import Any, Optional, TypedDict


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


class Offer(BaseModel):
  country: str
  currency: str
  jw_entity_id: str
  monetization_type: str
  package_short_name: str
  presentation_type: str
  provider_id: int
  urls: dict
  retail_price: Optional[float]
  providers: list[Provider]

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

  @property
  def streaming(self):
    return self.monetization_type == 'flatrate'

  @property
  def rental(self):
    return self.monetization_type == 'rent'

  @property
  def hd(self):
    return self.presentation_type == 'hd'

  @property
  def four_k(self):
    return self.presentation_type == '4k'

  @property
  def watchable(self):
    return self.four_k or self.hd

  @property
  def relevant(self):
    return self.package_short_name in [provider.short_name for provider in self.providers]

  @property
  def for_me(self):
    return self.streaming or self.rental and self.watchable and self.relevant


class Upcoming(BaseModel):
  package_id: int
  release_type: str
  release_window_days: int
  release_window_from: str
  release_window_to: str


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
  localized_release_date: str
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

  def __init__(self, providers: list[Provider], **kwargs):
    if kwargs.get('offers'):
      kwargs['offers'] = [Offer(**x, providers=providers) for x in kwargs['offers']]
    super().__init__(**kwargs)
