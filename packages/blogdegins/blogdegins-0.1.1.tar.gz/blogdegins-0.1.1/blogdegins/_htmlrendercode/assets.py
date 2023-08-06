# -*- encoding: utf-8 -*-
import os.path
from webassets import Environment, Bundle

css_content = [
    'css/normalize.css',
]
top_js_content = [
    'js/top/modernizr.js',      # must be in first place
]
bottom_js_content = [
    'js/bottom/h5bp-log.js',    # must be in first place
    'js/bottom/jquery/jquery.js',
]


def get_assets_env(output_path, debug=False):
    """ The directory structure of assets is:
        output_path
            static
                css
                js
    """
    output_path = os.path.join(output_path, 'static')
    assets_env = Environment(output_path, 'static', debug=debug)

    css = Bundle(
        *css_content,
        #filters='yui_js',
        output='css/packed.css'
    )
    assets_env.register('css', css)

    top_js = Bundle(
        *top_js_content,
        #filters='yui_js',
        output='js/top.js'
    )
    assets_env.register('top_js', top_js)

    bottom_js = Bundle(
        *bottom_js_content,
        filters='yui_js',
        output='js/bottom.js'
    )
    assets_env.register('bottom_js', bottom_js)

    return assets_env
