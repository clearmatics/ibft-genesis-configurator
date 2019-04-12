#!/usr/bin/env python

import json
from os import listdir
from os.path import isfile, join, isdir

path_genesis_template = '/autonity/genesis-template.json'
path_validators = '/autonity/validators'
path_observers = '/autonity/observers'


def get_genesis_template():
    with open(path_genesis_template) as f:
        genesis = json.load(f)
    return genesis


def get_keys(path):
    list_vars = [f for f in listdir(path) if isfile(join(path, f))]
    addresses = {}
    pub_keys = {}
    for key_name in list_vars:
        splitted_key_name = [x.strip() for x in key_name.split('.')]
        if splitted_key_name[1] == 'address':
            f = open(path + '/' + key_name, 'r')
            addresses[splitted_key_name[0]] = f.readline().splitlines()[0]
            f.close()
        elif splitted_key_name[1] == 'pub_key':
            f = open(path + '/' + key_name, 'r')
            pub_keys[splitted_key_name[0]] = f.readline().splitlines()[0]
            f.close()
    return {'addresses': addresses, 'pub_keys': pub_keys}


def patch_genesis(genesis, validators, observers):
    print('======Validators ======')

    # List allowed addresses
    print(list(validators['addresses'].values()))
    print('======Observers ======')
    print(observers)
    return genesis


def main():
    genesis = get_genesis_template()
    validators = get_keys(path_validators)
    observers = get_keys(path_observers)
    genesis = patch_genesis(genesis, validators, observers)

    print(genesis)


if __name__ == '__main__':
    main()
