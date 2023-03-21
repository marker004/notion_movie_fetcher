from typing import Optional, TypedDict, cast
from requests import get as sync_get
from bs4 import BeautifulSoup, Tag
import asyncio

import json
from assemblers.letterboxd_movie_assembler import Assembler as LetterBoxdMovieAssembler

from models.letterboxd import (
    LetterboxdJustwatchResult,
    LetterboxdMovie,
    LetterboxdResponseCollection,
    WatchOption,
)

from shared_items.interfaces import Notion
from shared_items.utils import pp, measure_execution
from notion_repository import NotionRepo
from utils import async_aiohttp_get_all_json, async_aiohttp_get_all_text

notion = Notion()


with open("app/letterboxd.com_cookies.json", "r") as f:
    cookies_list = json.load(f)

cookies = {item["name"]: item["value"] for item in cookies_list}

LETTERBOXD_MOVIE_DATA_ATTRS = [
    "data-film-id",
    "data-film-name",
    "data-film-release-year",
    "data-film-link",
]

LETTERBOXD_LIST_URL = "https://letterboxd.com/markreckard/watchlist"


def find_movies_from_letterboxd_list_page(soup: BeautifulSoup) -> list[dict]:
    items = soup.find_all("div", {"class": "really-lazy-load"})

    keys = [
        {
            "buster": item.attrs["data-cache-busting-key"],
            "slug": item.attrs["data-film-slug"],
        }
        for item in items
    ]

    lbxd_urls = [
        f"https://letterboxd.com/ajax/poster{item.attrs['data-film-slug']}std/125x187/?k={item.attrs['data-cache-busting-key']}"
        for item in items
    ]

    results = asyncio.run(async_aiohttp_get_all_text(lbxd_urls))

    all_relevant_attrs: list[dict] = []

    for comp in results:
        souper = BeautifulSoup(comp, "html.parser")
        poster = souper.find("div", {"class": "poster"})
        if isinstance(poster, Tag):
            all_relevant_attrs.append(
                dict((k, poster.attrs[k]) for k in LETTERBOXD_MOVIE_DATA_ATTRS)
            )

    return all_relevant_attrs


@measure_execution("fetching movies from letterboxd")
def fetch_all_movies_from_letterboxd() -> list[dict]:
    every_relevant_attrs: list[dict] = []
    url: str = LETTERBOXD_LIST_URL

    while True:
        resp = sync_get(url, cookies=cookies)

        soup = BeautifulSoup(resp.text, "html.parser")
        next_paginator: Tag = soup.find_all("div", {"class": "paginate-nextprev"})[1]
        more_link = next_paginator.find("a")

        every_relevant_attrs += find_movies_from_letterboxd_list_page(soup)

        if isinstance(more_link, Tag):
            href = more_link.attrs["href"]
            url = f"https://letterboxd.com{href}"
        else:
            break

    return every_relevant_attrs


class ExtraDatasDict(TypedDict):
    runtime: list[str]
    genres_list: list[list[str]]


@measure_execution("fetching extra_data from letterboxd/justwatch")
def fetch_film_data_from_letterboxd(movies: list[LetterboxdMovie]):
    all_film_page_urls = [
        f"https://letterboxd.com{movie.letterboxd_url}" for movie in movies
    ]

    results = asyncio.run(async_aiohttp_get_all_text(all_film_page_urls))

    extra_datas: ExtraDatasDict = {"runtime": [], "genres_list": []}

    for page in results:
        soup = BeautifulSoup(page, "html.parser")
        runtime_el = soup.find("p", {"class": "text-link"})
        if isinstance(runtime_el, Tag):
            runtime_strings = list(runtime_el.stripped_strings)
            runtime = runtime_strings[0].split("\xa0")[0]
            extra_datas["runtime"].append(runtime)
        genres_parent_el = soup.find("div", {"id": "tab-genres"})
        if isinstance(genres_parent_el, Tag):
            genre_el = genres_parent_el.find("div")
            if isinstance(genre_el, Tag):
                genres_list = list(genre_el.stripped_strings)
                extra_datas["genres_list"].append(genres_list)

    return extra_datas


@measure_execution("fetching watchability from letterboxd/justwatch")
def fetch_jw_results_via_letterboxd(
    movies: list[LetterboxdMovie],
) -> list[Optional[WatchOption]]:
    all_availability_urls = [
        f"https://letterboxd.com/s/film-availability?filmId={movie.film_id}&locale=USA"
        for movie in movies
    ]
    results: list[dict] = asyncio.run(async_aiohttp_get_all_json(all_availability_urls))

    letterboxd_justwatch_results = [
        LetterboxdJustwatchResult(**result) for result in results
    ]

    return [result.best_option() for result in letterboxd_justwatch_results]


all_movies = fetch_all_movies_from_letterboxd()
letterboxd_collection = LetterboxdResponseCollection(movies=all_movies)
best_options = fetch_jw_results_via_letterboxd(letterboxd_collection.movies)
# x = list(zip(letterboxd_collection.movies, best_options))
# import pdb; pdb.set_trace()
# exit()
extra_data = fetch_film_data_from_letterboxd(letterboxd_collection.movies)


for idx, movie in enumerate(letterboxd_collection.movies):
    movie.justwatch_watch_option = best_options[idx]
    movie.runtime = extra_data["runtime"][idx]
    movie.genres = extra_data["genres_list"][idx]


def assemble_notion_items(movies: list[LetterboxdMovie]):
    return [LetterBoxdMovieAssembler(movie).notion_movie_item() for movie in movies]


assembled_items = assemble_notion_items(letterboxd_collection.movies)

NotionRepo(assembled_items).update_them_shits()
