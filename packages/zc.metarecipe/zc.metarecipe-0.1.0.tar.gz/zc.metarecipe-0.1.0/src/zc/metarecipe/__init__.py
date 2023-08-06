import ConfigParser, cStringIO, textwrap

class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

    def install(self):
        return ()

    update = install

    def __setitem__(self, name, data):
        self.buildout._raw[name] = data
        self.buildout[name]

    def parse(self, data):
        parser = ConfigParser.RawConfigParser()
        parser.readfp(cStringIO.StringIO(textwrap.dedent(data)))

        for section in parser.sections():
            self[section] = dict(parser.items(section))
