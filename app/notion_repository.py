import asyncio
from typing import Any, Optional, cast
from shared_items.utils import measure_execution
from shared_items.interfaces.notion import Notion, collect_paginated_api
from assemblers.letterboxd_movie_assembler import NotionMovieItem
from shared import MOVIE_DATABASE_ID

notion = Notion()


def recursively_fetch_existing_notion_movies(
    filter: Optional[dict] = None,
) -> list[dict]:
    kwargs: dict[str, Any] = {"database_id": MOVIE_DATABASE_ID}
    if filter:
        kwargs["filter"] = filter
    return collect_paginated_api(notion.client.databases.query, **kwargs)


class NotionRepo:
    def __init__(self, fresh_movie_items: list[NotionMovieItem]):
        self.fresh_movie_items = fresh_movie_items

    def update_them_shits(self) -> None:
        all_existing_movies = self.fetch_existing_movies()
        existing_schedule_items = self.assemble_existing_movie_items(
            all_existing_movies
        )

        delete_list, do_nothing_list, add_list = self.group_schedule_items(
            existing_schedule_items, self.fresh_movie_items
        )
        self.operate_in_notion(delete_list, do_nothing_list, add_list)

    @measure_execution(f"fetching existing movies")
    def fetch_existing_movies(self):
        return recursively_fetch_existing_notion_movies()

    def assemble_existing_movie_items(self, notion_rows: list[dict]):
        return [
            NotionMovieItem.from_notion_interface(notion_item)
            for notion_item in notion_rows
        ]

    def assemble_insertion_notion_props(self, insertion_list: list[NotionMovieItem]):
        return [
            notion.assemble_props(item.format_for_notion_interface())
            for item in insertion_list
        ]

    def group_schedule_items(
        self,
        existing_items: list[NotionMovieItem],
        fresh_items: list[NotionMovieItem],
    ) -> tuple[list[NotionMovieItem], list[NotionMovieItem], list[NotionMovieItem]]:
        delete_list = list(set(existing_items) - set(fresh_items))
        do_nothing_list = list(set(fresh_items) & set(existing_items))
        add_list = list(set(fresh_items) - set(existing_items))

        return (delete_list, do_nothing_list, add_list)

    @measure_execution("deleting existing movies")
    def delete_unuseful_movies(self, delete_list: list[NotionMovieItem]):
        asyncio.run(
            notion.async_delete_all_blocks(
                [cast(str, item.notion_id) for item in delete_list]
            )
        )
        print(f"deleted {len(delete_list)} movies")

    @measure_execution("inserting fresh movies")
    def insert_new_movies(self, insert_list: list[NotionMovieItem]):
        print([(item.title, item.location) for item in insert_list if item.location])
        insert_list_props = self.assemble_insertion_notion_props(insert_list)
        asyncio.run(notion.async_add_all_pages(MOVIE_DATABASE_ID, insert_list_props))
        print(f"inserted {len(insert_list)} movies")

    def operate_in_notion(
        self,
        delete_list: list[NotionMovieItem],
        do_nothing_list: list[NotionMovieItem],
        add_list: list[NotionMovieItem],
    ):
        self.delete_unuseful_movies(delete_list)
        print(f"keeping {len(do_nothing_list)} movies\n")
        self.insert_new_movies(add_list)
