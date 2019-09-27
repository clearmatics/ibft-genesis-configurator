#!/usr/bin/env python

import json
import argparse
from kubernetes import client, config
from os import listdir, environ
from os.path import isfile, join, isdir

path_genesis_template = '/autonity/genesis-template.json'
path_validators = '/autonity/validators'
path_observers = '/autonity/observers'
path_operator_governance = '/autonity/operator-governance'
path_operator_treasury = '/autonity/operator-treasury'


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


def patch_genesis_legacy(genesis, validators, observers, balance):
    alloc        = {}
    validatorIps = environ.get('VALIDATOR_IPS')
    observerIps  = environ.get('OBSERVER_IPS')

    for key, value in validators['addresses'].items():
        alloc[value] = {'balance': balance}
    genesis['alloc'] = alloc

    enodeWhitelist = []
    
    if validatorIps:
        validatorIpsArr = validatorIps.split(" ")
        for key, value in validators['pub_keys'].items():
            enodeWhitelist.append('enode://{pub_key}@{name}:{port}'.format(
                pub_key=value,
                name=validatorIpsArr[int(key)],
                port=30303
            ))
        
    else:
        for key, value in validators['pub_keys'].items():
            enodeWhitelist.append('enode://{pub_key}@validator-{name}:{port}'.format(
                pub_key=value,
                name=key,
                port=30303
            ))

    if observerIps:
        observerIpsArr = observerIps.split(" ")
        for key, value in observers['pub_keys'].items():
            enodeWhitelist.append('enode://{pub_key}@{name}:{port}'.format(
                pub_key=value,
                name=observerIpsArr[int(key)],
                port=30303
            ))
    else:
        for key, value in observers['pub_keys'].items():
            enodeWhitelist.append('enode://{pub_key}@observer-{name}:{port}'.format(
                pub_key=value,
                name=key,
                port=30303
            ))
    genesis['config']['enodeWhitelist'] = enodeWhitelist
    genesis['validators'] = list(validators['addresses'].values())
    return genesis


def patch_genesis(genesis, validators, observers, operator_governance, operator_treasury, balance, stake, mingasprice, gaslimit):
    alloc = {}
    validatorIps = environ.get('VALIDATOR_IPS')
    observerIps = environ.get('OBSERVER_IPS')

    genesis['config']['autonityContract']['minGasPrice'] = mingasprice
    genesis['gasLimit'] = gaslimit

    for key, value in operator_governance['addresses'].items():
        genesis['config']['autonityContract']['governanceOperator'] = value

    for key, value in operator_treasury['addresses'].items():
        alloc[value] = {'balance': balance}
    genesis['alloc'] = alloc

    users = []

    if validatorIps:
        validatorIpsArr = validatorIps.split(" ")
        for key, value in validators['pub_keys'].items():
            enode = 'enode://{pub_key}@{name}:{port}'.format(
                pub_key=value,
                name=validatorIpsArr[int(key)],
                port=30303
            )
            users.append({"enode": enode,
                          "type" : "validator",
                          "stake": stake
                          })

    else:
        for key, value in validators['pub_keys'].items():
            enode = 'enode://{pub_key}@validator-{name}:{port}'.format(
                pub_key=value,
                name=key,
                port=30303
            )
            users.append({"enode": enode,
                          "type" : "validator",
                          "stake": stake
                          })

    if observerIps:
        observerIpsArr = observerIps.split(" ")
        for key, value in observers['pub_keys'].items():
            enode = 'enode://{pub_key}@{name}:{port}'.format(
                pub_key=value,
                name=observerIpsArr[int(key)],
                port=30303
            )
            users.append({"enode": enode,
                          "type" : "participant"
                          })
    else:
        for key, value in observers['pub_keys'].items():
            enode = 'enode://{pub_key}@observer-{name}:{port}'.format(
                pub_key=value,
                name=key,
                port=30303
            )
            users.append({"enode": enode,
                          "type" : "participant"
                          })

    genesis['config']['autonityContract']['users'] = users
    return genesis


def write_genesis(genesis, namespace):
    api_instance = client.CoreV1Api()
    cmap = client.V1ConfigMap()
    cmap.data = {'genesis.json': json.dumps(genesis, indent=2)}
    api_instance.patch_namespaced_config_map('genesis', namespace, cmap)


def main():
    parser = argparse.ArgumentParser(description='Generate genesis.json and write it to configmap')
    parser.add_argument('-k',
                        dest='kubeconf_type',
                        default='pod',
                        choices=['pod', 'remote'],
                        help='Type of connection to kube-apiserver: pod or remote (default: %(default)s)'
                        )

    parser.add_argument('-legacy-genesis',
                        dest='legacy_genesis',
                        default=False,
                        action='store_true',
                        help='Legacy genesis.json structure (for autonity < v0.2.0)'
                        )
    parser.add_argument('--stake',
                        dest='stake',
                        default=500000,
                        type=int,
                        help='Stake for each validator (default: %(default)s)'
                        )
    parser.add_argument('--mingasprice',
                        dest='mingasprice',
                        default=10000000000000,
                        type=int,
                        help='Minimum Gas Price (default: %(default)s)'
                        )
    parser.add_argument('--gaslimit',
                        dest='gaslimit',
                        default="0x5F5E100",
                        type=str,
                        help='Gas Limit (default: %(default)s)'
                        )
    parser.add_argument('--balance',
                        dest='balance',
                        default='0x200000000000000000000000000000000000000000000000000000000000000',
                        type=str,
                        help='Balance for each treasury operator (default: %(default)s)'
                        )
    args = parser.parse_args()

    if args.kubeconf_type == 'pod':
        config.load_incluster_config()
        f = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r")
        namespace = f.readline()
        f.close()

    genesis = get_genesis_template()
    validators = get_keys(path_validators)
    observers = get_keys(path_observers)

    if args.legacy_genesis:
        genesis = patch_genesis_legacy(genesis, validators, observers, args.balance,)
        print('INFO: legacy genesis.json generated')
    else:
        operator_governance = get_keys(path_operator_governance)
        operator_treasury = get_keys(path_operator_treasury)
        print(operator_governance)
        print(operator_treasury)
        genesis = patch_genesis(genesis, validators, observers, operator_governance, operator_treasury, args.balance, args.stake, args.mingasprice, args.gaslimit)
        print('INFO: Stake for each validator: ' + str(args.stake))
        print('INFO: Balance for each treasury operator: ' + args.balance)
        print('INFO: NEW genesis.json generated')


    print(json.dumps(genesis, indent=2))

    if args.kubeconf_type == 'pod':
        write_genesis(genesis, namespace)


if __name__ == '__main__':
    main()

