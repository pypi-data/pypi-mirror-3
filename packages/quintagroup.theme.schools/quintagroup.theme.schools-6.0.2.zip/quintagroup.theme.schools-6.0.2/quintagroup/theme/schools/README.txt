Schools is a free diazo theme for Plone 4.1

Features
--------

* Carousel Banner
 
  Schools Plone Theme can contain carousel banner(s) on the front page. Changeable set of rotating banners can be added to 
  the Schools's front page with help of Products.Carousel, that is installed automatically with the theme. Banner images 
  rotate every several seconds, besides site visitor can browse any of them by covering the corresponding pager.

  To create a banner on the front page - go to the 'Carousel' tab in the task bar. Set carousel options and select 
  'Carousel Banner' from 'Add new...' drop-down menu. Upload image that will be used as one rotating banner, type its title and 
  text (will be displayed under the image), and provide web address image title will be linked to. Add as many carousel banners
  as you need. 
  
  Optimum image dimensions are  397*288px. There are 4 demo images that might be used as demo banners - see 'src' folder within
  theme package (quintagroup -> theme -> schools).

* Right top area is reserved for a portlet. The first portlet from right column is displayed there. 

* Basic edits via 'Diazo theme' panel (/@@theming-controlpanel)
  
  Open 'Advanced settings' in 'Diazo theme' panel. In 'Parameter expressions' field replace 'False' for 'True' 
  in ``enablecustomizations = python:False`` line.

  Now you can fill in new values for the following parameters in 'Parameter expressions' field to modify:

  - column width: update values for ``columnonewidth`` and ``columntwowidth`` (numbers only)
  - links colors: update values for ``links_color``, ``hover_links_color``, and ``visited_links_color`` (be carefull to insert valid css colors
    instead of default ones) 
  - logo and top portlet block height: update ``logo_min_height`` (number only)

 In case Schools theme gets broken after your modifying the above parameters - try reinstalling the theme to revert to default parameters.

* Replaceable logo as in default Plone: customize portal_skins -> sunburst_images -> logo.png image.
* Editable footer as in default Plone: customize portal_view_customizations -> plone.footer

Dependencies
============

* plone.app.theming
* plone.app.themingplugins
* Products.Carousel

Recommended
===========

SuinRain diazo theme was tested with:

* Plone 4.1
* plone.app.theming 1.0b9 
* plone.app.themingplugins 1.0b1
* Products.Carousel 2.1

Besides, special styles were added to the theme for correct theme display with the following products activated:

* quintagroup.dropdownmenu 1.2.5
* Products.LinguaPlone 4.1

Home Directory
==============

http://skins.quintagroup.com/schools

Authors
=======

* Yuriy Hvozdovych
* Volodymyr Rudnytskyy
* Serhiy Valchuk  
* Taras Peretiatko 

Quintagroup: http://quintagroup.com, 2006-2011
