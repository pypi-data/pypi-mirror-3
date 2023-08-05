##################################################################################
#    Copyright (c) 2010 Cynapse India Pvt. Ltd., All rights reserved. 
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation, version 2.                                      
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    
#                                                                                 
##################################################################################

__author__ = """Brent Lambert"""

from zope.interface import implements
from urllib import unquote
from zope.component import adapts
from interfaces import IZipFileAdapter
from collective.zipfiletransport.utilities.interfaces import IZipFileTransportUtility
from Products.ATContentTypes.interfaces import IATImage
from urlparse import urlparse
from Products.CMFCore.interfaces import IContentish


class BaseZipFileAdapter(object):
    """ Base class for Zip File Object adapter. """

    implements(IZipFileAdapter)

    def __init__(self, context):
        self.context = context

    def _getFilePath(self, context, extension=''):
        """ Get a proper path from the object for the zip archive. """
        # Find the relative path
        opath = str(self.context.virtual_url_path())
        cpath = str(context.virtual_url_path())
        object_path = opath.replace(cpath+'/', '')
        # Remove invalid characters
        object_path = unquote(object_path)
        # If required, add extension
        if extension:
            object_path += extension
        return object_path


class ATImageZipFileAdapter(BaseZipFileAdapter):
    """ Adapts image objects to be able to read/write to Zip archives. """

    mime_types = ['image/jpeg']

    def writeObjectToZipArchive(self, context, zipfile, comments):
        """ Write the image data and path to zip file. """
        filedata = str(self.context.data)
        filepath = self._getFilePath(context)
        if filepath:
            zipfile.writestr(filepath, filedata)

    def readObjectFromZipArchive(self, zipfile):
        """ Read data from Zip Archive and store in the image. """


class ATFileZipFileAdapter(BaseZipFileAdapter):
    """ Adapts file objects to be able to read/write to Zip archives. """
        
    def writeObjectToZipArchive(self, context, zipfile, comments):
        """ Write the file data and path to Zip archive. """
        filedata = str(self.context.data)
        filepath = self._getFilePath(context)
        if filepath:
            zipfile.writestr(filepath, filedata)

    def readObjectFromZipArchive(self, zipfile):
        """ Read data from Zip Archive and store in the file. """


class ATDocumentZipFileAdapter(BaseZipFileAdapter):
    """ Adapts Documents to be able to read/write to Zip archives. """

    def writeObjectToZipArchive(self, context, zipfile, comments):
        """ Write the document and its path to Zip archive. """
        fmt = self.context.Format()
        if 'text/html' == fmt:
            filedata = '<!-- collective.zipfiletransport: ATDcoument -->\n'
            filedata += self.context.getText()
            extension = '.html'
        elif 'text/x-rst' == fmt:
            filedata = self.context.getRawText()
            extension = '.rst'
        elif 'text/structured' == fmt:
            filedata = self.context.getRawText()
            extension = '.stx'
        elif 'text/plain' == fmt:
            filedata = self.context.getRawText()
            extension = '.txt'
        else:
            filedata = self.context.getRawText()
            extension = None
        if IContentish.providedBy(self.context) and self.context.isDiscussable() and comments:
            cmview = self.context.restrictedTraverse('@@get_raw_comments')
            filedata += cmview(self.context)
        filepath = self._getFilePath(context, extension)
        if filepath:
            zipfile.writestr(filepath, filedata)

    def readObjectFromZipArchive(self, zipfile):
        """ Read data from Zip archive and store it in the document. """


class ATLinkZipFileAdapter(BaseZipFileAdapter):
    """ Adapts link objects to be able to be read/written to Zip archives. """

    def writeObjectToZipArchive(self, context, zipfile, comments):
        """ Write the link to the Zip archive as an html snippet. """
        filedata = '<!-- collective.zipfiletransport: ATLink -->\n'
        filedata += '<a href="%s" alt="%s">%s</a>\n' %(self.context.getRemoteUrl(),
                                                       self.context.title,
                                                       self.context.title)
        filepath = self._getFilePath(context, '.html')
        if filepath:
            zipfile.writestr(filepath, filedata)

    def readObjectFromZipArchive(self, zipfile):
        """ Read link data from Zip archive. """


class ATFavoriteZipFileAdapter(BaseZipFileAdapter):
    """ """

    def writeObjectToZipArchive(self, context, zipfile, comments):
        """ """
        filedata = '<!-- collective.zipfiletransport: ATFavorite -->\n'
        filedata += '<a href="%s" alt="%s">%s</a>\n' %(self.context.getRemoteUrl(),
                                                       self.context.title,
                                                       self.context.title)
        filepath = self._getFilePath(context, '.html')
        if filepath:
            zipfile.writestr(filepath, filedata)

    def readObjectFromZipArchive(self, zipfile):
        """ """

class ATNewsItemZipFileAdapter(BaseZipFileAdapter):
    """ """

    def writeObjectToZipArchive(self, context, zipfile, comments):
        """ """
        filedata = '<!-- collective.zipfiletransport: ATNewsItem -->\n'
        filedata += self.context.getText()
        filepath = self._getFilePath(context, '.html')
        if IContentish.providedBy(self.context) and self.context.isDiscussable() and comments:
            cmview = self.context.restrictedTraverse('@@get_raw_comments')
            filedata += cmview(self.context)
        if filepath:
            zipfile.writestr(filepath, filedata)


    def readObjectFromZipArchive(self, zipfile):
        """ """

class ATEventZipFileAdapter(BaseZipFileAdapter):
    """ """

    def writeObjectToZipArchive(self, context, zipfile, comments):
        """ """
        cal = "BEGIN:VCALENDAR\n"
        cal += "VERSION:2.0\n"
        cal += "PRODID:collective.zipfiletransport\n"
        cal += "BEGIN:VEVENT\n"
        cal += "UID:%s@%s\n" %(self.context.created().strftime('%Y%m%dT%H%M%S'),
                               urlparse(self.context.absolute_url())[1])
        cal += "DSTAMP:%s\n" %(self.context.created().strftime('%Y%m%dT%H%M%S'))
        cal += "DTSTART:%s\n" %(self.context.startDate.strftime('%Y%m%dT%H%M%S'))
        cal += "DTEND:%s\n" %(self.context.endDate.strftime('%Y%m%dT%H%M%S'))
        cal += "SUMMARY:%s\n" %(self.context.description)
        cal += "END:VEVENT\n"
        cal += "END:VCALENDAR\n"
        filepath = self._getFilePath(context, '.ics')
        if filepath:
            zipfile.writestr(filepath, cal)

    def readObjectFromZipArchive(self, zipfile):
        """ """


class ATFolderZipFileAdapter(BaseZipFileAdapter):
    """ Adapts Folders to be able to be read/written to Zip archives. """

    def writeObjectToZipArchive(self, context, zipfile, comments):
        """ Write a folder with its path to Zip archive. """

        # If the folder has been extended to have a text body
        if getattr(self.context, 'getRawText', None):
            filedata = self.context.getRawText()
            filepath = self.getFilePath(context, '/index.html')
            if filepath:
                zipfile.writestr(filepath, filedata)

    def readObjectFromZipArchive(self, zipfile):
        """ Read folder from Zip archive. """

