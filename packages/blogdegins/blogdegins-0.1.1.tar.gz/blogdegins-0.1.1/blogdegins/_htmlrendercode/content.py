# -*- encoding: utf-8 -*-
from ghtml.c_ghtml import GHtml

CONTENT_TEMPLATE = """\
Hi world! I'm ${myname}! ;-)
"""

content_data = {
    'myname': 'Blogdegins.',
}


class Content(GHtml):
    def __init__(self):
        super(Content, self).__init__()

    def render(self, **kw):
        kw.update(**content_data)
        return super(Content, self).render(**kw)


def get_content(page):
    page.create_gobj(
        None,
        Content,
        page,
        template=CONTENT_TEMPLATE,
    )
    return page
