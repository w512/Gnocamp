#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gnome Notification for Campfirenow (http://campfirenow.com)
"""
__author__ = 'Nikolay Blohin <nikolay@blohin.org>'
__copyright__ = 'Copyright (c) 2011, Nikolay Blohin'
__license__ = 'GNU General Public License'
__version__ = '0.3'


import os
import time
import pynotify
import hashlib
import urllib
import gtk
import gst
from pinder import Campfire




# ***************************************************************************
# ***  Important! Here you need to enter data or write it to settings.py  ***
# ***************************************************************************
SECRET_TOKEN = ''
SUBDOMAIN = ''
ROOM_ID = ''    # you can enter only ID or Name
ROOM_NAME = ''
SHOW_GRAVATAR = False
PLAY_SOUND = False
FREQUENCY = 0
DURATION = 0
# ***************************************************************************

# if you want to keep confidential data separately
try:
    from settings import *
except:
    pass



class MyNotify(object):
    def __init__(self):
        super(MyNotify, self).__init__()

        # connect to Campfire
        self.c = Campfire(SUBDOMAIN, SECRET_TOKEN, ssl=True)
        if ROOM_ID:
            self.room = self.c.room(ROOM_ID)
        else:
            self.room = self.c.find_room_by_name(ROOM_NAME)
        self.room.join()

        print 'Begin...'
        self.room.listen(self.callback_for_campfire, self.error_callback)
        print 'End...'


    def callback_for_campfire(self, mes):
        print '***** Simple callback *****'
        print mes
        print '****** End callback *****'

        if mes['type']=='TextMessage':
            user = self.c.user(mes['user_id'])['user']
            gravatar_hash = hashlib.md5(user['email_address'].lower()).hexdigest()
            title = user['name']
            body = mes['body']

        elif mes['type']=='TopicChangeMessage':
            user = self.c.user(mes['user_id'])['user']
            gravatar_hash = hashlib.md5(user['email_address'].lower()).hexdigest()
            title = 'Topic has been changed'
            body = '%s changed the room’s topic to "%s"' % (user['name'],
                                                            mes['body'])

        elif mes['type']=='LeaveMessage':
            user = self.c.user(mes['user_id'])['user']
            gravatar_hash = hashlib.md5(user['email_address'].lower()).hexdigest()
            title = 'Someone has left the room'
            body = '%s has left the room' % user['name']

        elif mes['type']=='EnterMessage':
            user = self.c.user(mes['user_id'])['user']
            gravatar_hash = hashlib.md5(user['email_address'].lower()).hexdigest()
            title = 'Someone has joined the room'
            body = '%s has entered the room' % user['name']

        elif mes['type']=='UploadMessage':
            user = self.c.user(mes['user_id'])['user']
            gravatar_hash = hashlib.md5(user['email_address'].lower()).hexdigest()
            title = 'New file uploaded'
            body = '%s uploaded %s' % (user['name'],
                                         mes['body'])

        else:
            return


        n = pynotify.Notification(title, body)

        if gravatar_hash and SHOW_GRAVATAR:
            source = urllib.urlopen('http://www.gravatar.com/avatar/' + gravatar_hash)
            contents = source.read()
            get_image = gtk.gdk.PixbufLoader()
            get_image.write(contents)
            get_image.close()
            n.set_icon_from_pixbuf(get_image.get_pixbuf())

        if PLAY_SOUND:
            pipeline = gst.Pipeline('mypipeline')
            audiotestsrc = gst.element_factory_make('audiotestsrc', 'audio')
            audiotestsrc.set_property('freq', FREQUENCY)
            pipeline.add(audiotestsrc)
            sink = gst.element_factory_make('alsasink', 'sink')
            pipeline.add(sink)
            audiotestsrc.link(sink)
            pipeline.set_state(gst.STATE_PLAYING)
            print '============== Sound =============='

        n.show()

        if PLAY_SOUND:
            time.sleep(DURATION)
            pipeline.set_state(gst.STATE_READY)

    def error_callback(self, expt):
        print '***** Error callback *****'
        print expt
        print '***** End callback *****'
        n = pynotify.Notification('Whoops!', 'An error occurred', 'dialog-error')
        n.show()



if __name__ == '__main__':
    MyNotify()

