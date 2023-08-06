import os
from fabric.api import task
from djeploy import djeploy_require, set_env, get_env, command


@task
def run_manage_command(cmd, extra_path=None):
    ''' Run manage.py syncdb
    '''
    opts = get_env('release_path', 'virtual_env_path', 'scm_repo_name')
    release_path = opts['release_path']
    virtual_env_path = opts['virtual_env_path']
    scm_repo_name = opts['scm_repo_name']
    python_path = os.path.join(virtual_env_path, 'bin', 'python')
    manage_path = os.path.join(release_path, scm_repo_name)
    if extra_path is not None:
        manage_path = os.path.join(manage_path, extra_path)

    with command.cd(manage_path):
        command.run('%s ./manage.py %s' % (python_path, cmd))


@task
def django_syncdb(extra_path=None):
    ''' Run manage.py syncdb
    '''
    run_manage_command('syncdb --noinput', extra_path)


@task
def django_migrate(extra_path=None):
    ''' Run manage.py migrate (requires South)
    '''
    run_manage_command('migrate', extra_path)


@task
def django_collectstatic(extra_path=None):
    ''' Run manage.py collectstatic
    '''
    run_manage_command('collectstatic --noinput', extra_path)
