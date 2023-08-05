class Container(dict):
    """return the items as pseudo members
       >>> a = Container()
       >>> a['otto'] = 2
       >>> a.otto
       2
    """
    def __getattr__(self, name):
        if name in self :
            return self[name]

