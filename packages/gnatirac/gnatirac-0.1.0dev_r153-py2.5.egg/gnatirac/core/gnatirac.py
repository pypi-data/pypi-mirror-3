# -*- encoding: UTF-8 -*-

#    Gnatirac is Picasa client for N900
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
Created on Oct 14, 2011

@author: maemo
'''
from exceptions import  *

import logging
import pickle
import os
import os.path

import gdata.photos.service
import gdata.media
import gdata.geo


from ..common import version 

version.getInstance().submitRevision("$Revision: 131 $")

def get_gnatirac_storage_dir():
    '''
    Compute the application storage dir.
    This is an utility function to retrieve the directory where gnatirac can
    store any file like settings or cached data.
    '''
    storage = os.path.expanduser("~")    
    storage = os.path.join(storage, ".gnatirac")
    return storage

class gnatirac(object):
    '''
    Main class of the Program. The GUI use this class like a Facade to any core functions.
    '''
    
    def __init__(self):
        self.connected = False
        self._ensure_gnatirac_conf_store()        
        self.settings = None        
        self.load_settings()        
        self.apply_settings()

    def get_gnatirac_settings_file(self):
        storage = get_gnatirac_storage_dir()
        storage = os.path.join(storage, "settings.pickle")
        return storage

    def load_settings(self):
        '''
        load the saved settings
        '''
        self._ensure_gnatirac_conf_store()
        storage = self.get_gnatirac_settings_file()
        try:           
            file = open(storage,'rb')
            self.settings = pickle.load(file)
            file.close()
        except IOError, EOFError:
            logging.warning("failed to load the settings")
            self.settings  = Settings()
            
    
    def save_settings(self):
        '''
        save the current settings
        '''
        self._ensure_gnatirac_conf_store()
        storage = self.get_gnatirac_settings_file()
        try:           
            file = open(storage,'wb')
            pickle.dump(self.settings,file)
            file.close()
        except IOError:
            logging.warning("failed to save the settings")

    
    def apply_settings(self):        
        if self.settings.autoconnect and self.settings.login and self.settings.password:
            self.connect()
        
       
        
        
    
    def _ensure_gnatirac_conf_store(self):
        storage = get_gnatirac_storage_dir()
        if os.path.exists(storage):
            pass
        else:
            os.makedirs(storage)

        

    
    
    '''
    Facade function
    '''
        
    
    def get_settings(self):
        return self.settings
    
    
    def set_google_account(self, login, password):    
        '''
        Open a new session to web album
        '''        
        self.settings.login = login
        self.settings.password = password
        

    def connect(self, captcha=None, response=None):
        '''
        Open a new session to web album
        '''                
        self.gd_client = gdata.photos.service.PhotosService()
        self.gd_client.email = self.settings.login
        self.gd_client.password = self.settings.password
        self.gd_client.source = 'bressure.net-gnatirac-v1'
        try : 
            self.gd_client.ProgrammaticLogin(captcha, response)    
            self.connected = True        
        except gdata.service.CaptchaRequired:
            raise GnatiracCaptchaException(self.gd_client._GetCaptchaToken(), self.gd_client._GetCaptchaURL(), self) 
                

    def get_gnatirac_storage_dir(self):
        '''
        Storage location of megen database
        '''
        return get_gnatirac_storage_dir()

    

    def iter_album_list(self, username="default"):
        '''
        Iterate on user album list and provide (yield) an Album object ready for use by the GUI
        '''
        logging.info("album listing...")
        albums = self.gd_client.GetUserFeed(user=username)
        for album in albums.entry:
            a = Album(album)
            logging.info('title: %s, number of photos: %s, id: %s' % (a.title,a.numphotos,a.id))           
            yield a 
           
    def iter_photos_list(self, album, username="default", start_index=1, max_results=10):
        logging.info("album photos listing...")
        photos = self.gd_client.GetFeed('/data/feed/api/user/%s/albumid/%s?kind=photo&start-index=%s&max-results=%s' % (username, album.id, start_index, max_results))
        for photo in photos.entry:
            p = Shot(photo)
            logging.info("title: %s url: %s" % (p.title, p.url))
            yield p 
           
    def iter_feed_list(self):
        logging.info("last feed listing...")
        photos = self.gd_client.GetUserFeed(kind='photo', limit='10')
        for photo in photos.entry:
            p = Shot(photo)
            logging.info("title: %s url: %s" % (p.title, p.url))
            yield p 

class Shot():
    
    def __init__(self, photo):
        self.title = photo.title.text
        self.url = photo.content.src
        self.thumbnail_url =  photo.media.thumbnail[2].url
        self.height = int(photo.height)
        self.width= int(photo.width)
        self.size = int(photo.size)

class Album():
    
    def __init__(self, album):
        '''
        Parameter
            - entry : the atom entry
        '''    
        self.title = album.title.text
        self.numphotos = int(album.numphotos.text)
        self.location = album.location.text
        self.access = album.access.text
        self.bytesUsed = int(album.bytesUsed.text)
        self.id =  album.gphoto_id.text
        self.thumbnail_url = None            
        if album.media.thumbnail and len(album.media.thumbnail) > 0:
            self.thumbnail_url =  album.media.thumbnail[0].url
        
class Settings():
    '''
    Represents the settings for Maegen
    '''
   
    def __init__(self):
        self.login = None
        self.password = None
        self.autoconnect = True

    
            