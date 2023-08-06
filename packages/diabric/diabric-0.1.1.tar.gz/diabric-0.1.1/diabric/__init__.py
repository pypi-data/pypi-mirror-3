
'''
FABRIC UTILITY FUNCTIONS
'''


import collections
import os
import shutil
import subprocess

import fabric.api
import fabric.contrib.files
import fabric.operations
from fabric.api import env, task, sudo, run, cd, local, lcd, execute, get, put
from fabric.contrib.files import exists, upload_template
from fabric.contrib.project import rsync_project


###############
# EC2 FUNCTIONS

def print_instances(instances, prefix=''):
    for instance in instances:
        print_instance(instance, prefix=prefix)


def print_instance(instance, prefix=''):
    print '{}Instance id={}, state={}, tags={}, public_dns_name={}'.format(
        prefix, instance.id, instance.state, instance.tags,
        instance.public_dns_name)


def terminate_instances(conn, instances):
    if not instances:
        return
    killed_instances = conn.terminate_instances([i.id for i in instances])
    if len(killed_instances) != len(instances):
        raise Exception('Not all instances terminated.', instances, 
                        killed_instances)
    print 'Terminated instances:'
    print_instances(killed_instances, '\t')


def get_named_instance(conn, name):
    '''
    Return a single non-terminated, non-shutting-down
    boto.ec2.instance.Instance that has a tag 'Name' that
    matches ``name``.

    conn: a boto.ec2.connection.EC2Connection
    name: string. The unique value of the 'Name' tag of a (running) instance
    return: the instance of the current webserver, of None if there is none.
    raise: Exception if there is more than one non-terminated instance.
    '''
    rs = conn.get_all_instances(filters={'tag:Name': name})
    instances = [i for r in rs for i in r.instances if i.state not in ['terminated', 'shutting-down']]
    if len(instances) > 1:
        raise Exception('More than one instance', instances)
    if not instances:
        return None
    return instances[0]






##################################
# Upstart, event-based init daemon
# http://upstart.ubuntu.com/


def upstart_conf_program(conf):
    '''
    conf: local upstart configuration file for the program.  If the program
    is named 'program', the basename of conf should be 'program.conf'.
    '''
    put(conf, os.path.join('/etc/init', os.path.basename(conf)), use_sudo=True)


def upstart_reload_program(program):
    '''
    program: the name of the program to use in initctl commands.

    Reload configuration, stop program if it is running, and start program.
    '''
    # reload upstart config
    sudo('initctl reload-configuration')

    with settings(warn_only=True):
        # fyi: error to stop an already stopped program
        sudo('initctl stop {}'.format(program))

    # fyi: error to start a running program
    sudo('initctl start {}'.format(program))


#############
# SUPERVISORD
# http://supervisord.org/index.html

class Supervisord(object):
    def install():
        pass

    def conf():
        pass

    def conf_dir():
        pass

    def conf_program():
        pass

    def reload_program():
        pass

    def program_conf_file():
        pass


def supervisord_install(conf_dir='/etc/supervisor.d'):
    '''
    conf_dir: defaults to '/etc/supervisor.d'.  If given, this directory will
    be made when installing supervisord.  If None, no directory will be made.
    It is a best practice to have a directory in which to place modular program
    configuration files for supervisor.  For example if you had a program 
    managed by supervisor named 'myapp', you might put its program
    configuration in /etc/supervisor.d/myapp.conf.
    
    Install the supervisor python package.  Currently this tries to install 
    distribute and pip into python2.7 and then install supervisor with pip.
    '''
    # Install distribute, a pip dependency
    sudo('curl http://python-distribute.org/distribute_setup.py | python2.7')
    # install pip in system python
    sudo('curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python2.7')
    # install supervisord to supervise nginx, gunicorn.
    sudo('pip-2.7 install supervisor')
    # make a dir for modular supervisor config files
    sudo('mkdir -p /etc/supervisor.d')


def supervisord_conf(conf):
    '''
    conf: local configuration file for supervisord.

    Upload supervisord's main configuration file.
    '''
    # FYI: how to generate a conf file.
    # sudo('echo_supervisord_conf > supervisord.conf')

    # supervisord configuration
    put(conf, '/etc/supervisord.conf', use_sudo=True)


def supervisord_reload():

    sudo('supervisorctl reload')


def supervisord_conf_program(src, dest, context=None, use_sudo=False,
                               mode=None):
    '''
    src: local configuration file, e.g. /path/to/program.conf
    dest: remote config file path, e.g. /etc/supervisor.d/program.conf

    Upload supervisor configuration for a program.
    '''
    upload_template(
        src,
        dest,
        context=context,
        use_sudo=use_sudo,
        mode=mode)


def supervisord_program_path(program):
    '''
    Return the canonical remote location of the configuration file for program.
    '''
    return '/etc/supervisor.d/{}.conf'.format(program)


def supervisord_reload_program(program):
    '''
    program: the name of a supervisor 'program' section.

    Reread supervisor's configuration and restart the program using the
    new configuration (if any).  Use this function to restart a program if
    its configuration has changed.
    '''
    # reread configuration files
    sudo('supervisorctl reread') 
    # stop the program if it is running.
    sudo('supervisorctl stop {}'.format(program)) 
    # remove the old program configuration
    sudo('supervisorctl remove {}'.format(program))
    # add the new program configuration
    sudo('supervisorctl add {}'.format(program))
    # start the program
    sudo('supervisorctl start {}'.format(program))


    

############
# DEPRECATED

# I now recommend running sshd on localhost to maintain the Fabric paradigm.

# This is bad advice:
# http://stackoverflow.com/questions/6725244/running-fabric-script-locally
def setremote():
    '''
    set env.* to the remote versions for run, cd, rsync, and exists
    '''
    env.run = fabric.api.run
    env.cd = fabric.api.cd
    env.rsync = rsync
    env.exists = fabric.contrib.files.exists
    return env

def setlocal():
    '''
    set env.* to the localhost versions for run, cd, rsync, and exists
    '''
    env.run = fabric.api.local
    env.cd = fabric.api.lcd
    env.rsync = lrsync
    env.exists = os.path.exists
    return env


def lrsync(options, src, dest, cwd=None, **kwds):
    '''
    options: list of rsync options, e.g. ['--delete', '-avz']
    src: source directory (or files).  Note: rsync behavior varies depending on whether or not src dir ends in '/'.
    dest: destination directory.
    cwd: change (using subprocess) to cwd before running rsync.
    This is a helper function for using rsync to sync files to localhost.
    It uses subprocess.  Note: shell=False.
    Use rsync() to sync files to a remote host.
    '''
    args = ['rsync'] + options + [src, dest]
    print args
    subprocess.check_call(args, cwd=cwd)
    
    


