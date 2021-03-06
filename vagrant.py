#!/usr/bin/env python

import argparse
import json
import os
import yaml
from re import sub

def setup_cli():
    ''' setup CLI '''
    parser = argparse.ArgumentParser(description='Ansible/Vagrant Dynamic Inventory Script')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--list', action="store_true", help='Return JSON for all groups.')
    group.add_argument('--host', help='Return host specific, or empty, JSON')
    return parser

def build_inventory(host=None):
    ''' build inventory from vagrant.yml '''
    config = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), 'vagrant.yml')))
    domain = config['domain']
    inventory = {}

    # build groups for a specific host
    def _gather_groups(inventory, host):
        for group in host['ansible_groups']:
            if group not in inventory:
                inventory[group] = {}
                inventory[group]['hosts'] = []
                inventory[group]['vars'] = {}
            inventory[group]['hosts'].append(host['name'] + domain)
        # append box version
        box = sub(r"[/]", "_", config['box'])
        if 'box' in host:
            box = sub(r"[/]", "_", host['box'])
        if box not in inventory:
            inventory[box] = {}
            inventory[box]['hosts'] = []
            inventory[box]['vars'] = {}
        inventory[box]['hosts'].append(host['name'] + domain)

    # build inventory object
    if host:
        _gather_groups(inventory, [i for i in config['vms'] if i['name'] == host][0])
    else:
        for host in config['vms']:
            _gather_groups(inventory, host)
    return inventory

def main():
    ''' main function '''
    parser = setup_cli()
    args = parser.parse_args()
    if args.list:
        print(json.dumps(build_inventory()))
    elif args.host:
        print(json.dumps(build_inventory(args.host)))
    else:
        parser.print_help()

main()
