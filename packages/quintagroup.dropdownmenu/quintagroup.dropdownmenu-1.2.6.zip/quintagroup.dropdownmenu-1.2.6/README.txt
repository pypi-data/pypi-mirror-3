Introduction
------------

This package allows to build dropdown menu through the web with portal_actions.
Submenus are built from a tree of nested Category Actions and Actions.
The other strategy used to populate submenus is Plone default NavigationStrategy, 
the one used in navigation portlet.  

This project is successor of qPloneDropDownMenu. 

Building you dropdown menu with portal_actions
==============================================

Starting from Plone 3 portal actions introduced CMF Action Category 
containers, it opened opportunity to build nested actions trees. Though CMF Action 
Category does not behave as a regular action, it has different set of properties. 
We introduced convention in quintagroup.dropdownmenu that requires to have 
a specially named Action for each Actions Category. The id of each such action 
must be build using the rule::
  
  action_id = prefix + category_id + suffix
   
where:
  
:category_id: is id of correspondent CMF Action Category    
:prefix: defined in DropDownMenu configlet, default value ''
:suffix: defined in DropDownMenu configlet, default value '_sub'

So, the actions structure can look like::

  + portal_tabs
  |- home
  |- blog_sub
  |-+ blog
  | |-- 2009
  | |-- 2010
     
By default the root of dropdown menu is 'portal_tabs' category.
 
Compatibility
=============

* **Plone 4** sample CSS file based on Sunburst theme provided
* **Plone 3.0-3.3** the default CSS file has to be overridden

Installation
============

* add http://good-py.appspot.com/release/plone.app.registry/1.0b2 to versions in your buildout
* add quintagroup.dropdownmenu to eggs in your buildout
* install Plone DropDown Menu in Plone via Site Setup -> Add-ons

Find more details inside docs/INSTALL.txt 
