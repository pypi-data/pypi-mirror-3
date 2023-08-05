import sys, os, json

from fabric import context_managers
from fabric.api import settings, env, sudo
from fabric.network import disconnect_all

from charon import loader

configured = False

def set_host(host):
    env.host_string = host

def set_key_filename(obj):
    env.key_filename = obj

def configure():
    conf = loader.read_configuration()

    if 'CHARON_HAPROXY_HOST' in conf:
        set_host(conf['CHARON_HAPROXY_HOST'])

    if 'CHARON_KEY_FILENAME' in conf:
        set_key_filename(conf['CHARON_KEY_FILENAME'])

    global configured
    configured = True

def _do_command(command):
    if not configured:
        configure()

    with settings(context_managers.hide('everything'), abort_on_prompts=True):
        result = sudo(command)

    old_stdout, sys.stdout = sys.stdout, open(os.devnull, 'w')
    disconnect_all()
    sys.stdout = old_stdout
    return json.loads(result.stdout)

def show(frontend=None, host=None):
    parts = ['charon show']
    if frontend:
        parts.append(frontend)
        if host:
            parts.append(host)

    return _do_command(' '.join(parts))

def add(frontend, host, state='enabled'):
    return _do_command('charon add %s %s %s' % (frontend, host, state,))

def remove(frontend, host):
    return _do_command('charon remove %s %s' % (frontend, host,))

def enable(frontend, host):
    return _do_command('charon enable %s %s' % (frontend, host,))

def disable(frontend, host):
    return _do_command('charon disable %s %s' % (frontend, host,))
