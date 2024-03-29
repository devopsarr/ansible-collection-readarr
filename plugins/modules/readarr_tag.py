#!/usr/bin/python

# Copyright: (c) 2020, Fuochi <devopsarr@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: readarr_tag

short_description: Manages Readarr tag.

version_added: "1.0.0"

description: Manages Readarr tag.

options:
    label:
        description: Actual tag.
        required: true
        type: str
    state:
        description: Create or delete a tag.
        required: false
        default: 'present'
        choices: [ "present", "absent" ]
        type: str

extends_documentation_fragment:
    - devopsarr.readarr.readarr_credentials

author:
    - Fuochi (@Fuochi)
'''

EXAMPLES = r'''
# Create a tag
- name: Create a tag
  devopsarr.readarr.tag:
    label: default

# Delete a tag
- name: Delete a tag
  devopsarr.readarr.tag:
    label: wrong
    state: absent
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
id:
    description: Tag ID.
    type: int
    returned: always
    sample: '1'
label:
    description: The output message that the test module generates.
    type: str
    returned: 'on create/update'
    sample: 'hd'
'''

from ansible_collections.devopsarr.readarr.plugins.module_utils.readarr_module import ReadarrModule
from ansible.module_utils.common.text.converters import to_native

try:
    import readarr
    HAS_READARR_LIBRARY = True
except ImportError:
    HAS_READARR_LIBRARY = False


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        # TODO: add validation for lowercase tags
        label=dict(type='str', required=True),
        state=dict(default='present', type='str', choices=['present', 'absent']),
    )

    result = dict(
        changed=False,
        id=0,
    )

    module = ReadarrModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    client = readarr.TagApi(module.api)

    # List resources.
    try:
        tags = client.list_tag()
    except Exception as e:
        module.fail_json('Error listing tags: %s' % to_native(e.reason), **result)

    # Check if a resource is present already.
    for tag in tags:
        if tag['label'] == module.params['label']:
            result.update(tag)

    # Create a new resource.
    if module.params['state'] == 'present' and result['id'] == 0:
        result['changed'] = True
        # Only without check mode.
        if not module.check_mode:
            try:
                response = client.create_tag(tag_resource={
                    'label': module.params['label'],
                })
            except Exception as e:
                module.fail_json('Error creating tag: %s' % to_native(e.reason), **result)
            result.update(response)

    # Delete the resource.
    elif module.params['state'] == 'absent' and result['id'] != 0:
        result['changed'] = True
        # Only without check mode.
        if not module.check_mode:
            try:
                response = client.delete_tag(result['id'])
            except Exception as e:
                module.fail_json('Error deleting tag: %s' % to_native(e.reason), **result)
            result['id'] = 0

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
