Introduction
============

This product add to the Plone administrator a new flag on the user profile: "**Block user password reset**".
This check will mark a specific user as unable to change his own password.

The Plone administrator can still reset the user password from the "*Users and Groups*" control panel.

When you can need this
----------------------

This can be useful only in some rare situation, when you need to share a single user account to a set of
users (giving them all the same userid and password), and for whatever reason you can't/don't want create
multiple users.
Obviously you don't want that an evil guy inside this set of users can change the password.

Plone security
--------------

Keep in mind that Plone can handle change password using its own security, playing with
``Set own password`` permission.

Use this product only if you need to control the change password behavior only for specific(s)
users.

Compatibility
=============

This product has been tested on *Plone 3*. It will not work on Plone 4, due to deep changes
in the user data infrastructure.

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

