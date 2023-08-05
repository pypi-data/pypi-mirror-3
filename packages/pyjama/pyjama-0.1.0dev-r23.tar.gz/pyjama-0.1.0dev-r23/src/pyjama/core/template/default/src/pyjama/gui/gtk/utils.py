${HEADER}

'''
Created on ${DATE_TIME}

@author: ${AUTHOR}
'''

import gtk


from ${NAME}.common import version

version.getInstance().submitRevision("$Revision: 37 $")


LOGO_PIXBUF = gtk.gdk.pixbuf_new_from_file("${NAME}-logo.png")


def fill_widget_with_logo(centerview):
    pixbuf = LOGO_PIXBUF
    for i in range(1,3):
        hbox = gtk.HBox()
        for j in range(1,5):                
            image = gtk.Image()
            image.set_from_pixbuf(pixbuf)
            hbox.add(image)
        centerview.add(hbox)
        



                    