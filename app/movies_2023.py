import json
import os
from typing import Any, Literal, Union
from typing_extensions import TypedDict, NotRequired
from justwatch import JustWatch
from interfaces import Notion, Prop as NotionProp
from interfaces.notion import MOVIES_DATABASE_ID
from models import Movie, Provider, Offer
from utils import reversor, pp, convert_runtime, strip_all_punctuation

class TitleWithId(TypedDict):
  title: str
  id: int

class ViewingOption(TypedDict):
  service: NotRequired[str]
  quality: NotRequired[str]
  runtime: str
  type: NotRequired[Literal["streaming", "rental"]]
  price: NotRequired[Union[str, None]]
  human_text: str

root = os.path.dirname(os.path.dirname(__file__))
data_dir = os.path.join(root, 'data')

with open(os.path.join(data_dir, 'relevant_streaming_services.json'), 'r') as f:
  relevant_streaming_ids: list[dict] = json.load(f)

with open(os.path.join(data_dir, 'movies_2023.json'), 'r') as f:
  titles_with_ids: list[TitleWithId] = json.load(f)

"""
TODOs:
clean all this shit up
have it pull the original list from Notion, and sync it with the JustWatch ids,
  maybe come up with a UI to confirm found movies are correct,
  save ids in a database
utilize Upcoming for timed updates
Bring in movies from Letterboxd
"""

just_watch = JustWatch(country='US')
notion = Notion()

def convert_relevant_providers(relevant_streaming_ids: list[dict]) -> list[Provider]:
  provider_results: list[dict] = just_watch.get_providers()
  relevant_streaming_ids_short_names: list[str] = [x['short_name'] for x in relevant_streaming_ids]
  relevant_provider_results: list[dict] = [x for x in provider_results if x['short_name'] in relevant_streaming_ids_short_names]

  return list(map(lambda x: Provider.parse_obj(x), relevant_provider_results))

def viewing_option(offer: Offer, movie: Movie, relevant_providers: list[Provider]) -> ViewingOption:
  streaming_service = next((x.clear_name for x in relevant_providers if x.short_name == offer.package_short_name))

  response: ViewingOption = {
    'service': streaming_service,
    'quality': offer.presentation_type,
    'runtime': convert_runtime(movie.runtime),
    'type': ('streaming' if offer.streaming else 'rental'),
    'price': (None if offer.streaming else str(offer.retail_price)),
    'human_text': (streaming_service if offer.streaming else f'Rent ${offer.retail_price}'),
  }

  return response

def generate_nice_offers(titles_with_ids: list[TitleWithId], relevant_providers: list[Provider]) -> dict[str, Any]:
  offers_object: dict[str, ViewingOption] = {}

  for title in titles_with_ids:
    movie_result = just_watch.get_title(title_id=title['id'])

    movie = Movie(**movie_result, providers=relevant_providers)

    if movie.offers:
      relevant_offers = []
      for offer in movie.offers:
        if offer.relevant and offer.watchable and (offer.streaming or offer.rental):
          nice_offer = viewing_option(offer, movie, relevant_providers)
          relevant_offers.append(nice_offer)

      sorted_offers = sorted(relevant_offers, key=lambda k: (reversor(k['type']), k['quality'], k['price']))

      if relevant_offers:
        best_offer = sorted_offers[0]
        offers_object[movie.title] = best_offer
      else:
        offers_object[movie.title] = {'human_text': '', 'runtime': convert_runtime(movie.runtime)}
    else:
      offers_object[movie.title] = {'human_text': '', 'runtime': convert_runtime(movie.runtime)}

  return offers_object

relevant_providers = convert_relevant_providers(relevant_streaming_ids)

nice_offers = generate_nice_offers(titles_with_ids, relevant_providers)

database_info = notion.client.databases.query(database_id=MOVIES_DATABASE_ID)

database_rows = database_info['results']

for title, info in nice_offers.items():
  try:
    found_row = next(
      row
      for row
      in database_rows
      if strip_all_punctuation(row['properties']['Title']['title'][0]['text']['content']) ==
        strip_all_punctuation(title)
    )
    page_id = found_row['id']
    props: list[NotionProp] = [{
      'name': 'Location',
      'type': 'rich_text',
      'content': info['human_text']
    }]

    notion.update_page_props(page_id=page_id, props=props)
  except(StopIteration):
    print(title)
