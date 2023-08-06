#!/usr/bin/env python
#coding: utf-8
#
# File Name: timeline.py
#
# Description: The main timeline listener for weetwit's timelined.
#
# Creation Date: 2012-03-05
#
# Last Modified: 2012-03-26 12:37
#
# Created By: Daniël Franke <daniel@ams-sec.org>

#import os

#from time import time

from tweepy import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

search_args = ["#zomertijd"]

class StreamTestListener(StreamListener):

    def on_status(self, status):
        """docstring for on_status"""
        print "%s: %s" % (status.user.screen_name, status.text)

at = '469366388-TcAZd9giSagUFtS7Rba424STfRTfQ6RDxgqRl9Qu'
ats = 'gpnC3zHP7BwZzvn9JEItwQMRKmGpCk7pbDMYl4bnVc'
cs = 'PLQgA1NVoT1TDPpuSEqPxuxVZPvC58C64E43oX22osw'
ck = '4gpu1fbB2rQmDRvRzdog'

auth = OAuthHandler(ck, cs)
auth.set_access_token(at, ats)

stream = Stream(auth=auth, listener=StreamTestListener(), buffer_size=1)
stream.filter( track=search_args)
