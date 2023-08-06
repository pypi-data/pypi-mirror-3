MigrateExternalMethods is a simple product that migrates existing
External Method objects to a module.

Install as an egg and then add the External Method with id migrate,
module name MigrateExternalMethods and function name migrate.

External methods that used to live in the Zope instance Extensions
folder are moved into a product with an Extensions folder, and then
the method can be run with the name of the product (without the
"Products.") prefix.
