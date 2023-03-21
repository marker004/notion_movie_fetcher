from typing import Optional
from shared_items.interfaces import Notion
from shared_items.utils import pp, measure_execution
from assemblers.movie_assembler import MovieAssembler
from models import Movie
from fetchers import (
    fetch_relevant_providers,
    get_movies_from_just_watch,
    upsert_to_notion_database,
    search_just_watch,
    get_movie_titles_from_notion,
)
from models.models import JustWatchSearchResult

notion = Notion()

relevant_providers = fetch_relevant_providers()

existing_movie_titles_from_notion = get_movie_titles_from_notion()


@measure_execution("Fetching Just Watch Info")
def fetch_all_just_watch_info(
    ids_with_titles: dict[str, str]
) -> dict[str, Optional[JustWatchSearchResult]]:
    return {id: search_just_watch(title) for id, title in ids_with_titles.items()}


jw_search_results = fetch_all_just_watch_info(existing_movie_titles_from_notion)

just_watch_movies = get_movies_from_just_watch(jw_search_results)

ids_with_movies = {
    id: Movie(relevant_providers, **jw_movie)
    for id, jw_movie in just_watch_movies.items()
}

assembled_items = {
    id: MovieAssembler(movie).notion_movie_item()
    for id, movie in ids_with_movies.items()
}

all_props = {
    id: notion.assemble_props(movie_item.format_for_notion_interface())
    for id, movie_item in assembled_items.items()
}

upsert_to_notion_database(all_props)

"""
TODOs:
utilize Upcoming for timed updates?
"""
