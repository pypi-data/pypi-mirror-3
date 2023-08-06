from fabric.api import *
from djeploy import get_env, command


@task(alias='env')
def space(envname='None'):
    ''' Specify the deploy environment. ie: space:staging
    '''
    opts = get_env('space_options')
    space_options = opts.get('space_options')
    if envname in space_options:
        func = space_options[envname]
        if not callable(func):
            command.abort('space option must be a callable function.')
        return func()
    else:
        if 'default' in space_options:
            func = space_options['default']
            if callable(func):
                return func()

    command.abort('"%s" is an invalid space option' % envname)


@task
def deploy(dtype='None'):
    ''' Specify the deploy type. ie, deploy:full
    '''
    opts = get_env('deploy_options')
    deploy_options = opts.get('deploy_options')
    if dtype in deploy_options:
        func = deploy_options[dtype]
        if not callable(func):
            command.abort('deploy option must be a callable function.')
        return func()
    else:
        if 'default' in deploy_options:
            func = deploy_options['default']
            if callable(func):
                return func()

    command.abort('"%s" is an invalid deploy option' % dtype)
