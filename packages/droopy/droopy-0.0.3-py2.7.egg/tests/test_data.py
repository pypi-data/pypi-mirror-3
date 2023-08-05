# -*- coding: utf-8 *-*

from droopy.lang.english import English
from droopy.lang.polish import Polish

TEXTS = [
    {
        'lang': English,
        'id': 'Simple',
        'text': u"""Just a simple test.""",
        'nof_characters': 15,
        'nof_words': 4,
        'nof_sentences': 1,
        'flesch_grade_level': 0.72,
        'automated_readability_index': -1.77,
        'smog': 3.13,
        'flesch_reading_ease': 97.03,
        'coleman_liau': -1.15,
    },

    {
        'lang': Polish,
        'id': 'Simple',
        'text': u"""Tylko prosty test.""",
        'nof_characters': 15,
        'nof_words': 3,
        'nof_sentences': 1,
        'flesch_grade_level': 5.25,
        'automated_readability_index': 3.62,
        'smog': 3.13,
        'flesch_reading_ease': 62.79,
        'coleman_liau': 3.73,
    }

]
