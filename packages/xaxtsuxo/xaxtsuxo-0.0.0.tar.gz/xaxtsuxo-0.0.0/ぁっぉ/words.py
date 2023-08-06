#), encoding: utf-8
from random import choice, randint, sample

katsuo_words = {
    "interjections": [
        "ぉゃ",
        "ぉぉ",
        "ぁぁ",
        "ぉ。",
        "ぅぁぁぁぁ",
        "ぅゎ",
        "ゎぁぃ",
        "ぁぁ…",
        "ぉゃぉゃ",
        "ぇぇヵ?",
        ],
    "adverbs_for_sentence": [
        "ィッヵ",
        ],
    "adverbs_for_adjective": [
        "ゃゃ",
        ],
    "adjectival_nouns_without_terminal_particles": [
        "っʓฺっʓฺ",
        "ιゎιゎ",
        ],
    "adjectival_nouns": [
        "ゅぃぃっ",
        "ゅぅぅっ",
        "ぃゃ",
        "ョヶィ",
        ],
    "adjectives": [
        "ぃぃ",
        "ぁゃιぃ",
        "ぁっぃ",
        "ヵュぃ",
        "ぁぉぃ",
        "ヮヵィ",
        "ァヵィ",
        "ょゎぃ",
        "っょぃ",
        "ぇӡฺぃ",
        "ぁゃぅぃ",
        "ょゅぅ",
        "ヵョゎぃ",
        "ヶゎιぃ",
        ],
    "nouns": [
        "ゎぃ",
        "ぁぃっ",
        "ぉっゅ",
        "ぁっぉ",
        "ゥォッヵ",
        "ぃゎι",
        "ぉゃっ",
        "ぉゃιﾞ",
        "ょぅι゛ょ",
        "ゃっ",
        "ヶッ",
        "ヵィャ",
        "ォッヵィ",
        "ぃぇ",
        "ヵッォ",
        "ぉヵヵ",
        "ゥヶッヶ",
        "ェィヵィヮ",
        "ょっゃ",
        "ヮィヶィヶィ",
        "ョゥヵィ",
        "ぉヶッ",
        "ヵォ",
        "っぇ",
        "ぇぃゅぅ",
        "ヵιュヵ",
        ],
    "verbal_nouns": [
        "ぉぃゎぃ",
        "ヵィヶィ",
        "ヶィヵィ",
        "ゅぅヵぃ",
        ],
    "noun_particles": [
        "ゎ",
        ],
    "copula_terminal1": [
        "ゃ",
        "ょ",
        "ゃゎ",
        ],
    "copula_terminal2": [
        "ょ",
        "ゎょ",
        ],
    "verb_connective": [
        "ゃぃτ",
        ],
    "verb_terminal": [
        "ぃぅ",
        "ヵゥ",
        "ッヵェ！",
        "ぅっ",
        ],
    }

class gen:
    def __init__(self, type, max=1, min=1):
        self.type = type
        self.max = max
        self.min = min

    def __call__(self, ctx):
        return sample(ctx[self.type], randint(self.min, self.max))

def zero_or_one(type):
    return gen(type, 1, 0)

class branch:
    def __init__(self, *branches):
        self.branches = branches

    def __call__(self, ctx):
        return choice(self.branches)

def noun_with_adjective():
    return [ branch(
               [gen('adverbs_for_adjective'), zero_or_one('adjectives')],
               [zero_or_one('adjectives')]),
             gen('nouns') ]

markov_chains = [
    gen('interjections', 2, 0),
    zero_or_one('adverbs_for_sentence'),
    branch(
      [ branch([], noun_with_adjective() + [
                   zero_or_one('noun_particles'),
                   branch(
                     [gen('adjectives'), gen('copula_terminal2')],
                     [gen('adjectival_nouns'), gen('copula_terminal1')],
                     noun_with_adjective() + [gen('copula_terminal1')],
                     noun_with_adjective() + [gen('verb_terminal')],
                     [gen('verbal_nouns'), gen('copula_terminal1')]) ]) ]) ]
