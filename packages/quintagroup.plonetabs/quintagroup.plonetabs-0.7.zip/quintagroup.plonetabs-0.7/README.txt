Introduction
============

This product allows Plone websites to manage portal_actions tool from
portal_control_panel configlet in an easier way. Especially using rich (Ajax
based) mode.

This is a fully rewritten version of qPloneTabs product. It is based on kss
javascript framework and Plone 3 technologies.

Features
--------

* quintagroup.plonetabs allows editing portal tabs, document actions, site actions, folder buttons (and other portal_actions tools) - all via Plone Control Panel
* possibility to make items visible/invisible
* possibility to change items order by simple drag-and-drop

Usage
-----

To create new Plone tabs go to your Site Setup:

* Select Plone Tabs from the list of Add-on Products Configuration
* In the Select category to manage select what items you want to manage
* Enter the name and the link of the tab you want to create
* Click Add button

To change tabs order:

* Click on the arrows next to the item title you want to change position for
* Move it up/down to the necessary place

Screencast
----------

You can watch Plone Tabs Screencast
http://quintagroup.com/cms/screencasts/qplonetabs to see how to use this
products on your Plone instance. Learn how to install Plone Tabs product on a
buildout-based Plone instance, how to create new tabs, change their order, how
to delete or edit tabs, as well as Plone actions items.

Requirements
------------

* Plone 4
* Plone 3.x

Rich (Ajax based) mode works for
--------------------------------

* Firefox 2+
* IE 7+

Notes
-----

* In case you are using browser which is not compatible with the given product (see list above for compatible browsers), you can easily switch to 'Plain Mode' and use basic HTML forms without any javascript functionality. That plain mode should work for any browser ;-)

* If you were using qPloneTabs product before and now you want to install this new package then before installing quintagroup.plonetabs uninstall qPloneTabs product from quickinstaller tool, then remove it from Products folder and only after that install quintagroup.plonetabs package.

Link
----

* See Plone Tabs screencast at http://quintagroup.com/services/plone-development/products/plone-tabs to learn how to use this products on your Plone instance.

Thanks
------

* Godefroid Chapelle [gotcha]


Author
------

* Vitaliy Podoba [piv]
