Introduction
============

Allows to create a user and assign roles directly from the sharing tab for Plone >= 4.1.
This can work with Plone 4.0.9 with plone.app.users > 1.0.6, < 1.1.x.

Content types have just to implement IAddNewUser.

Add to the configure.zcml of your policy module::

  <include package="collective.local.adduser" />
  <class class="my.package.content.MyContent.MyContent">
     <implements interface="collective.local.adduser.interfaces.IAddNewUser" />
  </class>

