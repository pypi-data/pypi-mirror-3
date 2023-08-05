Introduction
============

collective.flattr includes http://flattr.com/ into Plone. It gives you
a portlet for the entire site, as well as a flattr button (implemented
as viewlet) for Content Types. If you want to, collective.flattr
creates a "thing" on flattr on IObjectInitializedEvent. Then, this
"thing" will be linked to your content automatically.


Installation
============

* Add collective.flattr to eggs of the instance section of your
  buildout and run buildout
* use quickinstall to install collective.flattr
* go to https://flattr.com/apps and register your Plone Site
* go to http://YOURSITE/@@flattr-controlpanel and follow the
  instructions
  (or goto Plone Control Panel -> collective.flattr Settings)

Known issues
============

During my tests, getting of the access token didn't work always on the
first try, because Flattr denied the access. But on a second try it
worked.

The Compact Counter and Large Counter only works in the productive
environment. In development and/or staging, flattr's javascript is not
able to map things via url.
