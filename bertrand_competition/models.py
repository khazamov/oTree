# -*- coding: utf-8 -*-
from __future__ import division
"""Documentation at https://github.com/oTree-org/otree/wiki"""

from otree.db import models
import otree.models
from otree.common import money_range


doc = """
In the Bertrand competition game, players play firms and are asked to privately set the price of their product.
The firm with the lowest price gets all the business and received a profit. Firms who offer higher prices receive zero profit.
If multiple firms offer the same lowest price, business is divided equally amongst them.
Source code <a href="https://github.com/oTree-org/oTree/tree/master/bertrand_competition" target="_blank">here</a>.
"""


class Subsession(otree.models.BaseSubsession):

    name_in_url = 'bertrand_competition'

    marginal_cost = models.MoneyField(
        default=0.20,
        doc="""Marginal cost of production, effectively the minimum price (exclusive)"""
    )

    maximum_price = models.MoneyField(
        default=1.00,
        doc="""The maximum price"""
    )




class Match(otree.models.BaseMatch):

    # <built-in>
    subsession = models.ForeignKey(Subsession)
    # </built-in>

    players_per_match = 3

    num_winners = models.PositiveIntegerField(
        default=None,
        doc="""How many players offer lowest price"""
    )

    winning_price = models.MoneyField(
        default=None,
        doc="""Lowest price"""
    )

    def set_payoffs(self):
        self.winning_price = min([p.price for p in self.players])
        self.num_winners = len([p for p in self.players if p.price == self.winning_price])
        winner_payoff = (self.winning_price - self.subsession.marginal_cost) / self.num_winners

        for p in self.players:
            if p.price == self.winning_price:
                p.is_a_winner = True
                p.payoff = winner_payoff
            else:
                p.is_a_winner = False
                p.payoff = 0


class Player(otree.models.BasePlayer):

    # <built-in>
    match = models.ForeignKey(Match, null=True)
    subsession = models.ForeignKey(Subsession)
    # </built-in>

    price = models.MoneyField(
        default=None,
        doc="""Price player chooses to sell product for"""
    )

    def price_choices(self):
        return money_range(self.subsession.marginal_cost, self.subsession.maximum_price, 0.05)

    is_a_winner = models.BooleanField(
        default=False,
        doc="""Whether this player offered lowest price"""
    )

    def is_sole_winner(self):
        return self.is_a_winner and self.match.num_winners == 1

    def is_shared_winner(self):
        return self.is_a_winner and self.match.num_winners > 1


