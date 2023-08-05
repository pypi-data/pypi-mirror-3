class StarBrowser(object):
    """docstring for StarBrowser"""
    def __init__(self,  cube, connection=None, schema=None, locale=None):
        super(StarBrowser, self).__init__()
        self.cube = cube
        self.connection = connection
        self.schema = schema
        self.locale = locale

    def facts(self, cell, order=None):
        view = StarView(cube)
        pass
        
class StarView(object):
    """docstring for StarQuery"""
    def __init__(self, arg):
        super(StarView, self).__init__()
        self.arg = arg
        