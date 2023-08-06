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
        node = node.replace('__', ':')
        def builder(*args, **kwargs):
            return Element(node, *args, **kwargs)
        builder.func_name = 'Element("%s", ...)' % node
        return builder

E = Builder()
