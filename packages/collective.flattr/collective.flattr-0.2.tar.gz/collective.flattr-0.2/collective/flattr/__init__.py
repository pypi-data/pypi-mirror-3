# -*- extra stuff goes here -*-
from zope.i18nmessageid import MessageFactory
flattrMessageFactory = MessageFactory('collective.flattr')

from collective.flattr.widget import FlattrThingWidget
FlattrThingWidget # pyflakes
