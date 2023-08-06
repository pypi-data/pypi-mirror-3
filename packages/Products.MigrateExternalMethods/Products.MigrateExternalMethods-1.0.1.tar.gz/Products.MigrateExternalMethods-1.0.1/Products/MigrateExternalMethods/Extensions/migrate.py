import logging

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

logger = logging.getLogger('MigrateExternalMethods')

def update_external_method(external_method, to):
    external_method.manage_edit(
        title=external_method.title,
        module=to + '.' + external_method._module,
        function=external_method._function)

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
            try:
                update_external_method(external_method, to)
                migrated.append((external_method._module, external_method))
            except Exception, value:
                logger.log(logging.ERROR, 
                           '%s\n %s\n',
                           str((value,external_method,
                                external_method.getPhysicalPath())),
                           'Error when updating external method')
    return 'Migrated ' + ','.join(map(lambda x: str(x), migrated))
