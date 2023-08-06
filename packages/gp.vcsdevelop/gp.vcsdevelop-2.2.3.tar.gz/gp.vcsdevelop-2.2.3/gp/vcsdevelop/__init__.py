import zc.buildout
import subprocess
import shutil
import base64
import zlib
import glob
import sys
import re
import os


def initialize_pip():
    from gp.vcsdevelop import get_pip
    if sys.version_info >= (3,0):
        import pickle
        sources = get_pip.sources.encode("ascii") # ensure bytes
        sources = pickle.loads(zlib.decompress(base64.decodebytes(sources)))
    else:
        import cPickle as pickle
        sources = pickle.loads(zlib.decompress(base64.decodestring(get_pip.sources)))
    temp_dir = get_pip.unpack(sources)
    sys.path.insert(0, temp_dir)

    import pip, pip.index, pip.req, pip.vcs

    pip.version_control()
    pip.logger.consumers.append((pip.logger.INFO, sys.stdout))
    schemes = pip.vcs.vcs.schemes[:]
    if 'svn' not in schemes:
        schemes.append('svn')

    shutil.rmtree(temp_dir)
    return pip.req, pip.index, schemes

def asbool(buildout, name, default='true'):
    value = buildout['buildout'].get(name, default)
    value = value.lower()
    if value == 'false':
        return False
    return value

def has_setup(dirname):
    filename = os.path.join(dirname, 'setup.py')
    if os.path.isfile(filename):
        return filename
    return False

def popen(args, dirname=None):
    cwd = os.getcwd()
    if dirname:
        os.chdir(dirname)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    print(p.stdout.read())
    os.chdir(cwd)

class Options(object):
    skip_requirements_regex = False
    default_vcs = None

def install(buildout=None):

    pip_req, pip_index, schemes = initialize_pip()

    offline = asbool(buildout, 'offline', 'false')
    newest = asbool(buildout, 'newest', 'false')
    update = asbool(buildout, 'vcsdevelop-update', 'false')
    if not update:
        update = asbool(buildout, 'vcs-update', 'false')
    else:
        print('Warning: vcsdevelop-update option has been renamed to vcs-update')

    develop_dir = buildout['buildout'].get('develop-dir', os.getcwd())
    if develop_dir.startswith('~'):
        develop_dir = os.path.expanduser(develop_dir)

    if not os.path.isdir(develop_dir):
        os.makedirs(develop_dir)

    develop = buildout['buildout'].get('develop', '')
    develop = [d.strip() for d in develop.split('\n') if d.strip()]

    vcs_extend = buildout['buildout'].get('vcs-extend-develop', '')
    vcs_extend = [d.strip() for d in vcs_extend.split('\n') if d.strip()]

    requirements_eggs = []
    requirements = buildout['buildout'].get('requirements', '').split('\n')
    for filename in [req for req in requirements if req]:
        finder = pip_index.PackageFinder(
                find_links=buildout['buildout'].get('find-links', '').split('\n'),
                index_urls=[buildout['buildout'].get('index', 'http://pypi.python.org/simple')])
        for req in pip_req.parse_requirements(filename, finder=finder, options=Options()):
            if req.url:
                vcs_extend.append(req.url)
                if req.name:
                    requirements_eggs.append(req.name)
                else:
                    name, dummy = pip_req.parse_editable(req.url)
                    requirements_eggs.append(name)
            elif req.name:
                requirements_eggs.append(str(req.req))


    if vcs_extend:
        for url in vcs_extend:
            package, dummy = pip_req.parse_editable(url)
            if not [p for p in develop if p.endswith(package)]:
                develop.append(url)
            else:
                print(('Skipping %r. Package is already in the develop option' % url))

    new_develop = []
    for url in develop:
        if '+' in url and len([s for s in schemes if url.startswith(s+'+')]):
            package, dummy = pip_req.parse_editable(url)
            source_dir = os.path.join(develop_dir, package.strip())
            if os.path.isdir(source_dir) and (not offline and update == 'always'):
                print(('Removing %s' % source_dir))
                shutil.rmtree(source_dir)
            if not os.path.isdir(source_dir) or update:
                if not offline:
                    req = pip_req.InstallRequirement.from_editable(url)
                    req.source_dir = source_dir
                    req.update_editable()
                    if os.path.isfile(os.path.join(source_dir, '.gitmodules')):
                        popen(['git', 'submodule', 'init'], dirname=source_dir)
                        popen(['git', 'submodule', 'update'], dirname=source_dir)
            if has_setup(source_dir):
                new_develop.append(source_dir)
            else:
                print(('Warning: %s is not a python package' % source_dir))
        else:
            new_develop.append(os.path.abspath(url))

    if len(new_develop):
        package_names = []
        for package in new_develop:
            filename = has_setup(package)
            if filename:
                req = pip_req.InstallRequirement.from_line(package)
                if req.name:
                    package_names.append(req.name)
        buildout['buildout']['develop-eggs'] = '\n'.join(package_names)
        buildout['buildout']['develop'] = '\n'.join(new_develop)

    if len(requirements_eggs):
        buildout['buildout']['requirements-eggs'] = '\n'.join(requirements_eggs)
