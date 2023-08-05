Schools is a free diazo theme for Plone 4.1

Features
--------

* Replaceable header image for the whole site or site sections. To have new top image, add image with
  ``topimage`` shortname into desirable location on site. Default image size is 993*107px. 

  In case you upload higher image - it will not be completely displayed unlesss you configure ``logo_min_height`` 
  value in 'Diazo theme' panel -> 'Parameter expressions' tab. Replace default value 107 with a new header height.

* Right top area is reserved for a portlet. The first portlet from right column is displayed there. 

* Basic edits via 'Diazo theme' panel (/@@theming-controlpanel)
  
  Open 'Advanced settings' tab in 'Diazo theme' panel. In 'Parameter expressions' field replace default values for the following 
  parameters to modify:

  - column width: update values for ``columnonewidth`` and ``columntwowidth`` (numbers only)
  - links colors: update values for ``links_color``, ``hover_links_color``, and ``visited_links_color`` (be carefull to insert valid css colors instead of default ones) 
  - slogan: update text for ``site_description``, replace default slogan 'Free Theme for Plone' with a new one.
  - In case Schools theme gets broken after your modifying the above parameters - reinstall the theme to revert to default parameters.

* Carousel Banner

  Rotating banners can be added in case you install Products.Carousel add-on. Custom Carousel display style applies automatically to carousel banner.
 
  To create a banner on the front page - go to the 'Carousel' tab in the task bar. Set carousel options and select 
  'Carousel Banner' from 'Add new...' drop-down menu. Upload image that will be used as one rotating banner, type its title and 
  text (will be displayed under the image), and provide web address image title will be linked to. Add as many carousel banners
  as you need. 
  
  Optimum image dimensions are  397*288px. There are 4 demo images that might be used as demo banners - see 'src' folder within
  theme package (quintagroup -> theme -> schools).

* Replaceable logo as in default Plone: ZMI -> customize portal_skins -> sunburst_images -> logo.png image.

* Editable footer as in default Plone: ZMI -> customize portal_view_customizations -> plone.footer

* Compatibility with popular add-ons

Add-ons Compatibility
=====================

Theme was enhanced to work correctly with:

* Products.Carousel
* quintagroup.dropdownmenu
* Products.LinguaPlone
* Products.PloneFormGen
* Products.ContentWellPortlets

Recommended
===========

Theme was tested with:

* Plone 4.1
* plone.app.theming 1.0b9
* Products.Carousel 2.1
* quintagroup.dropdownmenu 1.2.5
* Products.LinguaPlone 4.1.1
* Products.PloneFormGen 1.7.0
* Products.ContentWellPortlets 4.1.0

Dependencies
============

* plone.app.theming

Home Directory
==============

http://skins.quintagroup.com/schools

Authors
=======

* Yuriy Hvozdovych
* Volodymyr Rudnytskyy
* Serhiy Valchuk  
* Taras Peretiatko 

Quintagroup: http://quintagroup.com, 2006-2012
