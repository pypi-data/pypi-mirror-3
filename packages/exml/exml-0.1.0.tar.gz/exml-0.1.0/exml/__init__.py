"""XML Element container and builder.

# Simple stuff
>>> Element("tag")
Element(<tag/>)

>>> Element("node", attr="value", intval=1)
Element(<node attr="value" intval="1"/>)

# "call" element to set children
>>> Element("text")("body")
Element(<text>body</text>)

>>> print Element("nobody", expects=True)(
...     "Spanish Inquisition",
...     " ",
...     Element("not", at="all")
... )
<nobody expects="True">Spanish Inquisition <not at="all"/></nobody>

# List-like append for adding children nodes
>>> list = Element("list")
>>> list.append(Element("item")("lorem"))
>>> list.append(Element("item")("ipsum"))
>>> print list
<list><item>lorem</item><item>ipsum</item></list>

>>> e = Element()
>>> e.node = "test"
>>> e['from'] = "scratch"
>>> e.append("ok")
>>> print e
<test from="scratch">ok</test>

# Some examples from http://www.w3.org/TR/REC-xml-names/#ns-decl
>>> print Element("x", xmlns__edi="http://ecommerce.example.org/schema")('''
...   <!-- the "edi" prefix is bound to http://ecommerce.example.org/schema
...        for the "x" element and contents -->
... ''')
<x xmlns:edi="http://ecommerce.example.org/schema">
  <!-- the "edi" prefix is bound to http://ecommerce.example.org/schema
       for the "x" element and contents -->
</x>

>>> print Element("book", xmlns="urn:loc.gov:books", xmlns__isbn="urn:ISBN:0-395-36341-6")(
...     Element("title")("Cheaper by the Dozen"),
...     Element("isbn:number")("1568491379"))
<book xmlns="urn:loc.gov:books" xmlns:isbn="urn:ISBN:0-395-36341-6"><title>Cheaper by the Dozen</title><isbn:number>1568491379</isbn:number></book>

# Using E the Builder shortcut
>>> E = Builder()
>>> E.use_getattr  # doctest:+ELLIPSIS
<function Element("use_getattr", ...) at 0x...>

>>> print E.tree(x="mas")(
...     E.stump(),
...     E.trunk()(
...         E.branch()(
...            E.ball(color="red"),
...            E.ball(color="gold"),
...         ),
...         E.branch()(
...            E.ball(color="green"),
...         ),
...     ),
...     E.tip()(
...         E.star(points="5")
...     )
... )
<tree x="mas"><stump/><trunk><branch><ball color="red"/><ball color="gold"/></branch><branch><ball color="green"/></branch></trunk><tip><star points="5"/></tip></tree>
"""


class Element(object):
    def __init__(self, node="", **attrs):
        self.node = node
        self.attrs = {}
        for attr, value in attrs.iteritems():
            # apply NS magic
            self[attr] = value
        self.children = None

    @property
    def _attrs(self):
        return ''.join(' %s="%s"' % (key, value) for key, value in sorted(self.attrs.iteritems())) if self.attrs else ""

    @property
    def _children(self):
        return "".join(str(kid) for kid in self.children)

    def __str__(self):
        if self.children is None:
            return "<%s%s/>" % (self.node, self._attrs)
        return "<%s%s>%s</%s>" % (self.node, self._attrs, self._children, self.node)

    def __repr__(self):
        return 'Element(%s)' % str(self)

    def __getitem__(self, key):
        return self.attrs[key]

    def __setitem__(self, key, value):
        self.attrs[key.replace('__', ':')] = value

    def __call__(self, *children):
        self.children = children
        return self

    def append(self, value):
        if self.children is None:
            self.children = []
        self.children.append(value)


class Builder(object):
    def __getattr__(self, node):
        def builder(*args, **kwargs):
            return Element(node, *args, **kwargs)
        builder.func_name = 'Element("%s", ...)' % node
        return builder

E = Builder()
