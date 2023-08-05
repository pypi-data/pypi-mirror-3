Iterate security changes via the default edit layer
===================================================

Please note that if you use formalworkflow with a theme egg 
or other package that defines its own layer ... you will 
have to respecify the security changes in configure.zcml
for the layer it defines ... ie. copy the contents of 
browser/configure.zcml to the one in your theme egg 
browser folder.

Without these changes ... the permission to checkout an 
iteration of an item is the same as being able to modify 
the original. Hence inappropriate for formal workflow.

NB: plone.app.iterate's own declaration has precidence
for layer="plone.theme.interfaces.IDefaultPloneLayer"

Ed Crewe
