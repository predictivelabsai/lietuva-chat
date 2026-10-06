"""Home suggestions: popular curated questions first, random fill, never free text."""

import random

from utils.popular import pool, suggestions


def test_random_fill_without_data():
    picked = suggestions('en', k=3, counts=lambda qs: [], rng=random.Random(1))
    assert len(picked) == 3 and len(set(picked)) == 3
    assert all(q in pool('en') for q in picked)


def test_popular_first_then_fill():
    top = pool('en')[4]
    picked = suggestions('en', k=3, counts=lambda qs: [(top.lower(), 9)], rng=random.Random(2))
    assert picked[0] == top and len(set(picked)) == 3


def test_free_text_is_never_shown():
    picked = suggestions('en', k=3, counts=lambda qs: [('my asmens kodas is 38001010000', 50)], rng=random.Random(3))
    assert all(q in pool('en') for q in picked)


def test_counting_failure_falls_back():
    def broken(qs):
        raise RuntimeError('db down')
    assert len(suggestions('lt', k=3, counts=broken)) == 3
