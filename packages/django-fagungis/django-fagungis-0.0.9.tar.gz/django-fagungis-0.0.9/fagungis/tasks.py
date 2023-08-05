#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from os.path import join, abspath, dirname, isfile
from fabric.api import env, puts, abort, cd, hide, task
from fabric.operations import sudo, settings, run
from fabric.contrib import console
from fabric.contrib.files import upload_template

from fabric.colors import _wrap_with, green

green_bg = _wrap_with('42')
red_bg = _wrap_with('41')
fagungis_path = dirname(abspath(__file__))


##########################
## START Fagungis tasks ##
##########################


@task
def setup():
    #  test configuration start
    if not test_configuration():
        if not console.confirm("Configuration test %s! Do you want to continue?" % red_bg('failed'), default=False):
            abort("Aborting at user request.")
    #  test configuration end
    if env.ask_confirmation:
        if not console.confirm("Are you sure you want to setup %s?" % red_bg(env.project.upper()), default=False):
            abort("Aborting at user request.")
    puts(green_bg('Start setup...'))
    start_time = datetime.now()

    _verify_sudo
    _install_dependencies()
    _create_django_user()
    _setup_directories()
    _hg_clone()
    _install_virtualenv()
    _create_virtualenv()
    _install_gunicorn()
    _install_requirements()
    _upload_nginx_conf()
    _upload_rungunicorn_script()
    _upload_supervisord_conf()

    end_time = datetime.now()
    finish_message = '[%s] Correctly finished in %i seconds' % \
    (green_bg(end_time.strftime('%H:%M:%S')), (end_time - start_time).seconds)
    puts(finish_message)


@task
def deploy():
    #  test configuration start
    if not test_configuration():
        if not console.confirm("Configuration test %s! Do you want to continue?" % red_bg('failed'), default=False):
            abort("Aborting at user request.")
    #  test configuration end
    _verify_sudo()
    if env.ask_confirmation:
        if not console.confirm("Are you sure you want to deploy in %s?" % red_bg(env.project.upper()), default=False):
            abort("Aborting at user request.")
    puts(green_bg('Start setup...'))
    start_time = datetime.now()

    hg_pull()
    _install_requirements()
    _upload_nginx_conf()
    _upload_rungunicorn_script()
    _prepare_django_project()
    _prepare_media_path()
    _supervisor_restart()

    end_time = datetime.now()
    finish_message = '[%s] Correctly deployed in %i seconds' % \
    (green_bg(end_time.strftime('%H:%M:%S')), (end_time - start_time).seconds)
    puts(finish_message)


@task
def hg_pull():
    with cd(env.code_root):
        run('hg pull -u')


@task
def test_configuration(verbose=True):
    errors = []
    parameters_info = []
    if 'project' not in env or not env.project:
        errors.append('Project name missing')
    elif verbose:
        parameters_info.append(('Project name', env.project))
    if 'repository' not in env or not env.repository:
        errors.append('Repository url missing')
    elif verbose:
        parameters_info.append(('Repository url', env.repository))
    if 'hosts' not in env or not env.hosts:
        errors.append('Hosts configuration missing')
    elif verbose:
        parameters_info.append(('Hosts', env.hosts))
    if 'django_user' not in env or not env.django_user:
        errors.append('Django user missing')
    elif verbose:
        parameters_info.append(('Django user', env.django_user))
    if 'django_user_group' not in env or not env.django_user_group:
        errors.append('Django user group missing')
    elif verbose:
        parameters_info.append(('Django user group', env.django_user_group))
    if 'django_user_home' not in env or not env.django_user_home:
        errors.append('Django user home dir missing')
    elif verbose:
        parameters_info.append(('Django user home dir', env.django_user_home))
    if 'projects_path' not in env or not env.projects_path:
        errors.append('Projects path configuration missing')
    elif verbose:
        parameters_info.append(('Projects path', env.projects_path))
    if 'code_root' not in env or not env.code_root:
        errors.append('Code root configuration missing')
    elif verbose:
        parameters_info.append(('Code root', env.code_root))
    if 'django_project_root' not in env or not env.django_project_root:
        errors.append('Django project root configuration missing')
    elif verbose:
        parameters_info.append(('Django project root', env.django_project_root))
    if 'django_media_path' not in env or not env.django_media_path:
        errors.append('Django media path configuration missing')
    elif verbose:
        parameters_info.append(('Django media path', env.django_media_path))
    if 'django_static_path' not in env or not env.django_static_path:
        errors.append('Django static path configuration missing')
    elif verbose:
        parameters_info.append(('Django static path', env.django_static_path))
    if 'south_used' not in env:
        errors.append('"south_used" configuration missing')
    elif verbose:
        parameters_info.append(('south_used', env.south_used))
    if 'virtenv' not in env or not env.virtenv:
        errors.append('virtenv configuration missing')
    elif verbose:
        parameters_info.append(('virtenv', env.virtenv))
    if 'virtenv_options' not in env or not env.virtenv_options:
        errors.append('"virtenv_options" configuration missing, you must have at least one option')
    elif verbose:
        parameters_info.append(('virtenv_options', env.virtenv_options))
    if 'ask_confirmation' not in env:
        errors.append('"ask_confirmation" configuration missing')
    elif verbose:
        parameters_info.append(('ask_confirmation', env.ask_confirmation))
    if 'gunicorn_bind' not in env or not env.gunicorn_bind:
        errors.append('"gunicorn_bind" configuration missing')
    elif verbose:
        parameters_info.append(('gunicorn_bind', env.gunicorn_bind))
    if 'gunicorn_logfile' not in env or not env.gunicorn_logfile:
        errors.append('"gunicorn_logfile" configuration missing')
    elif verbose:
        parameters_info.append(('gunicorn_logfile', env.gunicorn_logfile))
    if 'gunicorn_workers' not in env or not env.gunicorn_workers:
        errors.append('"gunicorn_workers" configuration missing, you must have at least one worker')
    elif verbose:
        parameters_info.append(('gunicorn_workers', env.gunicorn_workers))
    if 'gunicorn_worker_class' not in env or not env.gunicorn_worker_class:
        errors.append('"gunicorn_worker_class" configuration missing')
    elif verbose:
        parameters_info.append(('gunicorn_worker_class', env.gunicorn_worker_class))
    if 'gunicorn_loglevel' not in env or not env.gunicorn_loglevel:
        errors.append('"gunicorn_loglevel" configuration missing')
    elif verbose:
        parameters_info.append(('gunicorn_loglevel', env.gunicorn_loglevel))
    if 'nginx_server_name' not in env or not env.nginx_server_name:
        errors.append('"nginx_server_name" configuration missing')
    elif verbose:
        parameters_info.append(('nginx_server_name', env.nginx_server_name))
    if 'supervisorctl' not in env or not env.supervisorctl:
        errors.append('"supervisorctl" configuration missing')
    elif verbose:
        parameters_info.append(('supervisorctl', env.supervisorctl))
    if 'supervisor_autostart' not in env or not env.supervisor_autostart:
        errors.append('"supervisor_autostart" configuration missing')
    elif verbose:
        parameters_info.append(('supervisor_autostart', env.supervisor_autostart))
    if 'supervisor_autorestart' not in env or not env.supervisor_autorestart:
        errors.append('"supervisor_autorestart" configuration missing')
    elif verbose:
        parameters_info.append(('supervisor_autorestart', env.supervisor_autorestart))
    if 'supervisor_redirect_stderr' not in env or not env.supervisor_redirect_stderr:
        errors.append('"supervisor_redirect_stderr" configuration missing')
    elif verbose:
        parameters_info.append(('supervisor_redirect_stderr', env.supervisor_redirect_stderr))
    if 'supervisor_stdout_logfile' not in env or not env.supervisor_stdout_logfile:
        errors.append('"supervisor_stdout_logfile" configuration missing')
    elif verbose:
        parameters_info.append(('supervisor_stdout_logfile', env.supervisor_stdout_logfile))

    if errors:
        if len(errors) == 26:
            ''' all configuration missing '''
            puts('Configuration missing! Please read README.rst first or go ahead at your own risk.')
        else:
            puts('Configuration test revealed %i errors:' % len(errors))
            puts('%s\n\n* %s\n' % ('-' * 37, '\n* '.join(errors)))
            puts('-' * 40)
            puts('Please fix them or go ahead at your own risk.')
        return False
    elif verbose:
        for parameter in parameters_info:
            parameter_formatting = "'%s'" if isinstance(parameter[1], str) else "%s"
            parameter_value = parameter_formatting % parameter[1]
            puts('%s %s' % (parameter[0].ljust(27), green(parameter_value)))
    puts('Configuration tests passed!')
    return True


########################
## END Fagungis tasks ##
########################


def _create_django_user():
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = sudo('useradd -d %(django_user_home)s -m -r %(django_user)s' % env)
        if 'already exists' in res:
            puts('User \'%(django_user)s\' already exists, will not be changed.' % env)
            return
        #  set password
        sudo('passwd %(django_user)s' % env)


def _verify_sudo():
    ''' we just check if the user is sudoers '''
    sudo('cd .')


def _install_nginx():
    # add nginx stable ppa
    sudo('add-apt-repository ppa:nginx/stable')
    sudo('apt-get update')
    sudo('apt-get install nginx')
    sudo('/etc/init.d/nginx start')


def _install_dependencies():
    ''' Ensure those Debian/Ubuntu packages are installed '''
    packages = [
        'mercurial',
        'python-pip',
        'supervisor',
    ]
    sudo('aptitude install %s' % ' '.join(packages))
    _install_nginx()
    sudo('pip install --upgrade pip')


def _install_requirements():
    ''' you must have a file called requirements.txt in your project root'''
    requirements = join(env.code_root, 'requirements.txt')
    virtenvrun('pip install -r %s' % requirements)


def _install_gunicorn():
    """ force gunicorn installation into your virtualenv, even if it's installed globally.
    for more details: https://github.com/benoitc/gunicorn/pull/280 """
    virtenvrun('pip install -I gunicorn')


def _install_virtualenv():
    sudo('pip install virtualenv')


def _create_virtualenv():
    sudo('virtualenv --%s %s' % (' --'.join(env.virtenv_options), env.virtenv))


def _setup_directories():
    sudo('mkdir -p %(projects_path)s' % env)
    sudo('mkdir -p %(django_user_home)s/logs/nginx' % env)
    sudo('mkdir -p %(django_user_home)s/logs/projects' % env)
    sudo('mkdir -p %(django_user_home)s/configs/nginx' % env)
    sudo('mkdir -p %(django_user_home)s/configs/supervisord' % env)
    sudo('mkdir -p %(django_user_home)s/scripts' % env)
    sudo('mkdir -p %(django_user_home)s/htdocs' % env)
    sudo('mkdir -p %(django_user_home)s/tmp' % env)
    sudo('mkdir -p %(virtenv)s' % env)
    sudo('echo "<html><body>nothing here</body></html> " > %(django_user_home)s/htdocs/index.html' % env)


def virtenvrun(command):
    activate = 'source %s/bin/activate' % env.virtenv
    run(activate + ' && ' + command)


def _hg_clone():
    run('hg clone %s %s' % (env.repository, env.code_root))


def _test_nginx_conf():
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = sudo('nginx -t -c /etc/nginx/nginx.conf')
    if 'test failed' in res:
        abort(red_bg('NGINX configuration test failed! Please review your parameters.'))


def _upload_nginx_conf():
    ''' upload nginx conf '''
    nginx_file = '%(django_user_home)s/configs/nginx/%(project)s.conf' % env
    if isfile('conf/nginx.conf'):
        ''' we use user defined nginx.conf template '''
        template = 'conf/nginx.conf'
    else:
        template = '%s/conf/nginx.conf' % fagungis_path
    upload_template(template, nginx_file,
                    context=env, backup=False)
    sudo('ln -sf %s /etc/nginx/sites-enabled/' % nginx_file)
    _test_nginx_conf()
    sudo('nginx -s reload')


def _reload_supervisorctl():
    sudo('%(supervisorctl)s reread' % env)
    sudo('%(supervisorctl)s reload' % env)


def _upload_supervisord_conf():
    ''' upload supervisor conf '''
    supervisord_conf_file = '%(django_user_home)s/configs/supervisord/%(project)s.conf' % env
    if isfile('conf/supervisord.conf'):
        ''' we use user defined supervisord.conf template '''
        template = 'conf/supervisord.conf'
    else:
        template = '%s/conf/supervisord.conf' % fagungis_path
    upload_template(template, supervisord_conf_file,
                    context=env, backup=False)
    sudo('ln -sf %s /etc/supervisor/conf.d/' % supervisord_conf_file)
    _reload_supervisorctl()


def _prepare_django_project():
    with cd(env.django_project_root):
        virtenvrun('./manage.py syncdb --noinput --verbosity=1')
        if env.south_used:
            virtenvrun('./manage.py migrate --noinput --verbosity=1')
        virtenvrun('./manage.py collectstatic --noinput')


def _prepare_media_path():
    sudo('chmod -R 775 %s' % env.django_media_path)


def _upload_rungunicorn_script():
    ''' upload rungunicorn conf '''
    script_file = '%(django_user_home)s/scripts/rungunicorn_%(project)s.sh' % env
    if isfile('scripts/rungunicorn.sh'):
        ''' we use user defined rungunicorn file '''
        template = 'scripts/rungunicorn.sh'
    else:
        template = '%s/scripts/rungunicorn.sh' % fagungis_path
    upload_template(template, script_file,
                    context=env, backup=False)
    sudo('chmod +x %s' % script_file)


def _supervisor_restart():
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = sudo('%(supervisorctl)s restart %(project)s' % env)
    if 'ERROR' in res:
        print red_bg("%s NOT STARTED!" % env.project)
    else:
        print green_bg("%s correctly started!" % env.project)
