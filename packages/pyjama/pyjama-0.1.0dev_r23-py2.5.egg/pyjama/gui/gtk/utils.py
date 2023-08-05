# -*- encoding: UTF-8 -*-

#    Pyjama is a python project bootstraper for Maemo5 development
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
Created on Nov 16, 2011

@author: maemo
'''

import gtk


from pyjama.common import version

version.getInstance().submitRevision("$Revision: 37 $")


LOGO_PIXBUF = gtk.gdk.pixbuf_new_from_file("pyjama-logo.png")


def fill_widget_with_logo(centerview):
    pixbuf = LOGO_PIXBUF
    for i in range(1,3):
        hbox = gtk.HBox()
        for j in range(1,5):                
            image = gtk.Image()
            image.set_from_pixbuf(pixbuf)
            hbox.add(image)
        centerview.add(hbox)
        



                    