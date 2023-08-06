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
import gtk
import hildon
import logging
import os.path
import logging
import time
import datetime
import pango

import urllib



from gnatirac.gui.gtk.widget import  *
from gnatirac.gui.hildon.widget import *
from gnatirac.gui.gtk.utils import fill_widget_with_logo, LOGO_PIXBUF
from gnatirac.gui.hildon.utils import show_about_dialog, call_handled_method, not_yet_implemented, \
                                    GnatiracStackableWindow, ASYNC_EXCEPTION_HANDLER_INSTANCE, AsyncTask, \
                                    StopSignalException, show_banner_information, show_note_information
from gnatirac.core import gnatirac

from gnatirac.common import version

version.getInstance().submitRevision("$Revision: 153 $")

from gnatirac.gui.hildon.portrait import FremantleRotation


gtk.gdk.threads_init()


def show_album_list_view(facade):
        window = AlbumListView(facade)
        program = hildon.Program.get_instance() 
        program.add_window(window)
        window.show_all()


def show_feed_list_view(facade):
        window = LastPictureView(facade)
        program = hildon.Program.get_instance() 
        program.add_window(window)
        window.show_all()
      

class gnatiracGui(object):
    '''
    This is the GUI of gnatirac
    '''

    _last_folder = None

    def __init__(self):
        '''
        Create a new application GUI
        '''
        self.program = hildon.Program.get_instance()     
        self.facade = gnatirac.gnatirac()       
        ASYNC_EXCEPTION_HANDLER_INSTANCE.start_async_exception_handler()
        self.init_main_view()   




    def init_main_view(self):
        '''
        create a new window for the main view of the application
        '''
       
        # display a spashscreen
        window = SplashScreenView(self.facade)              
        self.program.add_window(window)
        window.connect("destroy", self.quit_application, None)
        # This call show the window and also add the window to the stack
        window.show_all()
        
        # autorotayion !!!
        FremantleRotation("Gnatirac",main_window=window)       

        # TODO do some stuff here       
        if self.facade.connected:
            # Show album list
            show_album_list_view(self.facade)
                             

    def quit_application(self, widget, data):
        ASYNC_EXCEPTION_HANDLER_INSTANCE.stop_async_exception_handler()
        gtk.main_quit()
        

        
      
        
    def run(self):
        # the splash screen  is displayed,now show the home screen in a fancy tansition               
        gtk.main()


      

    
class SplashScreenView(GnatiracStackableWindow):
    '''
    This is the first view of the application e.g. the main view.  
    '''

    def __init__(self, facade):
        self.facade = facade
        GnatiracStackableWindow.__init__(self)

    def init_center_view(self, centerview):
        fill_widget_with_logo(centerview)

    
    def _show_connect_dialog(self, widget, data):
        
            parent = hildon.WindowStack.get_default().peek()
            dialog = hildon.LoginDialog(parent)
            dialog.set_message("Gmail account required")            
            response = dialog.run()
            username = dialog.get_username()
            password = dialog.get_password()
            dialog.destroy()
            if response == gtk.RESPONSE_OK:
                self.facade.set_google_account(username, password)
                self.facade.save_settings()                
                show_banner_information("connecting to picasa web album")
                try:                
                    self.facade.connect()
                except:
                    show_banner_information("failed to log in")
                else:
                    show_banner_information("connected") 
                    # ok, so open album list view
                    show_album_list_view(self.facade)
            
        
    def show_connect_dialog(self, widget, data):
         call_handled_method(self._show_connect_dialog, widget, data)
                      
    def on_feed_menu_clicked(self, widget, data):
        call_handled_method(show_feed_list_view, self.facade)
    
    def on_albums_menu_clicked(self, widget, data):
        call_handled_method(show_album_list_view, self.facade)



    def init_menu(self, menu):
        connectMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        connectMenuBtn.set_label("Connect");
        connectMenuBtn.connect("clicked", self.show_connect_dialog, None)
        menu.append(connectMenuBtn)
        
        feedMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        feedMenuBtn.set_label("Feed");
        feedMenuBtn.connect("clicked", self.on_feed_menu_clicked, None)
        menu.append(feedMenuBtn)
        
        
        albumMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        albumMenuBtn.set_label("Albums");
        albumMenuBtn.connect("clicked", self.on_albums_menu_clicked, None)
        menu.append(albumMenuBtn)
                                                                                                                                                          

        
    


class PhotoView(GnatiracStackableWindow):
    '''
    This view show a photo
    '''
    
    def __init__(self, thumbnail, facade):
        self.facade = facade
        self.photo = thumbnail.shot
        self.prev = thumbnail.prev
        self.next = thumbnail.next
        self.current = thumbnail 
        GnatiracStackableWindow.__init__(self, self.photo.title)
        
        
    def init_center_view(self, centerview):
        async_thread = AsyncTask(self, self.raise_stop_flag, self.load_picture, centerview)
        async_thread.start()

    def reset_stop_flag(self):
        self.stop_request_flag = False

    def raise_stop_flag(self):
        self.stop_request_flag = True
    
    def handle_stop_flag(self):
        if self.stop_request_flag:
            self.reset_stop_flag()
            raise StopSignalException()        
        
        
    def on_previous_clicked(self, widget, data):
        self.next = self.current
        self.current = self.prev
        self.photo = self.current.shot
        self.prev = self.current.prev
        
        self._refresh_center_view()
        
    def _refresh_center_view(self):
        for child in self.centerview.get_children():
            self.centerview.remove(child)
        self.init_center_view(self.centerview)
       
    
    def _on_next_clicked(self, widget, data):
        self.prev = self.current
        self.current = self.next
        self.photo = self.current.shot
        self.next = self.current.next
        
        self._refresh_center_view()
    
        
    def load_picture(self, centerview, gtk_sync=True):
        if gtk_sync : gtk.gdk.threads_enter()
        pixbuf = gtk.gdk.pixbuf_new_from_file(urllib.urlretrieve(self.photo.url)[0])
        image = gtk.Image()
        image.set_from_pixbuf(pixbuf)  
        hbox = gtk.HBox()
        if self.prev:
            img = gtk.image_new_from_icon_name("general_back", gtk.ICON_SIZE_BUTTON)
            but =  hildon.Button(gtk.HILDON_SIZE_AUTO, hildon.BUTTON_ARRANGEMENT_VERTICAL)
            but.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0,0))
            but.set_image(img)
            but.connect("clicked",self.on_previous_clicked,None)
            hbox.add(but)
        hbox.add(image)
        self.set_title(self.photo.title)
        if self.next:
            img = gtk.image_new_from_icon_name("general_forward", gtk.ICON_SIZE_BUTTON)
            but =  hildon.Button(gtk.HILDON_SIZE_AUTO, hildon.BUTTON_ARRANGEMENT_VERTICAL)
            but.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0,0))
            but.set_image(img)
            but.connect("clicked",self._on_next_clicked, None)
            hbox.add(but)        
        centerview.add(hbox)
        centerview.show_all()  
        if gtk_sync: gtk.gdk.threads_leave()
                       
    def show_photo_details(self, widget, data):
        dialog = gtk.Dialog() 
        dialog.set_transient_for(self) 
        dialog.set_title("Photo details")
        table = gtk.Table(4,2,False)
        
        row = 0;        
        def add_row_information(name, value, row):            
            child = gtk.Label("%s :" % name)
            table.attach(self.justifyRight(child), 0,1,row,row+1)
            child = gtk.Label(value)
            table.attach(self.justifyLeft(child), 1,2,row,row+1)
            return row + 1
        row = add_row_information("Name", self.photo.title, row)        
        row = add_row_information("Size", str(self.photo.size), row)
        row = add_row_information("Dimension", "%i x %i" % (self.photo.width, self.photo.height), row)
        
        
        dialog.vbox.pack_start(table)
        dialog.show_all() 
        dialog.run()

    def init_menu(self, menu):
        detailMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        detailMenuBtn.set_label("Details");
        detailMenuBtn.connect("clicked", self.show_photo_details, None)
        menu.append(detailMenuBtn)

                       
class AlbumView(GnatiracStackableWindow):
    '''
    This view shows all picture in an album
    '''
    
    last_thumbnail = None
    
    def __init__(self, album, facade):
        self.facade = facade
        self.album = album
        self.displayed_photo_count = 0
        GnatiracStackableWindow.__init__(self, album.title)


    def show_album_details(self, widget, data):
        dialog = gtk.Dialog() 
        dialog.set_transient_for(self) 
        dialog.set_title("Album details")
        table = gtk.Table(4,2,False)
        
        row = 0;        
        def add_row_information(name, value, row):            
            child = gtk.Label("%s :" % name)
            table.attach(self.justifyRight(child), 0,1,row,row+1)
            child = gtk.Label(value)
            table.attach(self.justifyLeft(child), 1,2,row,row+1)
            return row + 1
        row = add_row_information("Name", self.album.title, row)
        row = add_row_information("Photos", str(self.album.numphotos), row)
        row = add_row_information("Bytes used", str(self.album.bytesUsed), row)
        row = add_row_information("Access", str(self.album.access), row)
        row = add_row_information("Location", str(self.album.location), row)
        
        dialog.vbox.pack_start(table)
        dialog.show_all() 
        dialog.run()

    def init_menu(self, menu):
        detailMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        detailMenuBtn.set_label("Details");
        detailMenuBtn.connect("clicked", self.show_album_details, None)
        menu.append(detailMenuBtn)


    def init_center_view(self, centerview):       
        # load the thumbnail in background        
        async_thread = AsyncTask(self, self.raise_stop_flag, self.populate_picture_list, centerview)
        async_thread.start()
        
    def _on_more_button_clicked(self, button):        
        self.centerview.remove(button)
        self.centerview.show_all()   
                
        async_thread = AsyncTask(self, self.raise_stop_flag, self.populate_picture_list, self.centerview, start_index=self.displayed_photo_count+1)
        async_thread.start()

    def reset_stop_flag(self):
        self.stop_request_flag = False

    def raise_stop_flag(self):
        self.stop_request_flag = True
    
    def handle_stop_flag(self):
        if self.stop_request_flag:
            self.reset_stop_flag()
            raise StopSignalException()
    
    
    def on_more_button_clicked(self, widget, data):
        call_handled_method(self._on_more_button_clicked, widget)

    def _on_photo_clicked_event(self, thumbnail):
        window = PhotoView(thumbnail,self.facade)
        self.program.add_window(window)
        window.show_all()
        
    def on_photo_clicked_event(self, widget, data):
        call_handled_method(self._on_photo_clicked_event, data)
        
    def populate_picture_list(self, centerview, start_index=1):
        show_banner_information("Loading album content...", gtk_sync=True)
        photo_per_row = 2
        photo_count = 0
        self.reset_stop_flag()
        
        for photo in self.facade.iter_photos_list(self.album,start_index = start_index):
            self.handle_stop_flag()
            # add a photo widget
            thumbnnail = ShotThumbnail(photo, self.last_thumbnail)            
            if self.last_thumbnail:
                self.last_thumbnail.next = thumbnnail          
            self.last_thumbnail = thumbnnail
            
            if (photo_count % photo_per_row == 0) :
                 # strat a new line
                hbox = gtk.HBox()
                centerview.pack_start(hbox)
            gtk.gdk.threads_enter()
            hbox.pack_start(thumbnnail, True, False,0)  
            centerview.show_all()            
            photo_count = photo_count + 1
            self.displayed_photo_count = self.displayed_photo_count + 1                        
            self.set_title("%s %s/%s" % (self.album.title, self.displayed_photo_count, self.album.numphotos) )
            gtk.gdk.threads_leave()    
            
            thumbnnail.connect_action(self.on_photo_clicked_event, thumbnnail)

        if self.displayed_photo_count < self.album.numphotos :
            show_banner_information("More photos are available, see bellow", gtk_sync=True)
            self.nextButton = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT| gtk.HILDON_SIZE_FULLSCREEN_WIDTH, hildon.BUTTON_ARRANGEMENT_VERTICAL)
            self.nextButton.set_title("More")
            self.nextButton.connect("clicked",self.on_more_button_clicked, None)
            gtk.gdk.threads_enter()   
            centerview.add(self.nextButton)            
            centerview.show_all()  
            gtk.gdk.threads_leave()  
        else:
            show_banner_information("Album content loaded", gtk_sync=True)

class LastPictureView(GnatiracStackableWindow):
    '''
    This view show the last uploaded image
    '''
    def __init__(self, facade):
        self.facade = facade
        GnatiracStackableWindow.__init__(self, "Last image")

    def init_center_view(self, centerview):       
        # load the thumbnail in background        
        async_thread = AsyncTask(self, self.raise_stop_flag, self.populate_feed_list, centerview)
        async_thread.start()
        
    def _on_photo_clicked_event(self, photo):
        window = PhotoView(photo,self.facade)
        self.program.add_window(window)
        window.show_all()
        
    def on_photo_clicked_event(self, widget, data):
        call_handled_method(self._on_photo_clicked_event, data)


    def reset_stop_flag(self):
        self.stop_request_flag = False

    def raise_stop_flag(self):
        self.stop_request_flag = True
    
    def handle_stop_flag(self):
        if self.stop_request_flag:
            self.reset_stop_flag()
            raise StopSignalException()
       
    def populate_feed_list(self, centerview):
        album_per_row = 2
        album_count = 0
        self.reset_stop_flag()
        for shot in self.facade.iter_feed_list():
            self.handle_stop_flag()
            # add a album widget
            thumbnnail = ShotThumbnail(shot)            
            if (album_count % album_per_row == 0) :
                 # strat a new line
                hbox = gtk.HBox()
                centerview.pack_start(hbox)
            gtk.gdk.threads_enter()
            hbox.pack_start(thumbnnail, True, False,0)  
            centerview.show_all()            
            gtk.gdk.threads_leave()    
            album_count = album_count + 1                       
            
            thumbnnail.connect_action(self.on_photo_clicked_event, shot)
         

class AlbumListView(GnatiracStackableWindow):
    '''
    This is the album list view
    '''
    def __init__(self, facade):
        self.facade = facade
        GnatiracStackableWindow.__init__(self, "Album list")

    def init_center_view(self, centerview):
        #self.populate_album_list(centerview)
        # load the thumbnail in background                
        async_thread = AsyncTask(self, self.raise_stop_flag, self.populate_album_list, centerview)
        async_thread.start()
        
    def reset_stop_flag(self):
        self.stop_request_flag = False

    def raise_stop_flag(self):
        self.stop_request_flag = True
    
    def handle_stop_flag(self):
        if self.stop_request_flag:
            self.reset_stop_flag()
            raise StopSignalException()
        
    def on_album_clicked_event(self, widget, data):
        window = AlbumView(data,self.facade)
        self.program.add_window(window)
        window.show_all()
                
    def populate_album_list(self, centerview):
        show_banner_information("Loading album list...", gtk_sync=True)        
        album_per_row = 2
        album_count = 0        
        self.reset_stop_flag()
        for album in self.facade.iter_album_list():
            self.handle_stop_flag()
        # add a album widget
            thumbnnail = AlbumThumbnail(album)            
            if (album_count % album_per_row == 0) :
                 # strat a new line
                hbox = gtk.HBox()
                centerview.pack_start(hbox)
            gtk.gdk.threads_enter()
            hbox.pack_start(thumbnnail, True, False,0)
            centerview.show_all()            
            gtk.gdk.threads_leave()    
            album_count = album_count + 1                       
            
            thumbnnail.connect_action(self.on_album_clicked_event, album)
                        
        show_banner_information("Album list loaded", gtk_sync=True)
        
        

                    
    