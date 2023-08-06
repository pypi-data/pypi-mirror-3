# -*- encoding: utf-8 -*-
"""
Utility for creating static html code.
"""

import argparse
import sys
import os.path
import shutil
import imp

import envoy

try:  # pragma: no cover
    from ConfigParser import ConfigParser
except:  # pragma: no cover
    from configparser import ConfigParser

import logging
logging.basicConfig(level=logging.DEBUG)

from blogdegins.getyesno import getyesno

BLOGDEGINS_INI = 'blogdegins.ini'

comandos = ['init', 'skeleton', 'render', 'rsync']


def main(argv=sys.argv):
    command = Blogdegins(argv)
    return command.run()


class Blogdegins(object):
    description = 'Generate static html code.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "command",
        choices=comandos,
        help="Available commands ==> "
            "init {project}: create a .ini file and the directory structure."
            "skeleton: create a new tag directory, copying a assets directory."
            "render: generate a new index.html, in tags/{version} directory."
            "tag: generate a new tag version in the tags directory."
            "rsync: syncronize the tag version with the remote host."
    )
    parser.add_argument(
        "arguments",
        nargs=argparse.REMAINDER,
        help="Arguments to command."
    )
    parser.add_argument(
        '-d',
        '--debug',
        dest='debug',
        action='store_true',
        help="True if render in development mode, False in production mode.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase output verbosity",
        action='store_true',
    )

    def __init__(self, argv=sys.argv):
        self.args = self.parser.parse_args(argv[1:])
        if self.args.debug:
            self.args.verbose = True

    def run(self):
        cmd = self.args.command
        fn = getattr(self, cmd)
        if cmd != 'init':
            self.load_ini()

        return fn()

    def init(self):
        print('====> init')
        if not self.args.arguments:
            print('<---- * You must supply a project name!')
            return 2
        project = self.args.arguments[0]
        output_dir = os.path.abspath(os.path.normpath(project))
        if os.path.exists(output_dir):
            print('<---- * Directory "%s" already exists!' % (output_dir))
            return 2
        else:
            print('<---- * Creating blogdegins project in "%s".' % output_dir)
        os.mkdir(output_dir)

        src_path = self.assets_dir()
        dst_path = os.path.join(output_dir, 'assets')
        shutil.copytree(src_path, dst_path)

        src_path = self.code_dir()
        dst_path = os.path.join(output_dir, 'htmlrendercode')
        shutil.copytree(
            src_path,
            dst_path,
            ignore=shutil.ignore_patterns('*.pyc')
        )

        os.mkdir(os.path.join(output_dir, 'tags'))
        current_tag = '0.00.aa'
        config = ConfigParser()
        config.set('DEFAULT', 'current_tag', current_tag)
        config.add_section('tags')
        config.set('tags', current_tag, '')
        config.add_section(current_tag)
        config.set(
            current_tag,
            'assets',
            os.path.join('assets', 'h5bp+jquery'),
        )
        config.set(
            current_tag,
            'remote-server',
            '',
        )

        ini_file = os.path.join(output_dir, BLOGDEGINS_INI)
        with open(ini_file, 'w') as configfile:
            config.write(configfile)

        return 0

    def load_ini(self):
        if not os.path.exists(BLOGDEGINS_INI):
            print('File "%s" NOT found.' % (BLOGDEGINS_INI))
            exit(2)
        # 'here' is the directory of the .ini file
        here = os.path.dirname(os.path.abspath(BLOGDEGINS_INI))
        self.config = ConfigParser({'here': here})
        self.config.read(BLOGDEGINS_INI)
        self.config.here = here
        self.config.current_tag = self.config.get('DEFAULT', 'current_tag')

    def module_dir(self):
        mod = sys.modules[self.__class__.__module__]
        return os.path.dirname(mod.__file__)

    def assets_dir(self):
        return os.path.join(self.module_dir(), "assets")

    def code_dir(self):
        return os.path.join(self.module_dir(), "_htmlrendercode")

    def skeleton(self):
        print('====> skeleton')
        dst_path = os.path.join(
            self.config.here,
            'tags',
            self.config.current_tag,
        )

        if not os.path.exists(dst_path):
            print('<---- * Creating "%s" directory.' % (dst_path))
        else:
            resp = getyesno(
                'You are re-creating the skeleton "%s".\n'
                'You will loose your data! Are you sure?' % dst_path,
                default='n',
            )
            if not resp:
                print('<---- * Operation aborted.')
                return 2
            print('<---- * Re-creating "%s" directory.' % (dst_path))
            shutil.rmtree(dst_path)

        assets = self.config.get(self.config.current_tag, 'assets')
        src_path = os.path.join(
            self.config.here,
            assets,
        )
        shutil.copytree(src_path, dst_path)
        return 0

    def render(self):
        #todo: check if skeleton is created.
        if self.args.verbose:
            print('====> render')
        dst_path = os.path.join(
            self.config.here,
            'tags',
            self.config.current_tag,
        )
        if not os.path.exists(dst_path):
            print('<---- * First you must create a tag skeleton.')
            exit(2)

        code_path = os.path.join(
            self.config.here,
            'htmlrendercode',
        )
        sys.path.append(code_path)
        os.chdir(self.config.here)
        from page import get_page
        page = get_page(dst_path, self.args.debug)
        html = page.render()
        if self.args.verbose:
            print(html)

        index_html = os.path.join(dst_path, 'index.html')
        fd = open(index_html, 'w')
        fd.write(html)
        fd.close()
        return 0

    def rsync(self):
        print('====> rsync')
        src_path = os.path.join(
            self.config.here,
            'tags',
            self.config.current_tag,
            ''
        )
        remote = self.config.get(self.config.current_tag, 'remote-server')
        if not remote:
            print('<---- * Please specify a remote server path.')
            exit(2)

        command = 'rsync -avz --delete %s %s' % (
            src_path,
            remote,
        )
        if self.args.verbose:
            print(command)
        response = envoy.run(command)
        print(response.std_out)

        return 0


if __name__ == '__main__':
    main()
