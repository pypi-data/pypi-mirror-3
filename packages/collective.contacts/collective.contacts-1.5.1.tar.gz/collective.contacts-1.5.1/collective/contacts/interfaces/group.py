# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface

from collective.contacts.interfaces import IPerson
from collective.contacts import contactsMessageFactory as _

class IGroup(Interface):
    """Let you have several persons together"""

    # -*- schema definition goes here -*-
    persons = schema.Object(
        title=_(u"Persons"),
        required=False,
        description=_(u"The persons that belong to this group"),
        schema=IPerson, # specify the interface(s) of the addable types here
    )
