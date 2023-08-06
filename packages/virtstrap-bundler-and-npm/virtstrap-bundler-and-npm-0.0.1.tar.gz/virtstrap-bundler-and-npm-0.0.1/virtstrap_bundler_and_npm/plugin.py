import os
from contextlib import contextmanager
from subprocess import Popen

from virtstrap import hooks
from virtstrap.utils import in_directory


@hooks.create('install', ['after'])
def install_ruby_and_nodejs_dependencies(event, options, project=None, **kwargs):
    project_path = project.path()
    project_binpath = project.bin_path()

    # ensure we're in the project's root directory
    with in_directory(project_path):
        print '\n=> Installing ruby gems...'
        Popen(['bundle', 'install', '--binstubs=%s' % project_binpath]).communicate()

        print '\n=> Installing nodejs dependencies...'
        Popen(['npm', 'install']).communicate()

        print '\n=> Adding nodejs tools to %s...' % project_binpath
        nodejs_tools = os.path.join(project_path, 'node_modules', '.bin', '*')
        Popen('ln -s %s %s' % (nodejs_tools, project_binpath), shell=True).communicate()
