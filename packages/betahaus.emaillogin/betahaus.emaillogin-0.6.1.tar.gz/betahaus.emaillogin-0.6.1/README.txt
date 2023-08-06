betahaus.emaillogin
====================

Contents
========

* `What is betahaus.emaillogin?`_
* `Installation`_
* `How it works`_
* `Performance`_
* `Extensions`_
* `Issues`_
* `Change history`_
* `Contributors`_

What is betahaus.emaillogin?
----------------------------
The use of emailaddress are speading more and more but Plone does not 
have a convenient way to use a users registered email address to login.

``betahaus.emaillogin`` makes it possible to login using the email address
specified in the user profile. 

Plone has a very powerful and modifiable authentication system called 
Pluggable Authentication Service (PAS). As the name suggest the system 
is pluggable and thus can easily be extended by third-party products 
such as this.  


Installation
------------

buildout:
 - add ``betahaus.emaillogin`` entries to eggs and zcml in the appropriate buildout configuration file.
 - re-run buildout.
 - Install via portal_quickinstaller or Site Setup in plone
 
                

How it works
------------

``betahaus.emaillogin`` is at installation put first in the list of 
extraction plugins. If an email address is specified and a corresponding 
user is found. The email address in the request is replaced with the
username and then simulates failed extraction to continue normal login procedure.


- Code repository: https://svn.plone.org/svn/collective/betahaus.emaillogin


Performance
-----------

The current default implementation does a lookup of the email by iterating over all of the PAS users until the 
corresponding email is found. This approach is fine for a large number of sites with a liberal number of users. 
It is however computationally expensive and slow when the number of users rise. If you experience performance issues
there is a GenericSetup profile called ``extended`` that can be applied. This extension adds a custom email->userid
catalog that enables faster userid look-up from email address.

The extended profile is applied via ``portal_setup`` -> ``Import`` -> select and apply profile ``Extended performance 
for EmailLogin Support``.

If you want to uninstall this extended profile just remove the ``email_catalog`` from the site root and emaillogin will 
fall back to default lookup implementation. 

Extensions
----------

You can write a custom email lookup method that will be used for translating an email to one or more usernames.
The usecase in mind is that a contenttype based member implementation is used and the email is present in a 
catalog, either portal_catalog or a custom catalog. Two examples of this is `betahaus.memberprofile <http://pypi.python.org/pypi/betahaus.memberprofile>`_
and `Products.remember <http://pypi.python.org/pypi/Products.remember>`_. Then by reusing the already stored catalog data there is 
no need for another catalog. To implement this you need to register a utility implementing the interface ``IEmailPluginExtension``.
Warning: When using contentbased membership implementations Plone by default creates the member contenttype on first login.
This can cause a problem on initial login since the information is not available in portal_catalog yet.
 
Utility example::

  from zope.interface import implements
  from betahaus.emaillogin.interfaces import IEmailPluginExtension
  class Dummy(object):
      implements(IEmailPluginExtension)
      
      def getUserNames(self, context, login_email, get_all = False):
          usernames = context.custom_catalog(email = login_email)
          if usernames and get_all == False:
               return usernames[0].username
          return [x.username for x in usernames]

  dummy_extension = Dummy()
  
  
Zcml registration example::

  <utility
      provides="betahaus.emaillogin.interfaces.IEmailPluginExtension"      
      component="betahaus.emaillogin.tests.test_extension.dummy_extension"
      permission="zope.Public"
      />  


Issues
------

Issues can be filed at `the issue tracker <http://plone.org/products/betahaus.emaillogin/issues>`_ on the products page at plone.org.
After update to Plone 4 compatibility some bugs might have been introduced. All tests for plone 3 pass, but if you find any bugs don't 
hesitate to file it.  

