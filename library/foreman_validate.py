#!/usr/bin/python
#coding: utf-8 -*-

# (c) 2015, Tim Rozet <trozet@redhat.com>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.


import requests
import json
from time import sleep
from ansible.module_utils.basic import *

DOCUMENTATION = '''
---
module: foreman
version_added: "0.1"
short_description: Validates hosts are active in Foreman
description:
   - Verifies hosts are in Active state in Foreman.
options:
        foreman_username                = dict(default='admin'),
        foreman_password                = dict(required=True),
        foreman_url                     = dict(default='https://127.0.0.1/api/v2/'),
        node_list                       = dict(required=True),
        retries                         = dict(default=60),
        delay                           = dict(default=60),
   foreman_username:
     description:
        - login username to authenticate to foreman
     required: true
     default: admin
   foreman_password:
     description:
        - Password of login user
     required: true
   foreman_url:
     description:
        - The foreman api url
     required: false
     default: 'https://127.0.0.1/v2.0/'
   node_list:
     description:
        - List of hostname instances to check
     required: true
     default: None
   retries:
     description:
        - number of retries to check if node is active
     required: false
     default: 60
   delay:
     description:
        - Amount of time in seconds to wait between checks
     required: false
     default: 60
'''

EXAMPLES = '''
# Creates a new VM and attaches to a network and passes metadata to the instance
'''


def main():
    module = AnsibleModule(
        argument_spec                   = dict(
        foreman_username                = dict(default='admin'),
        foreman_password                = dict(required=True),
        foreman_url                     = dict(default='https://127.0.0.1/api/v2/'),
        node_list                        = dict(required=True),
        retries                         = dict(default=60),
        delay                           = dict(default=60),
        ),
    )

    # pull out the module params
    username = module.params['foreman_username']
    password = module.params['foreman_password']
    url = module.params['foreman_url']
    node_list = module.params['node_list']
    retries = module.params['retries']
    delay = module.params['delay']

    # Create a new http session with the following auth details and disabling ssl verification.
    s = requests.Session()
    s.auth = (username, password)
    s.verify = False

    headers = {'Content-Type': 'application/json', }

    for node in node_list:
        node_active = False
        retry_counter = 0
        while retry_counter < retries:
            r = s.get(url + 'hosts/%s/status' % node, headers=headers)
            if r.status_code == 200:
                if r.json()['status'] == 'Active':
                    node_active = True
                    break
            retry_counter += 1
            sleep(delay)
        if node_active is False:
            module.fail_json(msg='Unable to determine node: %s status' % node)

    module.exit_json(changed=True, msg="Nodes are Active")

if __name__ == '__main__':
    main()

