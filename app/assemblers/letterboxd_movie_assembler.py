from typing import Optional
from models.letterboxd import LetterboxdMovie
from pydantic.dataclasses import dataclass
from shared_items.interfaces import Prop as NotionProp
from shared_items.utils import convert_runtime

@dataclass
class NotionMovieItem:
    title: str
    runtime: str
    location: str
    year: int
    letterboxd_id: str
    letterboxd_link: str
    notion_id: Optional[str] = None

    def format_for_notion_interface(self) -> list[NotionProp]:
        return [
            {
                "name": "Title",
                "type": "title",
                "content": {
                    "content": self.title,
                },
            },
            {
                "name": "Year",
                "type": "number",
                "content": {
                    "content": self.year,
                },
            },
            {
                "name": "Runtime",
                "type": "rich_text",
                "content": {
                    "content": self.runtime,
                },
            },
            {
                "name": "Location",
                "type": "rich_text",
                "content": {
                    "content": self.location,
                },
            },
            {
                "name": "Letterboxd ID",
                "type": "rich_text",
                "content": {
                    "content": self.letterboxd_id,
                },
            },
            {
                "name": "Letterboxd Link",
                "type": "url",
                "content": {
                    "content": self.letterboxd_link,
                },
            }
        ]

class Assembler:
    def __init__(self, movie: LetterboxdMovie) -> None:
        self.movie = movie

    def format_title(self) -> str:
        return self.movie.title

    def format_runtime(self) -> str:
        return convert_runtime(int(self.movie.runtime)) if self.movie.runtime else ''

    def format_location(self) -> str:
        return self.movie.formatted_location()

    def format_year(self) -> int:
        return self.movie.release_year

    def format_letterboxd_id(self) -> str:
        return self.movie.film_id

    def format_letterboxd_link(self) -> str:
        return f"https://letterboxd.com{self.movie.letterboxd_url}"

    def notion_movie_item(self) -> NotionMovieItem:
        return NotionMovieItem(
            title=self.format_title(),
            runtime=self.format_runtime(),
            location=self.format_location(),
            year=self.format_year(),
            letterboxd_id=self.format_letterboxd_id(),
            letterboxd_link=self.format_letterboxd_link(),
        )
