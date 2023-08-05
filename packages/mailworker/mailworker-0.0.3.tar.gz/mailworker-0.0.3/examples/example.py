#!/usr/bin/env python
# encoding: utf-8
"""
mail_worker.py

Created by Ben Hughes on 2011-10-17.
Copyright (c) 2011 Bright Approach Ltd.. All rights reserved.
"""
from hotqueue import HotQueue
from logbook import Logger


mail_queue = HotQueue("mail_queue", host="localhost", port=6379, db=0)

def send_messages(messages_to_send):
    for message in xrange(messages_to_send):
        log.info('Sending mail %s' % message)
        mail_queue.put({'to':'bwghughes@gmail.com', 'from':'bwghughes@gmail.com', 'subject':'Hi'})
        
if __name__ == '__main__':
    log = Logger(__name__)
    log.info('Sending mail messages...')
    send_messages(10)
