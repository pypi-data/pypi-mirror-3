# -*- encoding: utf-8 -*-
"""
Utility for creating static html code.
"""

import argparse
import sys
import os.path
import shutil

import envoy

try:  # pragma: no cover
    from ConfigParser import ConfigParser
except:  # pragma: no cover
    from configparser import ConfigParser

import logging
logging.basicConfig(level=logging.DEBUG)

from blogdegins.getyesno import getyesno

BLOGDEGINS_INI = 'blogdegins.ini'

comandos = ['init', 'skeleton', 'render', 'page', 'widget', 'rsync']


def get_python_page_code(Content, content, is_widget=False):
    if is_widget:
        widget_path = os.path.join('widgets', content, '')
    else:
        widget_path = ''

    python_page_code = """# -*- encoding: utf-8 -*-
from ghtml.c_ghtml import GHtml

{content}_data = {{
    'myname': 'Blogdegins.',
}}


class {Content}(GHtml):
    def __init__(self, fsm=None, gconfig=None):
        super({Content}, self).__init__(fsm=fsm, gconfig=gconfig)

    def render(self, **kw):
        kw.update(**{content}_data)
        return super({Content}, self).render(**kw)


def create_{content}(parent):
    {content} = parent.create_gobj(
        None,
        {Content},
        parent,
        template='{widget_path}{content}.mako',
    )
    return {content}

""".format(Content=Content, content=content, widget_path=widget_path)
    return python_page_code


mako_page_code = ""

javascript_page_code = """jQuery(function($) {
    // Your code using failsafe $ alias here...

    $(function() {
        // Document is ready
    });

});
"""

scss_page_code = ""


def main(argv=sys.argv):
    command = Blogdegins(argv)
    return command.run()


class Blogdegins(object):
    description = 'Generate static html code.'
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "command",
        choices=comandos,
        help="Available commands:\n"
"init {project} ==> create a .ini file and the directory structure.\n"
"skeleton ==> create a new tag directory, copying a assets directory.\n"
"render ==> generate a new index.html, in tags/{version} directory.\n"
"page {name} ==> creat a new set of py/js/mako/scss files in main directory.\n"
"widget {name} ==> creat a new wigdet directory"
    " with their set of py/js/mako/scss files in the widgets directory\n"
"rsync ==> syncronize the tag version with the remote host.\n"
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
        """ create a .ini file and the directory structure
        """
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
        shutil.copytree(src_path, dst_path, symlinks=True)

        src_path = self.code_dir()
        dst_path = os.path.join(output_dir, 'htmlrendercode')
        shutil.copytree(
            src_path,
            dst_path,
            ignore=shutil.ignore_patterns('*.pyc', '*~'),
            symlinks=True,
        )
        dst_path = os.path.join(output_dir, 'htmlrendercode', 'wid')


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

        util_names = os.listdir(self.utils_dir())
        for name in util_names:
            srcname = os.path.join(self.utils_dir(), name)
            shutil.copy2(srcname, output_dir)

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

    def utils_dir(self):
        return os.path.join(self.module_dir(), "utils")

    def current_tag_dir(self):
        return os.path.join(
            self.config.here,
            'tags',
            self.config.current_tag,
        )

    def skeleton(self):
        """ create a new tag directory, copying a assets directory
        """
        print('====> skeleton')
        dst_path = self.current_tag_dir()

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
        shutil.copytree(
            src_path,
            dst_path,
            symlinks=True,
        )

        # creat links of current pages/widgets ???
        rendercode_path = os.path.join(
            self.config.here,
            'htmlrendercode',
        )

        return 0

    def widget(self):
        """ creat a new widget directory
        with their set of py/js/mako/scss files in the widgets directory
        """
        print('====> widget')
        if not self.args.arguments:
            print('<---- * You must supply a name!')
            return 2
        name = self.args.arguments[0].lower()
        Name = name.capitalize()
        self._make_set(
            name,
            get_python_page_code(Name, name, True),
            mako_page_code,
            javascript_page_code,
            scss_page_code,
            True
        )

    def page(self):
        """ creat a new set of py/js/mako/scss files in the main directory
        """
        print('====> page')
        if not self.args.arguments:
            print('<---- * You must supply a name!')
            return 2
        name = self.args.arguments[0].lower()
        Name = name.capitalize()
        self._make_set(
            name,
            get_python_page_code(Name, name),
            mako_page_code,
            javascript_page_code,
            scss_page_code,
        )

    def _make_set(self,
            name,
            python_page_code,
            mako_page_code,
            javascript_page_code,
            scss_page_code,
            is_widget=False,
        ):
        if not is_widget:
            rendercode_path = os.path.join(
                self.config.here,
                'htmlrendercode',
            )
        else:
            rendercode_path = os.path.join(
                self.config.here,
                'htmlrendercode',
                'widgets',
                name,
            )

        if not os.path.exists(self.current_tag_dir()):
            print('<---- * First you must create a tag skeleton.')
            exit(2)

        py_file = '%s.py' % name
        js_file = '%s.js' % name
        scss_file = '%s.scss' % name
        mako_file = '%s.mako' % name

        widget_path = os.path.join(rendercode_path)
        if not os.path.exists(widget_path):
            os.mkdir(widget_path)
        filename = os.path.join(rendercode_path, '__init__.py')
        if not os.path.exists(filename):
            fd = open(filename, 'w')
            fd.write('')
            fd.close()

        ## Python
        filename = os.path.join(rendercode_path, py_file)
        if not os.path.exists(filename):
            print('<---- * Creating "%s" file.' % (filename))
            fd = open(filename, 'w')
            fd.write(python_page_code)
            fd.close()

        ## Mako
        filename = os.path.join(rendercode_path, mako_file)
        if not os.path.exists(filename):
            print('<---- * Creating "%s" file.' % (filename))
            fd = open(filename, 'w')
            fd.write(mako_page_code)
            fd.close()

        ## Javascript
        filename = os.path.join(rendercode_path, js_file)
        if not os.path.exists(filename):
            print('<---- * Creating "%s" file.' % (filename))
            fd = open(filename, 'w')
            fd.write(javascript_page_code)
            fd.close()

        ## Scss
        filename = os.path.join(rendercode_path, scss_file)
        if not os.path.exists(filename):
            print('<---- * Creating "%s" file.' % (filename))
            fd = open(filename, 'w')
            fd.write(scss_page_code)
            fd.close()

        ## js symbolic link
        if not is_widget:
            ln_path = os.path.join(
                self.current_tag_dir(),
                'static',
                'js',
                'bottom',
                'app',
            )
        else:
            ln_path = os.path.join(
                self.current_tag_dir(),
                'static',
                'js',
                'bottom',
                'widgets',
            )
        os.chdir(ln_path)
        if not is_widget:
            source_file = '../../../../../../htmlrendercode/%s' % js_file
        else:
            source_file = '../../../../../../htmlrendercode/widgets/%s/%s' % (
                name,
                js_file
            )
        link_name = js_file
        try:
            os.symlink(source_file, link_name)
            print('<---- * Creating "%s" symbolic link.' % (
                ln_path + '/' + link_name))
            msg = """Remember to add to bottom_js_content[] list (assets.py) \
the line:
    'js/bottom/%s/%s.js'""" % (
                'app' if not is_widget else 'widgets',
                name,
            )
            print(msg)
        except OSError:
            pass

        ## scss symbolic link
        if not is_widget:
            ln_path = os.path.join(
                self.current_tag_dir(),
                'static',
                'css',
                'app',
            )
        else:
            ln_path = os.path.join(
                self.current_tag_dir(),
                'static',
                'css',
                'widgets',
            )
        os.chdir(ln_path)
        if not is_widget:
            source_file = '../../../../../htmlrendercode/%s' % scss_file
        else:
            source_file = '../../../../../htmlrendercode/widgets/%s/%s' % (
                name,
                scss_file,
            )
        link_name = scss_file
        try:
            os.symlink(source_file, link_name)
            print('<---- * Creating "%s" symbolic link.' % (
                ln_path + '/' + link_name))
            msg = """Remember to add to scss_content[] list (assets.py) \
the line:
    'css/%s/%s.scss'""" % (
                'app' if not is_widget else 'widgets',
                name
            )
            print(msg)
        except OSError:
            pass

        return 0

    def render(self):
        """ generate a new index.html, in tags/{version} directory
        Blogdegins will render using next call code:

        get_page(code_path, output_path, debug)
            is the only function being called from blogdegins.
            The rest is up to you.
            This function must return a class with a `render` method.
            The `render` method must return a string with the html code.
            :param code_path: path where python and templates code reside.
            :param output_path: current output tag directory.
            :param debug: True if you want debug.
        """
        if self.args.verbose:
            print('====> render')
        output_path = self.current_tag_dir()
        if not os.path.exists(output_path):
            print('<---- * First you must create a tag skeleton.')
            exit(2)

        code_path = os.path.join(
            self.config.here,
            'htmlrendercode',
        )
        sys.path.append(code_path)
        os.chdir(self.config.here)
        from page import get_page
        page = get_page(code_path, output_path, self.args.debug)
        html = page.render()
        if self.args.verbose:
            print(html)

        index_html = os.path.join(output_path, 'index.html')
        fd = open(index_html, 'w')
        fd.write(html)
        fd.close()
        return 0

    def rsync(self):
        """ syncronize the tag version with the remote host
        """
        print('====> rsync')
        src_path = os.path.join(self.current_tag_dir(), '')
        remote = self.config.get(self.config.current_tag, 'remote-server')
        if not remote:
            print('<---- * Please specify a remote server path.')
            exit(2)

        command = 'rsync -avz --delete ' \
            '--exclude \.webassets-cache --exclude \.cache %s %s' % (
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
