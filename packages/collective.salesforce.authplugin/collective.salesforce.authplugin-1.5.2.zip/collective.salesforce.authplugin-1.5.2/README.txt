Overview
========

Using the architecture of Zope's Pluggable Authentication Service and PlonePAS, Salesforce
Auth Plugin provides the infrastructure to manage site users as arbitrary objects within a 
Plone portal.  Features and capabilities for Plone user management via Salesforce.com include:


- Configurable SFObject type to serve as Plone user for authentication
- Configurable username and password field on an SFObject for credential checking
- Optional password encryption
- Optional caching of user data from Salesforce.com to improve performance
- Addition of new users as designated SFObject type from Plone portal into Salesforce.com
- Property retrieval and setting for Plone users as stored in Salesforce.com

Installation, Configuration, and Usage
======================================

Requirements
------------

 * Active Salesforce.com account with API access from http://www.salesforce.com

 * Developed and tested against Plone 3.x and 4.0.

 * salesforcebaseconnector (and its pre-reqs, such as 'beatbox' python product)
   Instructions for configuration of salesforcebaseconnector are in README.txt of the
   product which is downloadable here:
   http://plone.org/products/salesforcebaseconnector

 * Some basic understanding the PAS and PlonePAS infrastructure and capabilities

Steps for Installation into Plone
---------------------------------

1. IMPORTANT: Make sure you install/configure salesforcebaseconnector as
   mentioned above and set your login and password.

2. Install the salesforceauthplugin product as you would for any normal Plone
   product (using Add/Remove Products or the Quick Installer).

Configure Plugin
----------------

Though you've already installed the Salesforce Auth Plugin, which creates and
activates a PAS plugin for use in authentication, user creation, and profile
management, this has no impact on your Plone site's authentication scheme until
you've done some additional configuration.

Configure the salesforceauthplugin through the ZMI, at
acl_users/salesforceauthmultiplugin. (This is the acl_users *within* your Plone
site, not the one at the Zope root.)

At a minimum, you need to determine and configure on the Salesforce Auth Plugin:

 * Which Salesforce.com object (i.e. Contact, Lead, Account, etc.) you'll treat
   as users within your site (remember that if you'd like to treat multiple
   Salesforce objects as users, you can do so by setting up multiple Salesforce
   Auth Plugins).  See "Caveats" in this document for more information on this.

 * Which fields of the aforementioned chosen SFObject will serve as the username
   and password credentials for authentication.  At this point, the Salesforce
   Auth Plugin assumes that credentials will include and be limited to some
   field used for "username" and another optionally encryption aware field for
   password. This would look like::
     
     password|Password__c
     username|UserName__c

 * In addition, you can enable password encryption, setup additional
   authentication requirements (in the form of a SOQL statement), and choose which
   properties to manage in Salesforce.com, rather than within Mutable Properties.
   This would look like::
  
     assistant_name|AssistantName
     department|Department

Caching
-------
 
In addition to creating and activating a PAS plugin for use in authentication,
user creation, and profile management within your acl_users object, Salesforce
Auth Plugin also associates a RAM cache with the created plugin.  The cache
period is set for 10 minutes by default.  This is essential for ensuring that
the use of Salesforce Auth Plugin doesn't adversely impact the performance of
your Plone site.

The Salesforce Auth Plugin caches user enumerations and user properties.  If you
only manage your users and user properties through Plone, the cache will not have
any adverse effects, as the Salesforce Auth Plugin will invalidate the cache when
changes take place.  However, be aware that when modifying users through
Salesforce.com, Plone may not be aware of the changes for up to 10 minutes.  This
applies for any of the following modifications via Salesforce.com:
  
 * new user added
 * user removed
 * user properties for user are changed
  
To modify the cache period: In the ZMI, go to SalesforceAuthPluginCache in your
portal root.
  
To remove the cache: In the ZMI, go to acl_users/salesforceauthmultiplugin and
go to the Caching tab.
  
User authentication can also be optionally cached.  This is disabled by default,
and is probably unnecessary unless you routinely have users logging into Plone
from other sources besides the Salesforce Auth Plugin. To enable it, set
CACHE_PASSWORDS to True in config.py.  This may boost performance at the expense
of also introducing a 10-minute delay when passwords are changed via
salesforce.com.

Through The Web Testing
-----------------------

Let's try joining a site and seeing if the login appears in Salesforce.com

Once the plugin is installed open up a browser and enter the URL of your
Plone instance. You may need to log out first which will require closing your
browser and reopening it.

In Plone 3.0, registration is disabled by default.

As site admin, head over to "Site Setup->Security" then check the 
"Enable self-registration" option.  
   
You may want to make sure your new Plone site's Mail server settings (and
"From:" address) are setup so when you create a new account, Plone can
send its Welcome email.

Click on the link to join (in the upper right hand corner, next to the log-in
link) to create a new login.

Go ahead and add the user and then log in to your Salesforce account
at http://www.salesforce.com. The user you just added
should be found in your list of contacts.

Then, you should be able to log out of Plone and try logging in as
the new user you just created.  See the "Customizing" section of this
document for tips about how you might tweak the user experience a bit more.

Customizing
-----------

For simple tweaks to the personalize form, see documentation in 
"customizing_personalize.txt" within the docs directory of this package.

Tips
----  
  
 * If you're setting a Date or DateTime property on a Salesforce object
   make sure your input field type is of DateTime format.  Manually, this 
   is done with::
     
    <input type="text" name="birthdate:date"/>

Caveats
-------

 * At this time, Contact, Account, and Lead objects have been pretty 
   thoroughly tested and are the target use cases for this product.  One might
   commonly want to use some custom Salesforce.com object to serve as the user
   object. While technically, probably any object could work for authentication,
   assuming a username and password field have been configured, other
   Salesforce.com objects may or may not work with all available PAS
   configuration options.

 * As a follow-up to the caveat regarding which Salesforce objects are likely
   to work with this product, at this time objects where there are required
   fields that don't except a string data type will not work as a user adder
   utility.
   
   For example, the Event object requires an integer for length in
   minutes as well as an HTML4 formatted date/time for start of event.  By
   contrast, the interface for doAddUser mandates that only the login and
   password are passed in the signature. For this reason, when create is called
   via the Salesforce.com API, we use the provided login value for all required
   fields needed to create the object.  Thus, PAS join capability is unlikely
   to pass doAddUser the appropriate data types for all required fields for more
   complex Salesforce objects (a la Event) in order to allow the initial
   creation of the object to happen.  Of course, PlonePAS will then go forth and
   update (using set property capabilities) those fields that were temporarily
   stocked with the login value if they were asked somewhere in the signup
   process, since this happens after doAddUser is called.

 * Self-Service Users and Salesforce.com Users have not been tested with this
   product.  They may or may not work.


Additional Resources
====================

Product home is http://plone.org/products/salesforceauthplugin. A
`documentation area`_ and `issue tracker`_ are available.

.. _documentation area: http://plone.org/documentation/manual/integrating-plone-with-salesforce.com
.. _issue tracker: http://plone.org/products/salesforceauthplugin/issues

A Google Group, called `Plone Salesforce Integration`_ exists with the sole aim
of discussing and developing tools to make Plone integrate well with
Salesforce.com.  If you have a question, joining this group and posting to the
mailing list is the likely best way to get support.

.. _Plone Salesforce Integration: http://groups.google.com/group/plonesf

Failing that, please try using the Plone users' mailing list or the #plone IRC
channel on freenode for support requests. If you are unable to get your
questions answered there, or are interested in helping develop the product, see
the credits below for individuals you might contact.

Credits
=======

The Plone & Salesforce crew in Seattle and Portland:

- Jon Baldivieso <jonb --AT-- groundwire --DOT-- org>
- Andrew Burkhalter <andrewburkhalter --AT-- gmail --DOT-- com>
- Brian Gershon <briang --AT-- webcollective --DOT-- coop>
- David Glick <davidglick --AT-- groundwire --DOT-- org> 
- Jesse Snyder <jesses --AT-- npowerseattle --DOT-- org>

Thanks to Salesforce.com Foundation and Enfold Systems for their gift and work
on beatbox and the original proof of concept code that has become Salesforce
Auth Plugin (see: 
http://gokubi.com/archives/onenorthwest-gets-grant-from-salesforcecom-to-integrate-with-plone)

See the changelog for the growing list of people who helped
with particular features or bugs.

License
=======
Distributed under the GPL.

See LICENSE.txt and LICENSE.GPL for details.

Running Tests
=============

It is strongly recommended that you run your tests against a free developer
account, rather than a real production Salesforce.com instance. ... With that
said, to run the tests for Salesforce Auth Plugin do the following:

Configure your Salesforce.com instance:
---------------------------------------

In order to successfully run all of the automated unit tests, some
modifications need to happen within your Salesforce.com instance.  

In many of the tests, authentication, user creation, and modification happen
against the Salesforce.com contact and/or lead object.  Specifically, the unit
tests create objects and then authenticate against two custom fields: Password
and UserName.

For all tests to successfully work create and configure the following 
fields as shown below:

  =================  ================  =============
  Field Label        Field Name        Field Type
  =================  ================  =============
  Password           Password          Text(100)
  User Name          UserName          Text(50)
  Favorite Boolean   FavoriteBoolean   Checkbox
  Favorite Float     FavoriteFloat     Number(13, 5)
  =================  ================  =============

Note: You can accept the defaults for the other field attributes.

Read:
-----

Running Tests --> "To run tests in a unix-like environment" from
`SalesforceBaseConnector`_, which is a dependency, so you should have it :)

.. _SalesforceBaseConnector: http://plone.org/products/salesforcebaseconnector

Running the tests
-----------------

Rather than running the test suite for salesforcebaseconnector
do the following:

    bin/instance test -s collective.salesforce.authplugin

If you have trouble running tests, consult "FAQ about running tests" from
SalesforceBaseConnector.
