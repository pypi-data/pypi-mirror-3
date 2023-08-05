import optparse
import sys
import os

from eggspacker import EggsPacker

parser = optparse.OptionParser('%prog [options] pkgname [pkgname [pkgname...]]')

parser.add_option('-i', '--index', dest='index',
                  default='http://pypi.python.org/simple/',
                  help=u'A Pypi compatible index URL. Default to pypi')
parser.add_option('-t', '--targetdir', dest='targetdir', default='basket',
                  help=u'Target directory. Default: "basket".')
parser.add_option('--python-version', dest='python_version',
                  default='%s.%s' % sys.version_info[0:2],
                  help=u'Target python version.')
parser.add_option('--platform', dest='platform',
                  help=u'Target platform')
parser.add_option('--unzip', action='append', dest='unzip',
                  default=[],
                  help=u'Unzip the asked egg if present in the dependencies. '
                       u'The special value "auto" will guess what to do '
                       u'with with not-zip-safe flag, and "all" will force '
                       u'unzipping of all the eggs. Can be specified several times.')

def main():
    options, args = parser.parse_args()

    if len(args) < 1:
        parser.error("Missing arguments")

    if not os.path.exists(options.targetdir):
        os.mkdir(options.targetdir)

    packer = EggsPacker(
        index=options.index,
        basket=options.targetdir,
        python=options.python_version,
        platform=options.platform,
        unzip=options.unzip)

    for egg in args:
        packer.pack(egg)
