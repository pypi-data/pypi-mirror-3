
import socket


class _Stream(object):
    def __init__(self, host, port, topic, **extra_options):
        self.conn_info = (host, port)
        self.topic = topic
        self.socket = self._open_socket()

        self._init_socket(self.socket, topic, **extra_options)

    def _init_socket(self, socket):
        raise NotImplementedError()

    def _open_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.conn_info)
        return sock

    def close(self):
        self.socket.close()


class WritableStream(_Stream):
    def _init_socket(self, sock, topic):
        init_message = 'SEND %s\n' % topic
        sock.send(init_message)

    def write(self, data):
        self.socket.send(data)


class ReadableStream(_Stream):
    def _init_socket(self, sock, topic, **kwargs):
        show_timestamp = 'yes' if kwargs.get('show_timestamp', True) else 'no'
        show_client = 'yes' if kwargs.get('show_client', True) else 'no'
        http_headers = (
            'GET /%s' % topic,
            'X-CloudTee-Show-Timestamp: %s' % show_timestamp,
            'X-CloudTee-Show-Client: %s' % show_client,
            '\r\n',
        )
        sock.send('\r\n'.join(http_headers))

    def read(self):
        while True:
            yield self.socket.recv(1024)
