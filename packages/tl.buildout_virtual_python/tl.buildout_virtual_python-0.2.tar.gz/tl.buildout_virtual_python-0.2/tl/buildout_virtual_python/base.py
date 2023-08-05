# Copyright (c) 2007-2012 Thomas Lotze
# See also LICENSE.txt

"""zc.buildout recipe for creating a virtual Python installation
"""

from os.path import join
import hashlib
import logging
import os
import os.path
import pkg_resources
import shutil
import subprocess
import sys
import tempfile
import virtualenv


class Recipe(object):
    """zc.buildout recipe for creating a virtual Python installation

    Configuration options:
        executable-name
        interpreter
        real-python
        site-packages
        eggs
        extra-paths

    Exported options:
        location
        executable
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        # set some defaults
        options.setdefault("executable-name", "python")
        options.setdefault("real-python", sys.executable)
        options.setdefault("site-packages", "false")
        options.setdefault("extra-paths", "")

        # Create the egg recipe instance now to let it initialize the options.
        self.egg = pkg_resources.load_entry_point(
            "zc.recipe.egg", "zc.buildout", "eggs")(buildout, name, options)

        # export some options
        options["location"] = join(
            buildout["buildout"]["parts-directory"], name)

        (self.python_home, self.python_lib,
         self.python_inc, self.python_bin) = (
            virtualenv.path_locations(options['location']))

        options["executable"] = join(
            self.python_bin, options['executable-name'])

        # explore the real Python, store fingerprint
        py_sig = hashlib.md5()
        py_sig.update(open(options['real-python']).read())
        options['__python-signature__'] = py_sig.hexdigest()

    def install(self):
        options = self.options
        items = [options['location']]

        # Since we want the real executable to be configurable, we need to
        # create the virtual environment by calling the real executable on a
        # script instead of calling into virtualenv in-process.
        venv_path = self.create_venv_script()
        executable = self.call_venv_script(venv_path)
        os.unlink(venv_path)

        # Install any additional eggs and extra paths into the virtual env.
        site_packages = join(self.python_lib, "site-packages")
        lines = []
        if options.get("eggs"):
            ignored, working_set = self.egg.working_set(())
            lines.extend(spec.location for spec in working_set)
        lines.extend(line.strip()
                     for line in options["extra-paths"].splitlines())
        if lines:
            pth = open(join(site_packages, "virtual-python.pth"), "w")
            pth.writelines(line + "\n" for line in lines)
            pth.close()

        # make sure the executable is available under the requested name
        if not os.path.exists(options['executable']):
            shutil.copy(executable, options['executable'])

        # make the interpreter available in buildout's bin directory if desired
        if 'interpreter' in options:
            interpreter = join(self.buildout['buildout']['bin-directory'],
                               options['interpreter'])
            if os.path.lexists(interpreter):
                os.remove(interpreter)
            os.symlink(executable, interpreter)
            items.append(interpreter)

        return items

    def update(self):
        pass

    def create_venv_script(self):
        # The egg located here may not correspond to the Python version being
        # virtualized. This should not be a problem, though.
        virtualenv_dist = pkg_resources.working_set.find(
            pkg_resources.Requirement.parse('virtualenv'))
        _, venv_path = tempfile.mkstemp()
        venv = open(venv_path, 'w')
        venv.write(VENV_TEMPLATE % dict(
                virtualenv_location=virtualenv_dist.location,
                home_dir=self.python_home,
                lib_dir=self.python_lib,
                inc_dir=self.python_inc,
                bin_dir=self.python_bin,
                site_packages=boolean(self.options['site-packages']),
                ))
        venv.close()
        return venv_path

    def call_venv_script(self, venv_path):
        # Call the script with PYTHONPATH removed from the environment since
        # virtualenv would choke on buildout's custom site.py.
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        real_executable = self.options['real-python']
        executable, err = subprocess.Popen(
            [real_executable, venv_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env).communicate()
        executable = executable.strip()
        if not executable:
            logger = logging.getLogger(self.name)
            logger.debug('While installing virtual Python:\n\n' + err)
            logger.info('You may want to check the used versions of '
                        'zc.buildout and virtualenv for compatibility.')
            raise ValueError(
                'An error occurred while calling virtualenv with %r.'
                'Run buildout with the -v option to see more details.' %
                real_executable)
        # sanity check
        assert os.path.dirname(executable) == self.python_bin
        return executable


def boolean(value):
    return value.lower() in (1, "yes", "true", "on")


VENV_TEMPLATE = """\
import sys
sys.path.insert(0, %(virtualenv_location)r)
import virtualenv
import logging
virtualenv.logger = virtualenv.Logger([(logging.DEBUG, sys.stderr)])
print virtualenv.install_python(
    %(home_dir)r, %(lib_dir)r, %(inc_dir)r, %(bin_dir)r,
    site_packages=%(site_packages)r, clear=True)
"""
