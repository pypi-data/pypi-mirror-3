# -*- encoding: utf-8 -*-
from ginsfsm.gobj import GObj
from ghtml.c_ghtml import GHtml

PAGE_TEMPLATE = """\
<%!
from ginsfsm.compat import iteritems_
%>
<!DOCTYPE html>
<!--paulirish.com/2008/conditional-stylesheets-vs-css-hacks-answer-neither/-->
<!--[if lt IE 7]> <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>    <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>    <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <title>${title}</title>

% for key, value in iteritems_(metadata):
    % if value:
    <meta name="${key}" content="${value}">
    % endif
% endfor

    <!-- Mobile viewport optimized: h5bp.com/viewport -->
    <meta name="viewport" content="width=device-width">

% for url in assets_env['css'].urls():
    <link rel="stylesheet" href="${url}"">
% endfor

% for url in assets_env['top_js'].urls():
    <script src="${url}"></script>
% endfor

</head>

<body>
    <!--[if lt IE 8]>
    <div style="border:2px solid red;\
margin:1em; \
padding:1em; \
background-color:#FDD;">
    <strong>Warning</strong>
    <h1>The browser you are using is not standard and is obsolete.</h1>
    <h2>Probably this application will not run correctly.</h2>
    </div>
    <![endif]-->

    ${rendered_childs}

    <!-- JavaScript at the bottom for fast page loading -->
% for url in assets_env['bottom_js'].urls():
    <script src="${url}"></script>
% endfor

</body>
</html>
"""

page_data = {
    'title': 'My Blog',
    'base': 'http://www.myblog.com/',
    'metadata': {
        'application-name': 'My Blog',
        'description': '',
        'keywords': '',
    },
}


class Root(GObj):
    def __init__(self):
        super(Root, self).__init__({})


class Page(GHtml):
    def __init__(self):
        super(Page, self).__init__()

    def render(self, **kw):
        from assets import get_assets_env

        assets_env = get_assets_env(
            self.output_path,
            self.debug,
        )
        kw.update(**page_data)
        kw.update(assets_env=assets_env)
        return super(Page, self).render(**kw)


def get_page(output_path, debug):
    """ This is the only function to be called from blogdegins.
        The rest is up to you.
        This function must return a class with a render method.
        The render method must return a string with the html code.
    """
    gobj_root = Root()
    page = gobj_root.create_gobj(
        None,
        Page,
        gobj_root,
        template=PAGE_TEMPLATE,
    )
    page.output_path = output_path
    page.debug = debug
    from content import get_content
    get_content(page)
    return page
