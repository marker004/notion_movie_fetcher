import pprint
import string


class reversor:
  def __init__(self, obj):
    self.obj = obj

  def __eq__(self, other):
    return other.obj == self.obj

  def __lt__(self, other):
    return other.obj < self.obj

pp = pprint.PrettyPrinter().pprint

def convert_runtime(runtime: int) -> str:
  return f'{int(runtime / 60)}:{(runtime % 60):02d}'

def strip_all_punctuation(subject: str) -> str:
  # add "smart quotes" that Notion uses
  punctuation = string.punctuation + '“‘”’'
  return subject.translate(str.maketrans('', '', punctuation))