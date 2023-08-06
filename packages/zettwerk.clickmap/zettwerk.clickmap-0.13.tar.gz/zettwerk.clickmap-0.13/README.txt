Introduction
============

zettwerk.clickmap integrates a clickmap/heatmap tool into Plone. These tools are for visualisation of user clicks on the page. So you can see, what part of the pages might be more interesting for your visitors, and which are not. Some good known tracking tools are offering the same, but this one adds no external url, cause it handles all to collect and show the clicks.

You can selective enable or disalbe the content type objects which gets logged and view the results in an overlay image.

Things to know
==============

The concept works best, if the page uses a fixed width layout. But it also tries to work with variable width layouts. To handle this, you must setup the tool to a given "reference" width, where all clicks gets transformed to. Use the plone control panel to do so, and read the given comments.

It is also important to know, that the control panel gui gives you a list of all available objects, which you can choose the ones, you want to log. But this also means, that on big sites, the generation of the list might took a while. I am looking for an alternate widget to select the pages.

The storage of the clicks is handle by a BTree data structure. This might be ok for small to mid-sized pages, but there es no experiance with heavy load pages.

And the last side note: clicks of users with edit permissions of an object will never be logged, cause the inline edit gui won't suite to the generated output image/map.

Plone compatibility
=================== 

The actual work is only tested in Plone 4. There is also a Plone 3 version tagged in the svn which should work, but it is not tested with the latest versions. It also contains jquery-ui javascript resources, which are now removed in trunk (and so for Plone 4). (Anyone knows a lightwight drag'n'drop lib for jquery?)

Installation
============ 

Add zettwerk.clickmap to your buildout eggs. After running buildout and starting the instance, you can install Zettwerk Clickmap via portal_quickinstaller to your plone instance. Switch to the control panel and use the configlet to adapt the settings.
