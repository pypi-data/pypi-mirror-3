refs = {}

class Introspectable(object):
    def __init__(self, category, title, detail, discriminator=None):
        self.category = category
        self.title = title
        self.detail = detail
        self.discriminator = discriminator
        self.declaration_info = ''
        self.refs = []

    def add_ref(self, category, discriminator):
        self.refs.append(hash((category,) + discriminator))

    def __hash__(self):
        if self.discriminator is not None:
            return hash((self.category,) + self.discriminator)
        return id(self)

v1 = Introspectable('view 1', 'view 1', 'view detail 1', 'view1')
t1 = Introspectable('template 1', 'template 1', 'template detail 1', 'tmpl1')
r1 = Introspectable('route 1', 'route 1', 'route detail 1', 'route1')

intr = refs.setdefault(hash('view1'), [])
refs.extend(['tmpl1', 'route1'])

class API(object):
    def relate(self, *keys):
        for k1 in keys:
            for k2 in keys:
                if k1 != k2:
                    self.related[tuple(
        
