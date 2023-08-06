migration_template = """<html>
<head><title>Migrating external methods</title></head>
<body>
<form action="./migrate">
<h1>Migration</h1>
<p>Migrate External Methods that used to live in the
Extensions folder to the following module (just the
module name).  The module should have a folder called
Extensions which contains all the external methods
that used to live in the Zope instance Extensions folder:<br /><br />
Migrate to module <input type="text" name="to" />
<input type="submit" value=" Change " />
</form>
</body>
</html>
"""

def migrate(self, to=''):
    if not to:
        return migration_template
    try:
        __import__(to)
    except ImportError:
        try:
            __import__('Products.' + to)
        except ImportError:
            return "Invalid module name"
    migrated = []
    for name, external_method in self.ZopeFind(self, obj_metatypes=('External Method',), search_sub=True):
        if not '.' in external_method._module:
            external_method._module = to + '.' + external_method._module
            migrated.append((external_method._module, external_method))
    return 'Migrated ' + ','.join(map(lambda x: str(x), migrated))
