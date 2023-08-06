
import argparse

VERSION = '0.0.5'
DEFAULT_HOST = 'service.cloudtee.me'
DEFAULT_PORT = '8080'


def get_option_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('topic', metavar='<TOPIC>',
                        help='Topic to subscribe to on CloudTee server')
    parser.add_argument('--host', metavar='<HOST>', default=DEFAULT_HOST,
                        help='CloudTee service hostname')
    parser.add_argument('--port', metavar='<PORT>', type=int,
                        default=DEFAULT_PORT,
                        help='CloudTee service port')
    parser.add_argument('--version', '-v', action='version', version=VERSION,
                        help='print client version and exit')
    return parser
