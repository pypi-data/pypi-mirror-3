#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
""" Script to interact with the DB.
"""
from services.config import Config
from wimms.shardedsqlstorage import NodeSQL
import sys


def main():
    args = sys.argv[1:]

    config = Config('/etc/mozilla-services/nodes.cfg').get_map()
    storage = NodeSQL(config['nodes.admin_uri'])

    if len(args) < 2:
        exit("Usage: refresh_nodes.py <count> <product> [<cluster> [<node>]]")

    count = int(args[0])
    product = args[1]
    cluster = node = None

    if len(args) > 2:
        cluster = args[2]

    if len(args) > 3:
        node = args[3]

    storage.update_available(count, product, cluster, node)
