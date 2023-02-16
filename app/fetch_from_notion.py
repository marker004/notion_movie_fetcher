from justwatch import JustWatch
from shared_items.utils import pp, strip_all_punctuation
from shared_items.interfaces import Notion, Prop as NotionProp
from shared_items.interfaces.notion import MOVIES_DATABASE_ID

just_watch = JustWatch(country="US")

notion = Notion()

movies_to_search = [
    "To Leslie",
    "Aftersun",
    "Causeway",
    "Bardo, False Chronicle of a Handful of Truths",
    "EO",
    "The Quiet Girl",
    "The Sea Beast",
    "All That Breathes",
    "All The Beauty and The Bloodshed",
    "Fire of Love",
    "A House Made of Splinters",
    "Navalny",
]


def get_movies_from_notion() -> list:
    database_info = notion.client.databases.query(database_id=MOVIES_DATABASE_ID)

    database_rows = database_info["results"]

    all_titles = [
        row["properties"]["Title"]["title"][0]["plain_text"] for row in database_rows
    ]

    titles_list = []

    for movie in all_titles:
        raw_results = just_watch.search_for_item(query=movie, release_year_from=2022)
        result = next(
            (
                result
                for result in raw_results["items"]
                if strip_all_punctuation(result["title"].lower())
                == strip_all_punctuation(movie.lower())
            ),
            None,
        )

        if result:
            titles_list.append({"title": result["title"], "id": result["id"]})

    return titles_list


def get_ids():
    for movie in movies_to_search:
        raw_results = just_watch.search_for_item(query=movie, release_year_from=2022)
        result = next(
            (
                result
                for result in raw_results["items"]
                if result["title"].lower() == movie.lower()
            ),
            None,
        )
        pp(result)
