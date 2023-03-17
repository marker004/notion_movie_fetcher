from shared_items.interfaces import Notion
from shared_items.utils import pp, measure_execution

notion = Notion()


MOVIE_DATABASE_ID = '33378c56ba7249b5ac88bf5f4753e7a2'

@measure_execution("inserting to notion database")
def insert_to_database(all_props: list[dict]):
    total: int = len(all_props)
    row_creator = notion.create_row_for_database(MOVIE_DATABASE_ID)
    for idx, props in enumerate(all_props):
        row_creator(props)
        print(idx / total, end="\r", flush=True)