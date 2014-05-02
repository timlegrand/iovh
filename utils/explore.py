#!/usr/bin/env python2.7

import sys
import argparse
import logging

import url_utils as url
from entity import *
from auth import *

class color:
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


def print_alinea(text, level):
    print '|   ' * (level-1) + '    ' * (level-2) + ('|-- ' if level != 0 else '') + color.BOLD + text + color.END


def visit(path, recursive=None, level=0):
    response = api.get(path)
    print_alinea(path, level)

    if isinstance(response, dict):
        if 'message' in response.keys():
            if 'This service does not exist' in response.values():
                logging.warn('Skipped: ' + path + ' (not implemented by OVH)')
                return
            elif 'does not answer to the GET HTTP method' in response['message']:
                logging.warn('Skipped: ' + response['message'])
                #(Cannot be browsed: OVH REST map unconsistent)
                return
        ### Node has direct children
        elif 'apis' in response.keys():
            for k in response['apis']:
                subpath = url.join(path, k['path'])
                if recursive:
                    visit(subpath, recursive, level+1)
        ### Node is an entity
        else:
            n = Node(response)
            logging.info(n)
    
    ### Path is a list of IDs
    elif isinstance(response, list):
        if not response:
            pass
            logging.info('Skipped: ' + path + ' (empty list of IDs)')
        else:
            for id in response:
                entity_path = url.join(path, id)
                if recursive:
                    visit(entity_path, recursive, level+1)
                else:
                    print_alinea(path, level)

    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Explore OVH API.')
    parser.add_argument('-p', '--path',  default='/', required=True, help='path to start exploration from')
    parser.add_argument('-r', '--recursive', action="store_true", help='enable recursive browsing')
    parser.add_argument('-v', '--verbose', action="store_const", dest="loglevel", const=logging.INFO, help='print objects details')
    parser.add_argument('-d', '--debug', action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING, help='Print lots of debugging statements')
    args = parser.parse_args()    
    logging.basicConfig(level=args.loglevel)

    ### Grant access to users' account
    api = get_api()
    
    ### One-shot request for consistency testing
    #response = api.get(args.path)
    #print response

    ### Launch explorer
    visit(args.path, args.recursive)

