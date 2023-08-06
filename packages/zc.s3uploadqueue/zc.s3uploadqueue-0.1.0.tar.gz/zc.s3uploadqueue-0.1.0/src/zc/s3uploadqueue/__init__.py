##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import boto.s3.connection
import boto.s3.key
import ConfigParser
import logging
import os
import Queue
import sys
import time
import urllib
import zc.thread

logger = logging.getLogger(__name__)

levels = dict(
    CRITICAL=50,
    ERROR=40,
    WARNING=30,
    INFO=20,
    DEBUG=10,
    NOTSET=0,
    )

def process(config=None):
    return_stop = True
    if config is None:
        [config] = sys.argv[1:]
        return_stop = False

    parser = ConfigParser.RawConfigParser()
    parser.read(config)
    options = dict((section, dict(parser.items(section))) for section in parser.sections())

    logging.basicConfig(level=levels[options['Queue'].get('log-level', 'INFO')])

    queue = Queue.Queue()
    srcdir = options['Queue']['directory']
    nthreads = int(options['Queue'].get('threads', 9))
    poll_interval = int(options['Queue'].get('poll-interval', 9))

    def process_queue(bucket):
        key = boto.s3.key.Key(bucket)

        while 1:
            try:
                name = queue.get()
                if name is None:
                    # stop
                    return
                key.key = urllib.unquote(name)
                path = os.path.join(srcdir, name)
                key.set_contents_from_filename(path)
                os.remove(path)
                logger.info('Transferred %r', name)
            except Exception:
                logger.exception('processing %r', name)
            finally:
                queue.task_done()

    running = [1]
    threads = []
    for i in range(nthreads):
        conn = boto.s3.connection.S3Connection(
            options['Credentials']['aws_access_key_id'],
            options['Credentials']['aws_secret_access_key'],
            )
        try:
            bucket = conn.get_bucket(options['Queue']['bucket'])
        except Exception:
            logger.exception('Error accessing bucket: %r', options['Queue']['bucket'])
            return
        threads.append(zc.thread.Thread(process_queue, args=[bucket]))

    def stop():
        running.pop()
        for thread in threads:
            thread.join(1)

    @zc.thread.Thread(daemon=False)
    def poll():
        while running:
            files = os.listdir(srcdir)
            if files:
                for name in files:
                    queue.put(name)
                queue.join()
            else:
                time.sleep(poll_interval)
        for thread in threads:
            queue.put(None)

    if return_stop:
        return stop

if __name__ == '__main__':
    process()

