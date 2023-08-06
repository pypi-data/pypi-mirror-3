import os
import time
from fabric.api import task
from djeploy import djeploy_require, set_env, get_env, command


def get_release_dir(release_dir=None):
    if release_dir is None:
        opts = get_env('env_path')
        env_path = opts['env_path']
        release_dir = os.path.join(env_path, 'releases')
    return release_dir


def get_releases_list(release_dir=None):
    ''' Returns sorted list of all current releases
    '''
    release_dir = get_release_dir(release_dir)

    with command.cd(release_dir):
        opts = {}
        if command.is_local:
            opts['capture'] = True
        releases = command.run('ls -xt', **opts)
        releases = [x.replace('/', '') for x in releases.split()]
    return sorted(releases)


@task
def fail_cleanup(release_dir=None):
    '''
    If your VERY LAST deploy failed, call this to clean up the
    mess left behind. It will only remove the most recent 
    release directory. BE CAREFUL USING THIS.
    '''
    release_dir = get_release_dir(release_dir)

    releases = get_releases_list(release_dir)
    release = releases[-1]
    with command.cd(release_dir):
        command.run('rm -rf %s' % release)


@task
def make_release_directory(release=None):
    ''' Create a new release directory.
    '''
    opts = get_env('env_path')
    env_path = opts['env_path']
    if release is None:
        release = time.strftime('%Y%m%d%H%M%S')

    release_path = os.path.join(env_path, 'releases', release)
    command.run('mkdir -p %s' % release_path)
    set_env(release=release, release_path=release_path)


@task
def remove_old_releases(release_dir=None):
    '''
    Remove oldest releases past the ammount passed 
    in with the "num_releases" variable. Default 5.
    '''
    opts = get_env('num_releases')
    num_releases = int(opts['num_releases'])
    release_dir = get_release_dir(release_dir)

    releases = get_releases_list(release_dir)
    with command.cd(release_dir):
        if len(releases) > num_releases:
            diff = len(releases) - num_releases
            remove_releases = ' '.join(releases[:diff])
            command.run('rm -rf %s' % remove_releases)


@task
def set_num_releases(amount=5):
    ''' Set number of releases to save. Default: 5
    '''
    set_env(num_releases=int(amount))


@task
def symlink_current_release(symlink_name='current'):
    ''' Symlink our current release
    '''
    opts = get_env('env_path', 'release')
    env_path = opts['env_path']
    release = opts['release']

    with command.cd(env_path):
        command.run('ln -nfs releases/%s %s' % (release, symlink_name))


@task
def show_versions(release_dir=None):
    ''' List all deployed versions
    '''
    release_dir = get_release_dir(release_dir)

    with command.cd(release_dir):
        print command.run('ls -xt')


@task
def rollback_version(version, release_dir=None):
    ''' Specify a specific version to be made live
    '''
    opts = get_env('env_path')
    env_path = opts['env_path']
    
    releases = get_releases_list(release_dir)
    if version not in releases:
        command.abort('Version "%s" is not a deployed release!' % version)

    with command.cd(env_path):
        command.run('ln -nfs releases/%s current' % version)


@task
def generic_rollback(release_dir=None):
    ''' Simple GENERIC rollback. Symlink to the second most recent release
    '''
    opts = get_env('env_path')
    env_path = opts['env_path']

    releases = get_releases_list(release_dir)
    release = releases[-2]
    with command.cd(env_path):
        command.run('ln -nfs releases/%s current' % release)


@task
def make_virtual_environment(extra_path=None, site_pkgs=False, python=None):
    ''' Create the virtual environment
    '''
    opts = get_env('release_path')
    release_path = opts['release_path']

    if extra_path is not None:
        release_path = os.path.join(release_path, extra_path)

    cmd = 'virtualenv '
    if not site_pkgs:
        cmd += '--no-site-packages '
    if python is not None:
        cmd += '-p %s ' % python
    cmd += '.'

    with command.cd(release_path):
        command.run(cmd)
        command.run('mkdir -p shared packages')
    set_env(virtual_env_path=release_path)


@task
def install_requirements(req_path='./requirements.txt',
                         cache=None, timeout=None):
    ''' Install the required packages from the requirements file using pip
    '''
    opts = get_env('virtual_env_path')
    virtual_env_path = opts['virtual_env_path']
    tout_str = '--timeout=%i ' % int(timeout) if timeout is not None else ''

    with command.cd(virtual_env_path):
        cmd = 'pip'
        if timeout is not None:
            cmd += ' --timeout=%i' % int(timeout)

        cmd += ' install -E . -r %s' % req_path
        if cache is not None:
            cmd += ' --download-cache=%s' % cache
        command.run(cmd)
