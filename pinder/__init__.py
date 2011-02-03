"""
Pinder

Pinder is a client library for Campfire, the chat application from 37Signals.
"""
from pinder.campfire import Campfire, VERSION as __version__
from pinder.room import Room
from pinder.exc import HTTPUnauthorizedException, HTTPNotFoundException
from pinder.exc import RoomNotFoundException

__author__ = "Lawrence Oluyede <l.oluyede@gmail.com>"
__copyright__ = "Copyright (c) 2009-2010, Lawrence Oluyede"
__license__ = "BSD"
