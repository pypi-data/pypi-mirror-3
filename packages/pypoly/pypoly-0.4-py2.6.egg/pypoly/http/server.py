from SocketServer import ThreadingMixIn
from Queue import Queue
import socket
import threading
import wsgiref.simple_server


class ThreadPoolMixIn(ThreadingMixIn, wsgiref.simple_server.WSGIServer):
    """
    Use a thread pool instead of a new thread on every request
    """

    num_threads = 10

    #: fix socket.error on server restart
    allow_reuse_address = True

    def serve_forever(self):
        """
        """
        self.requests = Queue(self.num_threads)

        for x in range(self.num_threads):
            t = threading.Thread(
                target=self.process_request_thread
            )
            t.daemon = 1
            t.start()

        # server main loop
        while True:
            self.handle_request()

        self.server_close()

    def process_request_thread(self):
        """
        Process a request from the queue.
        """
        while True:
            a = self.requests.get()
            ThreadingMixIn.process_request_thread(self, *a)

    def handle_request(self):
        """
        Collect a request and put it in the queue.
        """
        try:
            request, client_address = self.get_request()
        except socket.error:
            return

        if self.verify_request(request, client_address):
            self.requests.put((request, client_address))
