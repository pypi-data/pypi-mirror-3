from fanstatic.core import register_inclusion_renderer
from fanstatic import Library, Resource
from os.path import isfile
from os.path import join
import subprocess
import shutil
import os


def render_less(url):
    if url.endswith('.css'):
        return ('<link rel="stylesheet" type="text/css" href="%s" />' % url)
    else:
        return ('<link rel="stylesheet" type="text/x-less" href="%s" />' % url)

register_inclusion_renderer('.less', render_less, 25)

library = Library('less', 'resources')

lesscss_js = Resource(library, 'less.min.js', bottom=True)
lesscss = lesscss_js


class LessResource(Resource):

    def __init__(self, library, relpath, **kwargs):
        fullpath = join(library.path, relpath)
        if 'LESSC' in os.environ:
            lessc(fullpath)
            depends = kwargs.get('depends', [])
            if lesscss_js not in depends:
                depends.insert(0, lesscss_js)
            kwargs['depends'] = depends
            kwargs['debug'] = relpath
        else:
            # avoid failure
            fullpath += '.min.css'
            if not isfile(fullpath):
                fd = open(fullpath, 'w')
                fd.write('// Not compiled yet\n')
                fd.write('// set the LESSC environ variable ')
                fd.write(
                    'to a valid lessc binary and relaunch your application\n')
                fd.close()
        relpath += '.min.css'
        super(LessResource, self).__init__(library, relpath, **kwargs)


def lessc(in_path, *args):

    lessc = None
    if 'LESSC' in os.environ:
        lessc = os.path.abspath(os.environ['LESSC'])
    if lessc is None or not isfile(lessc):
        for path in ('bin/lessc', '/usr/bin/lessc', '/usr/local/bin/lessc'):
            if isfile(path):
                lessc = path
                break
    if lessc is None or not isfile(lessc):
        for path in (('node_modules', os.path.expanduser('~/.node_modules'))):
            path = os.path.join(path, 'less', 'bin', 'lessc')
            if isfile(path):
                lessc = path
                break
    if not lessc:
        lessc = 'lessc'

    args = list(args)
    if not args:
        args = ['-x']

    if 'LESSC_ARGS' in os.environ:
        args = set(args.extend(os.environ['LESSC_ARGS'].split()))

    cmd = [lessc] + list(args) + [in_path]
    env = os.environ.copy()

    # avoid a bug if you're using gp.recipe.node
    del env['PYTHONPATH']

    p = subprocess.Popen(cmd,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         env=env)
    p.wait()

    err = p.stderr.read()
    if err.strip():
        msg = 'Error while compiling %s:\n%s' % (in_path, err)
        raise RuntimeError(msg)

    out_path = in_path + '.min.css'
    fd = open(out_path, 'w')
    shutil.copyfileobj(p.stdout, fd)
    fd.close()
    return out_path


def main():
    from optparse import OptionParser
    parser = OptionParser()
    options, args = parser.parse_args()

    if not args:
        args = ['.']

    for arg in args:
        if os.path.isfile(arg):
            filename = os.path.abspath(arg)
            if filename.endswith('.less'):
                in_path = filename
                out_path = lessc(in_path, '-x')
                print in_path, '->', out_path
        else:
            for root, dirnames, filenames in os.walk(arg):
                for filename in filenames:
                    if filename.endswith('.less'):
                        in_path = os.path.join(root, filename)
                        print in_path
                        out_path = lessc(in_path, '-x')
                        print in_path, '->', out_path
