#!/usr/bin/env python
from ansible.module_utils.basic import AnsibleModule


def build():
  params = dict(
    kind=dict(type='str', default='python'),
    spec=dict(type='str', required=True),
    config=dict(type='str', required=True),
    dest=dict(type='str', required=True)
  )
  return AnsibleModule(argument_spec=params, supports_check_mode=True)


def main():
  module = build()
  rc, out, err = module.run_command([
    'openapi-generator-cli',
    'generate',
    '-g', module.params['kind'],
    '-i', module.params['spec'],
    '-c', module.params['config'],
    '-o', module.params['dest']
  ])
  if rc != 0:
    return module.fail_json(changed=False, failed=True, skipped=False, output=err)
  return module.exit_json(changed=True, failed=False, skipped=False, output=out)


if __name__ == '__main__':
  main()