Introduction
============

This product is intended as a solution for the use case of sending notification
e-mails for items which are about to expire (in, say, the next 24 hours).

The solution this product facilitates allows you to:

1. Select and preview the items for which to take action
2. Select different actions:

   a. send e-mail notification:

      i.  configure message text
      ii. configure recipients

   b. modify the workflow state
   c. move the item somewhere else

All this can be done by site administrators without programming skills, using
Plone's control panel.

Implementation
==============

The facilitated solution requires these parts:

1.  Items are selected in a Topic. Topics allow you to define a relative date,
    like "in the next week". They also allow you to filter items on lots of 
    other criteria.

2. We create a View which fires an Event for each item in the Topic when that 
   is View is called. That is the scope of this product.

3. A Content Rule is added which is triggered by the fired Event. Content Rules
   may have different Actions: sending e-mail, changing workflow state, moving
   objects.

4. The View is called at regular intervals. You may use Cron4Plone or a cron
   job for this.

Getting started
===============

1. Select items
---------------

Create a Topic which gathers all content you want some action taken for. 

    In the future, we might also use plone.app.collection's new style
    Collections for this, however these currently don't seem to support
    relative date criteria.

Example
~~~~~~~

If you want to send e-mails about content that was modified the previous day:

- go to the criteria tab
- "Add new search criteria" for field name "Modification date"
- set "Criteria type" to "Relative date" and click "Add criteria"
- in the "Modification Date" criteria:

  - for "Which day", select "Now"
  - for "In the past or future", select "In the past"
  - for "More or less", select "Less than"

2. Install the `@@fire-topicitems-events` view
----------------------------------------------

Install this product using buildout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In `buildout.cfg`::
  
  eggs +=
      collective.topicitemsevent

Afterwards, install the product using the Plone "Add-on products" controlpanel.

Check that it works
~~~~~~~~~~~~~~~~~~~

Go to your newly created Topic and call the `@@fire-topicitems-events` view on
it. You should have administrator permissions to do this. If all goes well, you
should be redirected to the Topic's default view, and you will see a status
message that says "Firing TopicItemEvent for: ", followed by a list of item
titles and their urls.
  
3. Configure Content Rule
-------------------------

Creating the Content Rule
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Via Plone's control panel, go to the "Content Rules Control Panel" 
   (`/@@rules-controlpanel`).
2. Add a content rule. As the "Triggering event" select "Topic Item Event". 
   Give it a meaningful title. For now, we'll use "Send e-mail notifications 
   about modifications".
3. The new rule will show up in the Rules Control Panel. Click it to add an
   action. Under the header "Perform the following actions", you can select
   any Content Rule action. 
4. For now, just select "Send email", click "Add" and configure the email. 
   (Use the `${title}` and `${url}` variables, so the people who get the mail 
   know what it's about.)
5. You might also want to add a "Notify user" action. This is handy when
   testing the content rule: You'll see the status message(es) after using the 
   `@@fire-topicitems-events` view.

Adding the Content Rule
~~~~~~~~~~~~~~~~~~~~~~~

1. Go to the root of the Plone Site, click "Rules" and add the rule for the 
   site.
2. Afterwards, select the rule and click "Apply to subfolders".

Testing the Content Rule
~~~~~~~~~~~~~~~~~~~~~~~~

Now go to your Topic and call `@@fire-topicitems-events` again.

4. Call the View at intervals
-----------------------------

We'll assume you use Cron4Plone_ for this, but you might also use a cron job.
You need to call the view as administrator, the Cron4Plone documentation will
tell you how.

In the Cron4Plone configuraton screen, you should have a line like::
  
    30 2 * * portal/test-topic/@@fire-topicitems-events

Where 'test-topic' refers to your Topic's id. This will call the view each
night at 02:30 AM.

Issues
======

1. This solution doesn't keep track of which e-mails were sent. When changing
   the Topic's date range, or the cron interval, notifications my be sent 
   multiple times or not at all. This issue will likely never be resolved.

.. _Cron4Plone: http://pypi.python.org/pypi/Products.cron4plone
