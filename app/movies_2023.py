import string
from typing import Any, Literal, Optional, Union
from typing_extensions import TypedDict, NotRequired
from justwatch import JustWatch
from interfaces import Notion, Prop as NotionProp
from interfaces.notion import MOVIES_DATABASE_ID
from models import Movie, Provider, Offer
from utils import reversor, pp, convert_runtime, strip_all_punctuation

"""
TODOs:
clean all this shit up
have it pull the original list from Notion, and sync it with the JustWatch ids,
  maybe come up with a UI to confirm found movies are correct,
  save ids in a database
utilize Upcoming for timed updates
"""

just_watch = JustWatch(country='US')

relevant_streaming_ids: list[dict] = [
  {'clear_name': 'Netflix', 'short_name': 'nfx'},
  {'clear_name': 'Amazon Prime Video', 'short_name': 'amp'},
  {'clear_name': 'Disney Plus', 'short_name': 'dnp'},
  {'clear_name': 'Apple TV Plus', 'short_name': 'atp'},
  {'clear_name': 'Apple iTunes', 'short_name': 'itu'},
  {'clear_name': 'Hulu', 'short_name': 'hlu'},
  {'clear_name': 'HBO Max', 'short_name': 'hbm'},
  {'clear_name': 'HBO Max Free', 'short_name': 'hmf'},
  {'clear_name': 'Peacock', 'short_name': 'pct'},
  {'clear_name': 'Peacock Premium', 'short_name': 'pcp'},
  {'clear_name': 'Amazon Video', 'short_name': 'amz'},
  {'clear_name': 'Google Play Movies', 'short_name': 'ply'},
  {'clear_name': 'YouTube', 'short_name': 'yot'},
  {'clear_name': 'Paramount Plus', 'short_name': 'pmp'},
  {'clear_name': 'The Roku Channel', 'short_name': 'rkc'},
  {'clear_name': 'YouTube Free', 'short_name': 'yfr'},
  {'clear_name': 'Hoopla', 'short_name': 'hop'},
  {'clear_name': 'Vudu', 'short_name': 'vdu'},
  {'clear_name': 'VUDU Free', 'short_name': 'vuf'},
  {'clear_name': 'PBS', 'short_name': 'pbs'},
  {'clear_name': 'Shudder', 'short_name': 'shd'},
  {'clear_name': 'Pluto TV', 'short_name': 'ptv'},
  {'clear_name': 'Plex', 'short_name': 'plx'},
  {'clear_name': 'Tubi TV', 'short_name': 'tbv'},
  {'clear_name': 'Kanopy', 'short_name': 'knp'},
]

class TitleWithId(TypedDict):
  title: str
  id: int

titles_with_ids: list[TitleWithId] = [
  {'title': 'Inu-oh', 'id': 898609},
  {'title': 'Puss in Boots: The Last Wish', 'id': 558},
  {'title': 'Turning Red', 'id': 375923},
  {'title': "Guillermo del Toro's Pinocchio", 'id': 438816},
  {'title': 'Marcel the Shell with Shoes On', 'id': 1101086},
  {'title': 'Decision to Leave', 'id': 1199158},
  {'title': 'Close', 'id': 1196181},
  {'title': 'Argentina, 1985', 'id': 1099911},
  {'title': 'Women Talking', 'id': 1221595},
  {'title': 'All Quiet on the Western Front', 'id': 57755},
  {'title': 'RRR', 'id': 463762},
  {'title': 'She Said', 'id': 1083213},
  {'title': 'Black Panther: Wakanda Forever', 'id': 465131},
  {'title': 'The Good Nurse', 'id': 1184116},
  {'title': 'Good Luck to You, Leo Grande', 'id': 1148164},
  {'title': 'Mrs. Harris Goes to Paris', 'id': 1113459},
  {'title': 'The Menu', 'id': 1198110},
  {'title': 'White Noise', 'id': 1063878},
  {'title': 'Blonde', 'id': 123367},
  {'title': 'The Woman King', 'id': 1125504},
  {'title': 'Empire of Light', 'id': 1032901},
  {'title': 'Living', 'id': 1138039},
  {'title': 'The Inspection', 'id': 1241645},
  {'title': 'The Son', 'id': 1238714},
  {'title': 'The Whale', 'id': 1241748},
  {'title': 'Triangle of Sadness', 'id': 950279},
  {'title': 'Glass Onion: A Knives Out Mystery', 'id': 915749},
  {'title': 'Everything Everywhere All at Once', 'id': 1137671},
  {'title': 'The Banshees of Inisherin', 'id': 1177080},
  {'title': 'Babylon', 'id': 1253698},
  {'title': 'Top Gun: Maverick', 'id': 316242},
  {'title': 'TÁR', 'id': 1131320},
  {'title': 'The Fabelmans', 'id': 1067559},
  {'title': 'Avatar: The Way of Water', 'id': 1904},
  {'title': 'Elvis', 'id': 823717}
]

provider_results: list[dict] = just_watch.get_providers()

relevant_streaming_ids_short_names: list[str] = [x['short_name'] for x in relevant_streaming_ids]

relevant_provider_results: list[dict] = [x for x in provider_results if x['short_name'] in relevant_streaming_ids_short_names]

relevant_providers: list[Provider] = list(map(lambda x: Provider.parse_obj(x), relevant_provider_results))

def generate_nice_offers(titles_with_ids: list[TitleWithId]) -> dict[str, Any]:
  offers_object: dict[str, ViewingOption] = {}

  for title in titles_with_ids:
    movie_result = just_watch.get_title(title_id=title['id'])

    movie = Movie(**movie_result, providers=relevant_providers)

    if movie.offers:
      relevant_offers = []
      for offer in movie.offers:
        if offer.relevant and offer.watchable and (offer.streaming or offer.rental):
          nice_offer = viewing_option(offer, movie)
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

class ViewingOption(TypedDict):
  service: NotRequired[str]
  quality: NotRequired[str]
  runtime: str
  type: NotRequired[Literal["streaming", "rental"]]
  price: NotRequired[Union[str, None]]
  human_text: str


def viewing_option(offer: Offer, movie: Movie) -> ViewingOption:
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

nice_offers = generate_nice_offers(titles_with_ids)

notion = Notion()

database_info = notion.client.databases.query(database_id=MOVIES_DATABASE_ID)

database_rows = database_info['results']

punctuation = string.punctuation + '’'

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
