from __future__ import absolute_import, with_statement

from argparse import ArgumentParser
from shutil import copy
from sys import stdout, stdin
import logging

from inifaction import API_URL, CONFIG_TEMPLATE, SECTIONS
from inifaction.setup import Setup


VERSION = '0.1'

def get_parser():
    usage = 'usage: %(prog)s [template|setup] [options]'
    parser = ArgumentParser(usage=usage)

    parser.add_argument('action', choices=('template', 'setup'))
    parser.add_argument('-f', '--file', help='file to write the template'
            ' or to read the config, stdin/stdout otherwise')
    parser.add_argument('-s', '--section', help='setup only desired section')

    parser.add_argument('-l', '--loglevel', default='INFO', choices=(
        'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
    parser.add_argument('-v', '--version', action='version', 
            version='%(prog)s ' + VERSION)
    return parser


def main():
    parser = get_parser()
    namespace = parser.parse_args()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setLevel(namespace.loglevel)
    handler.setFormatter(formatter)
    logger = logging.getLogger('inifaction')
    logger.setLevel(namespace.loglevel)
    logger.addHandler(handler)

    if namespace.action == 'template':
        if namespace.file:
            copy(CONFIG_TEMPLATE, namespace.file)
        else:
            with open(CONFIG_TEMPLATE) as template:
                stdout.write(template.read())
    else:
        if namespace.file:
            config = open(namespace.file)
        else:
            config = stdin

        setup = Setup(API_URL, config)

        sections = SECTIONS.keys()
        if namespace.section:
            sections = [namespace.section]
        setup.setup(sections)

if __name__ == '__main__':
    main()
