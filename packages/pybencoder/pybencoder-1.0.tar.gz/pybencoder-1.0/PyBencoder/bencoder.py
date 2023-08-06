#!/usr/bin/env python
# -*- coding: utf-8 -*-

# BENCODER CLASS
# deal with bencoded strings
#
# http://en.wikipedia.org/wiki/Bencode
# for usage see README
#
# don't use directly Ben* classes, use only PyBencoder with its
# automagically methods encode() and decode()
#
# @author: Cristian Năvălici ncristian [at] lemonsoftware eu
# @version: February - March 2012
#

import sys


from benexceptions import BenInvalidInputError, BenInvalidEncoded, BenInvalidMark

class PyBencoder(object):
    _obj = None

    BENCODE_INT_START = 'i'
    BENCODE_LIST_START = 'l'
    BENCODE_DICT_START = 'd'
    BENCODE_STR_SEPARATOR = ':'

    END_MARK = 'e'

    def decode(self, input_data = None):
        try:
            if input_data is None:
                raise BenInvalidInputError(self, "Please provide something to decode")

            dec = self.get_bentype_decoder(input_data)
            dec.decode(input_data)

            self._obj = dec # used in __str__

            return dec.result
        except Exception, e:
            print e

    def encode(self, input_data = None):
        try:
            if input_data is None:
                raise BenInvalidInputError(self, "Please provide something to encode")

            encob = self.get_bentype_encoder(input_data)
            return encob.encode(input_data)
        except Exception, e:
            print e


    def get_left(self):
        '''get what\'s left after decoding, if it's the case'''
        return self._obj.left_str if self._obj else None


    def get_bentype_encoder(self, elem):
        '''return the needed encoder for an elem'''
        if isinstance(elem, tuple([int, long, bool])): return BenInt()
        if isinstance(elem, tuple([basestring, buffer])): return BenString()
        if isinstance(elem, tuple([list, tuple])): return BenList()
        if isinstance(elem, tuple([dict])): return BenDict()

        raise Exception("No encoder found {0}".format(elem))


    def get_bentype_decoder(self, elem):
        '''return the needed decoder for an elem'''
        first = elem[0]

        if first == self.BENCODE_INT_START: return BenInt()
        if first == self.BENCODE_LIST_START: return BenList()
        if first == self.BENCODE_DICT_START: return BenDict()
        if first.isdigit(): return BenString()

        raise Exception("No decoder found {0}".format(first))


    def __str__(self): return repr(self.obj.result)


class BenInt(PyBencoder):
    def __init__(self): self.result = None

    def encode(self, input_data):
        return "{0}{1:-d}{2}".format(self.BENCODE_INT_START, input_data, self.END_MARK)

    def decode(self, raw_str = ''):
        '''decodes an integer from an raw string. It also retains the next offset
        in the raw string after extraction.
        FORMAT: i<number>e'''
        try:
            if raw_str[0] is not self.BENCODE_INT_START:
                raise BenInvalidMark(self, 'The starting mark ({0}) is missing'.format(BENCODE_INT_START))

            end_offset = raw_str.find(self.END_MARK)
            if end_offset == -1:
                raise BenInvalidMark(self, 'The ending mark ({0}) is missing'.format(self.END_MARK))

            self.left_str = raw_str[end_offset + 1:]

            self.result = int(raw_str[1:end_offset])

            return self.result
        except Exception, e:
            print e



class BenString(PyBencoder):

    def __init__(self): self.result = None

    def encode(self, input_data):
        try:
            ascii_ver = input_data.decode('ascii')
            return "{0}:{1}".format(len(ascii_ver), ascii_ver)
        except UnicodeDecodeError, e:
            raise BenInvalidInputError(self, "Non-ASCII chars in the provided input")
        except Exception, e:
           print e
           sys.exit()


    def decode(self, raw_str):
        '''decodes a string from an raw string. It also retains the next offset
        in the raw string after extraction.
        FORMAT: <length>:<contents>'''
        try:
            # extract the first part, length
            separator_index = raw_str.find(self.BENCODE_STR_SEPARATOR)
            if separator_index == -1:
                raise BenInvalidMark(self, 'The separator mark ({0}) is missing'.format(self.BENCODE_STR_SEPARATOR))

            first_part = raw_str[ :separator_index]
            if not first_part.isdigit():
                raise BenInvalidEncoded(self, 'Invalid Length', first_part)

            encoded_str_length = int(first_part)

            # extract the second part, contents
            content_str = raw_str[separator_index + 1: ]
            if len(content_str) < encoded_str_length:
                raise BenInvalidEncoded(self, 'String "{0}" too small for reported length'.format(content_str), encoded_str_length)

            decoded_str = content_str[ :encoded_str_length]

            self.left_str = raw_str[ separator_index + encoded_str_length + 1: ]

            self.result = decoded_str

            return decoded_str
        except Exception, e:
           print e



class BenList(PyBencoder):
    def __init__(self):
        self.result = []
        self.parent = super(BenList, self)

    def encode(self, input_data = []):
        try:
            if not isinstance(input_data, list):
                raise BenInvalidInputError(self, "Input is not a list")

            part_result = ""
            for elem in input_data: part_result += self.parent.encode(elem)

            return "{0}{1}{2}".format(self.BENCODE_LIST_START, part_result, self.END_MARK)
        except Exception, e:
           print e


    def decode(self, raw_str = ''):
        try:
            if raw_str[0] is not self.BENCODE_LIST_START:
                raise BenInvalidMark(self, 'The starting mark ({0}) is missing'.format(self.BENCODE_LIST_START))

            left = raw_str[1:]
            self.result = []

            while left and left[0] is not self.END_MARK:
                self.parent.decode(left)

                self.result.append(self._obj.result) # obj is a decoder object saved in parent class
                left = self._obj.left_str

            self.left_str = left[1:]
        except Exception, e:
            print e



class BenDict(PyBencoder):
    def __init__(self):
        self.result = {}
        self.parent = super(BenDict, self)

    def encode(self, input_data = None):
        ''' all keys are strings '''
        try:
            result = self.BENCODE_DICT_START
            for k, v in input_data.iteritems():
                result += self.parent.encode(str(k)) + self.parent.encode(v)
            result += self.END_MARK

            return result
        except Exception, e:
           print e

    def decode(self, raw_str = ''):
        try:
            if raw_str[0] is not self.BENCODE_DICT_START:
                raise BenInvalidMark(self, 'The starting mark ({0}) is missing'.format(self.BENCODE_DICT_START))

            # treat the dictionary as a list
            items_as_list = self.parent.decode(self.BENCODE_LIST_START + raw_str[1:])

            if len(items_as_list) % 2 != 0:
                raise Exception("Encoded data is not a dictionary. Odd number of items.")

            for it in range(0, len(items_as_list), 2):
                k = items_as_list[it]
                v = items_as_list[it+1]
                self.result[k] = v

            return self.result
        except Exception, e:
            print e





if __name__ == "__main__": pass
