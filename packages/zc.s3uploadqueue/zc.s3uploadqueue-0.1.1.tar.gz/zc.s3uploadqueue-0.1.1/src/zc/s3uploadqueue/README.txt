Use a file-system directory as an queue for uploading files to S3
=================================================================

This package provides support for implementing an S3 upload queue
using a file directory.

An application that wants to upload to S3 writes a temporary file and
then moves it into a directory and then goes on about it's business.

Separately, either in a daemon, or in a separate application thread,
zc.s3uploadqueue.main is run, which watches the directory and moves
files to S3 as they appear.

The main function takes the name of a configuration file.


The configuration file has 2 sections:

Credentials
   The AWS credentials, with options:

   aws_access_key_id
       Your AWS access key

   aws_secret_access_key
       Your AWS secret access key

Queue
   Option controlling the queue processing:

   directory
       The directory containing files to be moved to S3

   bucket
       The S3 bucket name

   poll-interval
       How often to poll for files.

       This defaults to 9 seconds.

   threads
       The number of threads to use for processing files.

        Defaults to 9.

   log-level
        Basic logging log level.

        Defaults to INFO.

The file names in the directory must be URL-encoded S3 Keys.  This
allows '/'s to be included without using directories.

The ``main`` function will poll the directory every poll interval and
upload any files found. As it uploads each file, it will remove it
from the source directory.  After uploading all of the files found, it
will poll immediately, in case new files were added while processing
files.

Here's a sample configuration::

    [Credentials]
    aws_access_key_id = 42
    aws_secret_access_key = k3y

    [Queue]
    directory = test
    bucket = testbucket
    poll-interval = 1
    threads = 2

.. -> config

    >>> import os
    >>> os.mkdir('test')
    >>> write('queue.cfg', config)

If we were to put files in S3, we'd place them in the ``test``
directory.  For example, to put data at the key:
``2012-06-14/01.txt``, we'd store the data in the file::

    2012-06-14%2F01.txt

.. -> name

This is the key name urlquoted with no safe characters::

    urllib.quote(key, safe='')

We can run the updater as a long-running script (using something like
`zdaemon <http://pypi.python.org/pypi/zdaemon>`_ or `supervisor
<http://pypi.python.org/pypi/supervisor>`_) or as a from an existing
process.  To run from an existing process, just import the ``process``
function and run it::

   import zc.s3uploadqueue
   stop = zc.s3uploadqueue.process('queue.cfg')
   if stop: stop()

.. -> src

This starts a daemonic threads that upload any files placed in the directory.

.. basic test with above data and code

    Place some data:

    >>> write('/'.join(['test', name.strip()]), '')

    >>> import logging
    >>> import zope.testing.loggingsupport

    >>> handler = zope.testing.loggingsupport.InstalledHandler(
    ...     "zc.s3uploadqueue", level=logging.INFO)

    >>> def show_log():
    ...     print handler
    ...     handler.clear()

    Start the processor:

    >>> exec src

    Wait a bit and see that boto was called:

    >>> import time
    >>> time.sleep(.1)

The two threads we created setup the necessary connection with S3:

    >>> import boto.s3.connection, pprint
    >>> pprint.pprint(boto.s3.connection.S3Connection.mock_calls) #doctest: +ELLIPSIS
    [call('42', 'k3y', calling_format=<boto.s3.connection.OrdinaryCallingFormat object at ...>),
     call().get_bucket('testbucket'),
     call('42', 'k3y', calling_format=<boto.s3.connection.OrdinaryCallingFormat object at ...>),
     call().get_bucket('testbucket')]

The file that we put in is processed and uploaded to S3:

    >>> pprint.pprint(boto.s3.key.Key.mock_calls) #doctest: +ELLIPSIS
    [call(<MagicMock name='S3Connection().get_bucket()' id='...'>),
     call(<MagicMock name='S3Connection().get_bucket()' id='...'>),
     call().set_contents_from_filename('test/2012-06-14%2F01.txt')]

    >>> show_log()
    zc.s3uploadqueue INFO
      Transferred '2012-06-14%2F01.txt'

If there's an exception, that'll be logged as well. To simulate an exception,
we'll monkey-patch the "urllib.unquote" method to raise an exception.

    >>> import urllib
    >>> orig_unquote = urllib.unquote
    >>> def fake_unquote(s):
    ...     1/0
    >>> urllib.unquote = fake_unquote
    >>> write('/'.join(['test', name.strip()]), '')
    >>> exec src

    >>> show_log()
    zc.s3uploadqueue ERROR
      processing '2012-06-14%2F01.txt'

    >>> urllib.unquote = orig_unquote

If there's an error getting the S3 bucket, an exception will be printed.

    >>> def foo(self, s):
    ...     raise Exception('some error accessing an S3 bucket.')
    >>> boto.s3.connection.S3Connection.return_value.get_bucket.side_effect = foo
    >>> write('/'.join(['test', name.strip()]), '')
    >>> exec src
    >>> show_log()
    zc.s3uploadqueue ERROR
      Error accessing bucket: 'testbucket'

    >>> handler.uninstall()

