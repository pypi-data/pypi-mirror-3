from zope.interface import Interface
# -*- Additional Imports Here -*-
from zope import schema

from getpaid.pfgbuyableadapter import pfgbuyableadapterMessageFactory as _


class IBuyableFormAdapter(Interface):
    """An adapter for PloneFormGen to allow forms to be purchased."""

    # -*- schema definition goes here -*-
    price = schema.Float(
        title=_(u"Price"),
        required=True,
        description=_(u"How much does this form cost"),
    )
#

