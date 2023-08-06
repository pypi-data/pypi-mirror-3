#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2008
"""
import decimal
try:
    import fractions
except ImportError:
    fractions = None
from cocktail.translations import translations
from cocktail.schema.member import Member
from cocktail.schema.rangedmember import RangedMember


class Number(Member, RangedMember):
    """Base class for all members that handle numeric values."""

    def __init__(self, *args, **kwargs):
        Member.__init__(self, *args, **kwargs)
        RangedMember.__init__(self)        


class Integer(Number):
    """A numeric field limited integer values."""
    type = int


class Float(Number):
    """A numeric field limited to float values."""
    type = float


class Decimal(Number):
    """A numeric field limited to decimal values."""
    type = decimal.Decimal

    def translate_value(self, value, language = None, **kwargs):
        if value is None:
            return u""
        else:
            return translations(value, language, **kwargs)


if fractions:
    class Fraction(Number):
        """A numeric field limited to fractional values."""
        type = fractions.Fraction


