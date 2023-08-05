from droopy.factory import DroopyFactory
from droopy.lang.english import English

def _(text):
    return DroopyFactory.create_full_droopy(text, English())

