#!/usr/bin/env python
# -*- coding: utf-8 -*-

# BENCODER CUSTOM EXCEPTIONS

class BenException(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)

        self.classname = args[0].__class__
        self.arg_raw = args[1]
    

class BenInvalidInputError(BenException):
    def __init__(self, *args):
        BenException.__init__(self, *args)
        self.message = args[1]
    
    def __str__(self):
        return "[Invalid Input][{0}] {1}".format(self.classname, self.message)


class BenInvalidMark(BenException):
    def __init__(self, *args):
        BenException.__init__(self, *args)
        self.message = args[1]

    def __str__(self):
        err_str = '[Invalid Mark][{0}] '.format(self.classname)
        err_str += '{0}'.format(self.message) 
        return err_str


class BenInvalidEncoded(BenException):
    def __init__(self, *args):
        BenException.__init__(self, *args)
        self.message = args[1]
        self.encstr = args[2]

    def __str__(self):
        err_str = '[Invalid Encoded String][{0}] '.format(self.classname)
        err_str += '{0}:{1}'.format(self.message, self.encstr) 
        return err_str
