# -*- coding: utf-8 *-*

import unittest
import logging

from test_data import TEXTS

from droopy.factory import DroopyFactory

class TestAll(unittest.TestCase):
    """All processors test merged into one test. See module test_data"""

    def test_run(self):
        for test_text in TEXTS:
            # base attributes (any other will be treated as processors)
            lang_class = test_text.pop('lang')
            id = test_text.pop('id')
            text = test_text.pop('text')

            # create droopy
            droopy = DroopyFactory.create_full_droopy(text, lang_class())

            # check processors values
            for proc in test_text:
                expected = round(test_text[proc], 2) # round value
                got = round(getattr(droopy, proc), 2) # round value

                # raise error if values are not equal (accurate to two decimal
                # places
                if not expected == got:
                    self.fail("Inccorect value in text %s for processor %s (%s). Expected %s, got %s" % (id, proc, droopy.lang, expected, got))

