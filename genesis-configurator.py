#!/usr/bin/env python

import json

path_genesis_template = '/autonity/genesis-template.json'


def get_genesis_template():
    print('Start')
    with open(path_genesis_template) as f:
        genesis = json.load(f)
    return genesis


def main():
    print(get_genesis_template())


if __name__ == '__main__':
    main()
