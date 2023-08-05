import urlparse
import httplib
import json
import time

from socket import timeout
from threading import Thread
from time import sleep

class StreamListener(object):

    def __init__(self, newStateCallback):
        self.newStateCallback = newStateCallback

    def on_state(self, state):
        """Called when a new state is received from connection.

        Override this method if you wish to manually handle
        the stream data. Return False to stop stream and close connection.
        """
        if self.newStateCallback(state) == False:
          return False

    def on_error(self, status_code):
        """Called when a non-200 status code is returned"""
        return False

    def on_timeout(self):
        """Called when stream connection times out"""
        return

class Stream(object):

    def __init__(self, listener, **options):
        self.url = options.get('url')
        _,self.host,_,_,_,_ = urlparse.urlparse(self.url)
        self.listener = listener
        self.running = False
        self.timeout = options.get("timeout", 300.0)
        self.retry_count = options.get("retry_count")
        self.retry_time = options.get("retry_time", 10.0)
        self.snooze_time = options.get("snooze_time",  5.0)
        self.buffer_size = options.get("buffer_size",  1500)

        self.headers = options.get("headers") or {}
        self.body = options.get("body") or {}

    def _run(self):

        # Connect and process the stream
        error_counter = 0
        conn = None
        exception = None
        while self.running:
            if self.retry_count is not None and error_counter > self.retry_count:
                # quit if error count greater than retry count
                break
            try:
                conn = httplib.HTTPConnection(self.host)
                conn.connect()
                conn.sock.settimeout(self.timeout)
                print self.url
                print self.body
                print self.headers
                conn.request('POST', self.url, self.body, headers=self.headers)
                resp = conn.getresponse()
                if resp.status != 200:
                    if self.listener.on_error(resp.status) is False:
                        break
                    error_counter += 1
                    sleep(self.retry_time)
                else:
                    error_counter = 0
                    self._read_loop(resp)
            except timeout:
                if self.listener.on_timeout() == False:
                    break
                if self.running is False:
                    break
                conn.close()
                sleep(self.snooze_time)
            except Exception, exception:
                # any other exception is fatal, so kill loop
                break

        # cleanup
        self.running = False
        if conn:
            conn.close()

        if exception:
            raise

    def _read_loop(self, resp):
          decode = json.JSONDecoder().raw_decode 
          data = ''
          while self.running:
            if resp.isclosed():
                break
            c = resp.read(100)
            data += c
            try: 
              state, i = decode(data) 
              data = data[i:].lstrip()
            except ValueError:
                time.sleep(0.01)
                continue

            # read state and pass into listener
            if self.listener.on_state(state) is False:
                self.running = False

    def _start(self, async):
        self.running = True
        if async:
            Thread(target=self._run).start()
        else:
            self._run()

    def listen(self, count=None, async=False):
        if self.running:
            raise GrokError('Stream object already connected!')
        self._start(async)

    def disconnect(self):
        if self.running is False:
            return
        self.running = False