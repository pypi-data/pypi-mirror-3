# -*- encoding: UTF-8 -*-

#    Gnatirac is Picasa client for N900.
#
#    Copyright (C) 2011  Thierry Bressure
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
'''
Created on Dec 29, 2011

@author: maemo
'''

import gtk
import hildon
import urllib
import logging

from  gnatirac.gui.gtk.utils import LOGO_PIXBUF

class AlbumThumbnail(gtk.VBox):
    
    def __init__(self, album):
         gtk.VBox.__init__(self)
         
         miniature = None        
         if album.thumbnail_url:
            logging.debug("retrieving thumbnail %s" % album.thumbnail_url)
            miniature = gtk.gdk.pixbuf_new_from_file(urllib.urlretrieve(album.thumbnail_url)[0])
         else:
            miniature = LOGO_PIXBUF   
         image = gtk.Image()
         image.set_from_pixbuf(miniature)                             
         self.pack_start(image, False, False,0)
         self.button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT| gtk.HILDON_SIZE_HALFSCREEN_WIDTH, hildon.BUTTON_ARRANGEMENT_VERTICAL)
         self.button.set_title(album.title)
         self.button.set_value(str(album.numphotos))
         self.pack_start(self.button, False, False,0)

    def connect_action(self, *argv, **kwarg):
         self.button.connect("clicked", *argv, **kwarg)
         
         
class ShotThumbnail(gtk.VBox):
    
    def __init__(self, shot, prev=None, next=None):
         gtk.VBox.__init__(self)
         self.prev = prev
         self.next = next
         self.shot = shot
         miniature = None        
         if shot.thumbnail_url:
            logging.debug("retrieving thumbnail %s" % shot.thumbnail_url)
            miniature = gtk.gdk.pixbuf_new_from_file(urllib.urlretrieve(shot.thumbnail_url)[0])
         else:
            miniature = LOGO_PIXBUF   
         image = gtk.Image()
         image.set_from_pixbuf(miniature)                             
         self.pack_start(image, False, False,0)
         self.button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT| gtk.HILDON_SIZE_HALFSCREEN_WIDTH, hildon.BUTTON_ARRANGEMENT_VERTICAL)
         self.button.set_title(shot.title)
         self.pack_start(self.button, False, False,0)         


    def connect_action(self, *argv, **kwarg):
         self.button.connect("clicked", *argv, **kwarg)