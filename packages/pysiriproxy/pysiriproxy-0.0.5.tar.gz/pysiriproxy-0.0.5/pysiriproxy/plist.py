# Copyright (C) (c) 2012 Brett Ponsler, Pete Lamonica, Pete Lamonica
# This file is part of pysiriproxy.
#
# pysiriproxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pysiriproxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pysiriproxy.  If not, see <http://www.gnu.org/licenses/>.
'''The plist module contains the Plist, and BinaryPlist classes.

These classes are designed to encapsulate a plist object, and be able
to convert a standard plist into a binary formatted plist.

'''
import biplist
from string import printable
from datetime import datetime
from StringIO import StringIO
from CFPropertyList import CFPropertyList, native_types

from pysiriproxy.utf import Utf
from pysiriproxy.constants import Keys

from pyamp.util import getStackTrace


class BinaryPlist:
    '''The BinaryPlist class takes in a dictionary containing data and
    provides the ability to convert the dictionary into a binary plist.

    .. note:: This class uses the :mod:`biplist` module to convert a Python
              dictionary into a binary plist.

    '''
    
    def __init__(self, data, logger, logFile="/dev/null"):
        '''
        * data -- The data to convert into a binary plist
        * logger -- The logger
        * logFile -- The file to which output will be logged

        '''
        self.__log = logger.get("BinaryPlist")
        self.__logFile = logFile

        # Make sure any non-printable characters are wrapped with the
        # biplist Data class
        self.__data = self.__fixItems(data)

    def toBinary(self):
        '''Convert the data into a binary plist.'''
        return biplist.writePlistToString(self.__data)

    def __fixItems(self, data):
        '''Ensure that any entries in the given dictionary that contain
        non-printable characters are wrapped with the biplist Data object.

        * data -- The data dictionary
        
        '''
        # Traverse all the keys in the dictionary
        for key, item in data.iteritems():
            if key in [Keys.Text, Keys.SpeakableText]:
                try:
                    # @todo: the @{tts} tags in the speakable text key are
                    #        breaking, because the hex does not get parsed!
                    if key == Keys.SpeakableText:
                        item = self.__removeTts(item)

                    # Replace all the known utf strings with ASCII equivalents
                    item = Utf.replaceUtf(item)
                    data[key] = self.__wrapItem(item.decode("utf-8"))
                except:
                    data[key] = item
                    self.__log.error("Error translating to unicode: %s, %s" % \
                                         (type(item), item))
                    self.__log.error(getStackTrace())
            elif key in [Keys.Birthday, Keys.Date, Keys.DueDate]:
                # @todo: This actually works....but I have no idea why it works.
                # Obviously this is not the date it is actually storing...but,
                # it still displays the correct date on the phone, somehow...
                data[key] = datetime.now()
            else:
                data[key] = self.__fixItem(item)

        return data

    def __fixItem(self, item):
        '''Ensure that the given item is wrapped by the biplist Data class.

        * item -- The item that should be wrapped

        '''
        # If we found a dictionary, recurse, otherwise wrap the value
        # if it contains non-printable characters
        if type(item) == type(dict()):
            # Fix all the items in the dictionary
            item = self.__fixItems(item)
        elif type(item) == type(list()):
            # Fix all items in the list
            item = map(self.__fixItem, item)
        elif type(item) == type(str()):
            # Fix any unicode or non-printable strings
            item = self.__wrapItem(item)

        return item

    def __wrapItem(self, item):
        '''Return the item properly wrapped in the biplist Data class if it
        contains any non-printable characters. Otherwise, simply return the
        item itself.

        * item -- The item

        '''
        # Wrap any items containing non-printable characters,
        # otherwise, do nothing
        if self.__shouldWrap(item):
            return biplist.Data(item)
        else:
            return item

    def __shouldWrap(self, string):
        '''Determine if the given string should be wrapped with the biplist
        Data class, or not.

        * string -- The string

        '''
        # Determine if our string is a subset of the printable characters
        # and that it does not contain unicode characters
        return not set(string).issubset(set(printable)) \
            or self.__containsUnicode(string)

    def __containsUnicode(self, string):
        '''Determine if the given string contains unicode characters or not.

        * string -- The string

        '''
        try:
            str(string).decode('ascii')
            return False
        except:
            return True

    @classmethod
    def __removeTts(cls, text):
        '''Remove the tts tag from the given piece of text.

        * text -- The text

        '''
        startIndex = text.find("@{tts#")
        if startIndex != -1:
            endIndex = startIndex + text[startIndex:].find("}")
            text = text[:startIndex] + text[endIndex + 1:]

        return text


class Plist:
    '''The Plist class contains methods pertaining to converting objects
    to plist objects and manipulating them.

    '''

    @classmethod
    def convert(cls, objectData):
        '''Convert the given object into a plist.

        * objectData -- The data for this object

        '''
        string = StringIO(objectData)

        plist = CFPropertyList(string)
        plist.load()

        return native_types(plist.value)

    @classmethod
    def toBinary(cls, data, logger, logFile="/dev/null"):
        '''Convert an object into a binary plist.

        * data -- The data to convert into a binary plist
        * logger -- The logger
        * logFile -- The file to which output will be logged

        '''
        return BinaryPlist(data, logger, logFile).toBinary()
