from typing import Optional, TypedDict
from justwatch import JustWatch
from pydantic import BaseModel
from shared_items.utils import pp, strip_all_punctuation, measure_execution
from shared_items.interfaces import Notion, Prop as NotionProp
from shared_items.interfaces.notion import MOVIES_DATABASE_ID

from models.models import JustWatchSearchResult, Movie, Provider, ProviderCollection

just_watch = JustWatch(country="US")

notion = Notion()


class PartialJustWatchResponse(TypedDict):
    items: list[dict]


@measure_execution("Getting Movies from Notion")
def get_movie_titles_from_notion() -> dict[str, str]:
    database_info = notion.client.databases.query(database_id=MOVIES_DATABASE_ID)

    return {
        row["id"]: row["properties"]["Title"]["title"][0]["plain_text"]
        for row in database_info["results"]
    }


def search_just_watch(movie_title: str, release_year=2022) -> Optional[JustWatchSearchResult]:
    jw_raw_results: PartialJustWatchResponse = just_watch.search_for_item(
        query=movie_title, release_year_from=release_year, release_year_until=release_year+1
    )

    search_results = list(
        map(lambda x: JustWatchSearchResult(**x), jw_raw_results["items"])
    )

    return next(
        (result for result in search_results if result.equal_by_title(movie_title)),
        None,
    )


@measure_execution("Fetching relevant providers")
def fetch_relevant_providers() -> list[Provider]:
    provider_results: list[dict] = just_watch.get_providers()
    provider_collection = ProviderCollection(providers=provider_results)
    return provider_collection.relevant_providers()


@measure_execution("Getting movies from JustWatch")
def get_movies_from_just_watch(
    jw_search_results: dict[str, JustWatchSearchResult]
) -> dict[str, Movie]:
    return {
        id: just_watch.get_title(title_id=jw_search_result.id)
        for id, jw_search_result in jw_search_results.items()
    }


@measure_execution("Inserting into database...")
def upsert_to_notion_database(all_props: dict[str, dict]) -> None:
    total: int = len(all_props)
    for idx, (id, props) in enumerate(all_props.items()):
        notion.update_page_props(page_id=id, props=props)
        print(idx / total, end="\r", flush=True)
