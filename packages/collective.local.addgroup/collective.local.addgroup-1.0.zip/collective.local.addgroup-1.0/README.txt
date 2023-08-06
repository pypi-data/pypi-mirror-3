Introduction
============

Allows to create a group and assign roles directly from the sharing tab for Plone 4.
Tested on Plone 4.1.

Content types have just to implement IAddNewGroup to have the functionnality.

If you want to enable it for Folder, you only have to add to your buildout.cfg::

  [instance]
  zcml =
      ...
      collective.local.addgroup


If you don't want the functionnality for Folder, but on your own content type,
add to the configure.zcml of your policy module::

  <include package="collective.local.addgroup" file="minimal.zcml" />
  <class class="my.package.content.MyContent.MyContent">
     <implements interface="collective.local.addgroup.interfaces.IAddNewGroup" />
  </class>

The user need to have the "Add Groups" permission to add a new group and
"Manage users" to add and remove users from the listed groups.
