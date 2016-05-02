#!/usr/bin/env python

from __future__ import print_function

import argparse
import logging
import os
from rdflib import Graph as graph
import requests
from io import BytesIO
import sys
import yaml


class fcrepo_resource(graph):
    '''subclass of an rdflib.Graph representing a Fedora resource'''
    def __init__(self, filepath, uri):
        graph.__init__(self)
        self.parse(filepath, format='turtle')
        self.filename = os.path.basename(filepath)
        self.uri = uri
        print(" - Resource {0} has {1} triples.".format(
                                                    self.filename, len(self)))
    
    # serialize resource as turtle
    def turtle(self):
        return self.serialize(format='turtle')
    
    # PUT resource to specified fcrepo
    def deposit(self):
        data = BytesIO(self.turtle())
       # headers = {'content-type': 'application/turtle'}
        response = requests.put(self.uri, 
                                data = data,
                                auth = (FEDORA_USER, FEDORA_PASSWORD))
        return response
    
    # filter out triples in with predicates in 'server-managed' namespaces
    def filter(self, ns):
        print("Filtering triples in namespace {0} ...".format(ns))
        for triple in self:
            if triple[1].startswith(ns):
                self.remove(triple)
            elif triple[0].endswith('fcr:export?format=jcr/xml'):
                print("Removing resource export triple...")
                self.remove(triple)


def main():
    '''Parse args, loop over repository and restore.'''
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Restore serialized Fedora repository.')
    parser.add_argument('-c', '--config', required=True,
        help='relative or absolute path to the YAML config file')
    args = parser.parse_args()
    
    # print header
    title = "| FCREPO SERIALIZATION RESTORATION |"
    border = "-" * len(title)
    print("\n".join(["", border, title, border]))
    
    # load and parse specified configuration settings
    with open(args.config, 'r') as configfile:
        globals().update(yaml.safe_load(configfile))
    
    # the server-managed namespaces to filter
    server_managed = FILTER_NAMESPACES.values()
    
    # check the connection to fcrepo
    print('Ready to load to endpoint => {0}'.format(REST_ENDPOINT))
    print('Testing connection with provided credentials => ', end='')
    response = requests.get(REST_ENDPOINT, 
                            auth=(FEDORA_USER, FEDORA_PASSWORD))
    print(response)
    
    # check the backup tree
    print('Scanning serialization tree => {0}'.format(BACKUP_LOCATION))
    
    # loop over files, read as graph, filter, PUT to fcrepo
    for root, dirs, files in os.walk(BACKUP_LOCATION):
        print("\n{0}".format(root))
        for f in files:
            if f.endswith('.ttl'):
                filepath = os.path.join(root, f)
                repopath = os.path.relpath(filepath, BACKUP_LOCATION)
                uri = os.path.join(REST_ENDPOINT, repopath)
                resource = fcrepo_resource(filepath, uri)
                for nspace in server_managed:
                    resource.filter(nspace)
                print(resource.turtle())
                print(resource.deposit())


if __name__ == "__main__":
    main()
