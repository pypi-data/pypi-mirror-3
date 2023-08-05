webcouturier.dropdownmenu
=========================

Overview
--------

The dropdown solution for Plone since 2007.

You will get the dropdown menus for those items in global navigation that have
the subitems. Submenus are built based on the same policy as the Site Map, so
it will show the same tree as you would get in the Site Map or navigation
portlet being in appropriate section.

How it works
------------

Dropdown menus are build based on the same policy as the Site Map, so it will
show the same tree as you would get in the Site Map or navigation portlet
being in appropriate section. This means - no **private** objects for
anonymouses; no objects, excluded from the navigation - exactly the same
behavior you would expect from Site Map or navigation portlet.

Installation
------------

As any addons, please follow the official install documentation:
http://plone.org/documentation/kb/add-ons/installing

Tips
----

- **While disabling clicking the links with children, I want the links in the
  global navigation bar to be clickable nevertheless.**

  What you need is to customize the ``browser/dropdown.js`` file like the
  following:
  
  ::
  
    jQuery(function ($) {
        $('#portal-globalnav ul .noClick').click(function (e) {
            e.preventDefault();
        });
    });
  
  Note that we have added **ul** in the jQuery selector. This will stop
  clickability of the links in the dropdowns only, but not the section's link
  in the global navigation bar itself.

Credits
-------

Authors:

- Denys Mishunov [mishunov] Twitter_ · `Google+`_

Contributors:

- Wichert Akkerman [wichert] `Simplon`_
- JeanMichel FRANCOIS [toutpt] `Makina-Corpus`_ 
- Thomas Desvarin [thomasdesvenain] `Ecréall`_
- Maurits van Rees [maurits]
- David Glick [davisagli]
- Matt Halstead [matthal]
- Leonardo J. Caballero G. [macagua]
- Florian Schulze [fschulze]


.. _Makina-Corpus: http://www.makina-corpus.com
.. _Simplon: http://www.simplon.biz
.. _Twitter: http://twitter.com/#!/mishunov
.. _Google+: https://plus.google.com/102311957553961771735/posts
.. _toutpt: http://profiles.google.com/toutpt
.. _Ecréall: http://www.ecreall.com/
