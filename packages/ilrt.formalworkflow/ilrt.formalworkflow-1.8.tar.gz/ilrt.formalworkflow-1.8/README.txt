ILRT Formal Workflow
====================

Overview
--------

Ed Crewe, `ILRT
<http://www.ilrt.bris.ac.uk/>`_ at University of Bristol, September 2nd 2010

NOTE: Updated from plone 3.* version 0.6 to plone 4.* compatible version 1.6
There are no functional changes between 0.6 and 1.6, just a skins install 
tweak and update of the test suite. 

See http://bitbucket.org/edcrewe/ilrt.formalworkflow for mecurial source 
repository, issue tracker etc.

Formal workflow is designed for sites where there may be many editors
for whom unmoderated access to change live published content on the 
web site is not desired. A typical scenario may be an organistaion's 
public website which has to comply with certain legal restrictions or
editorial style for example. To ensure this compliance only a limited
subset of editors are trusted to review and publish content.
Whilst content in the private state is available to all editors.

This package applies a workflow definition based on simple publication 
workflow ... but it ensures that editors cannot modify public content.
Instead it enables `plone.app.iterate`_  with which users can check out a 
working copy of a published item to work on and resubmit for review.

.. _`plone.app.iterate`: http://pypi.python.org/pypi/plone.app.iterate

Editors and owners are also restricted from deleting published items or 
reverting them to past versions, essentially anything that could change 
published content, without review.

Workflow
--------

A diagram of the workflow is available in /docs folder   

.. image:: http://mail.ilrt.bris.ac.uk/~cmetc/images/formalworkflow.png

The following walks through a user story::

  Editor
  - An editor creates a document
  - They edit and then submit it for review
  - It is now in the pending state

  Reviewer
  - The document appears for review in their review list so they click on it
  - They make a few minor ammendments and publish it

  Editor
  - A week later some more information needs to be added to the document
  - The editor goes to it, but it there is no workflow menu just 
    State:Published so they cannot retract it. The edit and history tabs
    are also gone. So instead they must click on 'Make changes' from the actions menu.
  - This locks the item and marks it as being edited in a working copy.
  - The editor does their edits then clicks on submit to bring their changes to the
    attention of the reviewer

  Reviewer
  - The reviewer sees the page pop up in their review list
  - They click on it and look at the changes the editor has made. 
    They like the changes but decide they want some modifications made to them
    by the editor. They dont want to 'Cancel changes' since the editor has done a
    lot of changes, so they just add a note of the further changes needed and make
    the working copy private again.

  Editor
  - The editor reads the comment and re-edits the working copy, once these final changes
    are complete is it resubmitted to the pending state. 

  Reviewer
  - The reviewer notices the item is back again in their review list, so realises 
    it has been re-edited.
    They click on it ... see that it is ready and so do the 'Accept changes' to replace 
    the current published version, at which point the working copy is removed.

Notes
-----

This package is really all just xml config data and reworking skin copy, paste
and delete security to be object specific rather than folder based.
However though it contains little python aside from the functional tests, 
it is a commonly required workflow which does require some time consuming 
configuration tweaks.

If this workflow is applied in conjunction with a theme egg then the formalworkflow
skin should be added near the top of the editing layer's skins listing in the 
portal_skins tool.

If this workflow is applied to an existing site you may require the 
`ilrt.migrationtool 
<http://pypi.python.org/pypi/ilrt.migrationtool>`_ to use its utility for mapping  
existing content states from one workflow to another. Otherwise changing 
workflow reverts objects to the new workflow's default state.

If you wish to use custom types with this workflow you will need to make them versionable 
via the 
`portal_repository tool
<http://plone.org/documentation/how-to/enabling-versioning-on-your-custom-content-types>`_ or 
plone.app.iterate will not be available for them. 

If formal workflow is applied to folders (as is the default profile setting) then types 
without workflow such as images and files cannot be added or deleted by editors.  
To fix this a slightly adapted version of one_state_workflow is also included for these 
content types that allows for editors to modify this content unrestricted. 

You can customize which types use formal_worflow, and hence enforce a review process, 
via the the portal_workflow tool. You could also choose to only apply formal workflow 
to the high profile parts of your site, via `placeful workflow
<http://pypi.python.org/pypi/Products.CMFPlacefulWorkflow>`_.

If you dont want users questioned over the location for their checkouts then you can
specify a checkout locator globally in the site properties. Currently this would be
global_checkout_locator = 'plone.app.iterate.home' or 'plone.app.iterate.parent'
If not set then the default behaviour is used.

