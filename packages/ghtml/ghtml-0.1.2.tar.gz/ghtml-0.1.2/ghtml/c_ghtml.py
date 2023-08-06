# -*- encoding: utf-8 -*-
""" GHtml GObj
A gobj that generates html.

.. autoclass:: GHtml
    :members: start_up

"""
import os.path
from mako.template import Template
from mako.runtime import Context

from ginsfsm.gobj import (
    GObj,
)

from ginsfsm.compat import (
    NativeIO,
    tostr,
    iteritems_,
)
from ginsfsm.gconfig import add_gconfig

void_elements = [
    'area',
    'base',
    'br',
    'col',
    'command',
    'embed',
    'hr',
    'img',
    'input',
    'keygen',
    'link',
    'meta',
    'param',
    'source',
    'track',
    'wbr',
]

# Supported attributes.
GHTML_GCONFIG = {
    'debug': [bool, False, 0, None, 'Debugging mode'],
    'template': [str, '', 0, None, "Template name."],

    'tag': [str, '', 0, None, "The element type."],
    'attrib': [dict, {}, 0, None,
        "A dictionary containing the element's attributes."
    ],
    'text': [str, '', 0, None, "Data associated with the element."],
}


class GHtml(GObj):
    """ GObj that generates html in XML syntax.

    :param fsm: FSM `simple-machine`.
    :param gconfig: GCONFIG `gconfig-template`.

    .. ginsfsm::
       :fsm: GHTML_FSM
       :gconfig: GHTML_GCONFIG


    """
    def __init__(self, fsm=None, gconfig=None):
        gconfig = add_gconfig(gconfig, GHTML_GCONFIG)
        if fsm is None:
            fsm = {}
        super(GHtml, self).__init__(fsm, gconfig)

    def start_up(self):
        """ Initialization zone.
        """

    def _write_attribs(self, buf):
        for key, value in iteritems_(self.attrib):
            buf.write(' %s="%s"' % (key, value))

    def _render_template(self, buf, mako_lookup, **kw):
        if mako_lookup:
            template = mako_lookup.get_template(self.template)
        else:
            template = Template(
                self.template,
                strict_undefined=True,
            )
        ctx = Context(buf, **kw)
        template.render_context(ctx)

    def render(self, buf=None, mako_lookup=None, **kw):
        buf_is_mine = False
        if buf is None:
            buf = NativeIO()
            buf_is_mine = True

        if self.tag:
            buf.write('<%s' % self.tag)
            self._write_attribs(buf)
            buf.write('>')

            if not self.tag in void_elements:
                # by the moment, the order is: self.text, template, childs
                if self.text:
                    buf.write(self.text)
                if self.template:
                    self._render_template(
                        buf,
                        mako_lookup,
                        **kw
                    )
                for child in self:
                    child.render(buf=buf, mako_lookup=mako_lookup, **kw)
            buf.write('</%s>' % self.tag)

        elif self.template:
            childs_buf = NativeIO()
            for child in self:
                child.render(buf=childs_buf, mako_lookup=mako_lookup, **kw)
            s = childs_buf.getvalue()
            rendered_childs = tostr(s)
            childs_buf.close()
            kw.update(rendered_childs=rendered_childs)
            self._render_template(buf, mako_lookup, **kw)

        s = buf.getvalue()
        s = tostr(s)
        if buf_is_mine:
            buf.close()
        return s
