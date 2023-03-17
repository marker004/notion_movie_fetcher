from typing import Optional
from shared_items.utils import measure_execution
from shared_items.interfaces import Notion
from assemblers.letterboxd_movie_assembler import NotionMovieItem
from shared import MOVIE_DATABASE_ID, insert_to_database

notion = Notion()


def fetch_all_existing_movies() -> list[dict]:
    movie_fetcher = fetch_movies()

    all_movies: list[dict] = []
    next_cursor: Optional[str] = None

    while True:
        response = movie_fetcher(next_cursor)
        next_cursor = response["next_cursor"]
        all_movies += response["results"]
        if not response["has_more"]:
            break

    return all_movies


def fetch_movies():
    def func(start_cursor: Optional[str] = None):
        return notion.client.databases.query(
            database_id=MOVIE_DATABASE_ID, start_cursor=start_cursor
        )

    return func


class NotionRepo:
    def __init__( self, fresh_movie_items: list[NotionMovieItem] ):
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
        return fetch_all_existing_movies()

    def assemble_existing_movie_items(self, notion_rows: list[dict]):
        return [
            NotionMovieItem.from_notion_interface(notion_item)
            for notion_item in notion_rows
        ]

    def assemble_insertion_notion_props(
        self, insertion_list: list[NotionMovieItem]
    ):
        return [
            notion.assemble_props(item.format_for_notion_interface())
            for item in insertion_list
        ]

    def group_schedule_items(
        self,
        existing_items: list[NotionMovieItem],
        fresh_items: list[NotionMovieItem],
    ) -> tuple[
        list[NotionMovieItem],
        list[NotionMovieItem],
        list[NotionMovieItem],
    ]:
        delete_list = list(set(existing_items) - set(fresh_items))
        do_nothing_list = list(set(fresh_items) & set(existing_items))
        add_list = list(set(fresh_items) - set(existing_items))

        return (delete_list, do_nothing_list, add_list)

    @measure_execution("deleting existing movies")
    def delete_unuseful_movies(self, delete_list: list[NotionMovieItem]):
        total = len(delete_list)
        for idx, item in enumerate(delete_list):
            if item.notion_id:  # should always be true
                notion.client.blocks.delete(block_id=item.notion_id)
                print(idx / total, end="\r", flush=True)
        print(f"deleted {len(delete_list)} movies")

    @measure_execution("inserting fresh movies")
    def insert_new_movies(self, insert_list: list[NotionMovieItem]):
        insert_list_props = self.assemble_insertion_notion_props(insert_list)
        insert_to_database(insert_list_props)
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
