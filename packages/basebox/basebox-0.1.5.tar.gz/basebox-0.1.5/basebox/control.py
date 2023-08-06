from collections import defaultdict
import json
import os

from fabric.api import env, settings, abort
from fabric.colors import red


def vagrant_environment(name, dir='vagrant'):
    '''
    Configure and load the named vagrant environment.
    Usage (with config at ./vagrant/test/environment.json):

        fab vagrant_environment:test [tasks in environment]

    Conventions:
    - Represent a cluster as a JSON file ('environment.json') in a directory
      that can double as a Vagrant directory.
    - Use the cluster spec to project a Vagrantfile and to assign roles to the
      boxes.
    - Load role -> host mappings to initialize fabric roledefs.

    Example environment.json showing all currently supported keys:
    {
        "vms": {
            "web": {                   # box name for vagrant
                "box": "base",         # name or URL of installed base box
                "ip": "192.168.1.10",  # address on host-only network
                "roles": ["app", "redis", "cache"]  # fabric roles for this box
            },
            "db": {
                "box": "base",
                "ip": "192.168.1.11",
                "roles": ["database", "solr"]
            },
            ... etc. ...
        }
    }
    '''
    env_dir = os.path.abspath(os.path.join(dir, name))
    env_config = os.path.join(env_dir, 'environment.json')
    if not file_exists(env_config):
        abort(red('Could not load environment config: %s' % env_config))

    # Load config and bring boxes up
    config = json.loads(file_read(env_config))
    file_render_template('vagrant/Vagrantfile',
                         os.path.join(env_dir, 'Vagrantfile'),
                         context=config)

    env.roledefs = defaultdict(list, env.roledefs)
    for name, vm in (config.get('vms') or {}).items():
        env.hosts.append(vm['ip'])
        for role in vm.get('roles') or []:
            env.roledefs[role].append(vm['ip'])

    with cd(env_dir):
        run('vagrant up')

    # register boxes by role
    import environments
    environments.shared()
