from typing import Optional
from models.models import Movie
from pydantic.dataclasses import dataclass
from shared_items.interfaces import Prop as NotionProp
from shared_items.utils import pp, convert_runtime


@dataclass
class NotionMovieItem:
    runtime: str
    justwatch_id: int
    url: str
    year: int
    location: Optional[str]

    def format_for_notion_interface(self) -> list[NotionProp]:
        attrs: list[NotionProp] = [
            {
                "name": "Time",
                "type": "rich_text",
                "content": {
                    "content": self.runtime,
                },
            },
            {
                "name": "JustWatch ID",
                "type": "number",
                "content": {
                    "content": self.justwatch_id,
                },
            },
            {
                "name": "JustWatch URL",
                "type": "url",
                "content": {
                    "content": self.url,
                },
            },
            {
                "name": "Year",
                "type": "number",
                "content": {
                    "content": self.year,
                },
            },
        ]

        if self.location:
            attrs.append(
                {
                    "name": "Location",
                    "type": "rich_text",
                    "content": {"content": self.location},
                },
            )

        return attrs


class MovieAssembler:
    def __init__(self, movie: Movie) -> None:
        self.movie = movie

    def format_runtime(self) -> str:
        return convert_runtime(self.movie.runtime)

    def format_justwatch_id(self) -> int:
        return self.movie.id

    def format_url(self) -> str:
        return self.movie.just_watch_url

    def format_year(self) -> int:
        return self.movie.original_release_year

    def format_location(self) -> Optional[str]:
        return (
            self.movie.best_offer.human_text if self.movie.relevant_offers() else None
        )

    def notion_movie_item(self) -> NotionMovieItem:
        return NotionMovieItem(
            runtime=self.format_runtime(),
            justwatch_id=self.format_justwatch_id(),
            url=self.format_url(),
            year=self.format_year(),
            location=self.format_location(),
        )
