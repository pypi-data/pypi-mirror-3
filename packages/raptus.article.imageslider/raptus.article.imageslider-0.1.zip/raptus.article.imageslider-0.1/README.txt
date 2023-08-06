Introduction
============

Show contained images in a `jQueryTOOLS scrollable`__ carousel.
(Does not use raptus.easyslider because jquerytools is shipped with Plone)

.. __: http://jquerytools.org/demos/scrollable/index.html

The reason for this being not integrated in `raptus.article.slider` is that
the latter depends on `raptus.article.nesting`.

The following features for `raptus.article` are provided by this package:

Components
----------

* Image Slider (Slider of images contained in the article) (XXX TODO)
* Image Slider Teaser (Slider of images contained in the article displayed above the columns)

Configuration
-------------

Configuration options can be found in portal_properties/raptus_article

images_imagesliderteaser_width
    maximum width of the image displayed in the slider
    defaults to 5

images_imagesliderteaser_height
    maximum height of the image displayed in the slider
    defaults to 0 (no limit)


imageslider_teaser_cropwidth/height
    use this to crop image to a certain width or height

imageslider_teaser_height
    maximum height of the slider
    (only used in case images_imagesliderteaser_height and cropheight
    are set to 0)

imageslider_teaser_caption (True/False)
    show the description of images in the slider

imageslider_teaser_navigation (True/False)
    activates the `navigator plugin`__

.. __:http://jquerytools.github.com/documentation/scrollable/navigator.html


imageslider_teaser_fadetime
    The time (in milliseconds) of the scrolling animation.

imageslider_teaser_halttime
    The time (in milliseconds) between autoscrolls.


TODOS
-----

* localization

* * images for components

Dependencies
------------

* raptus.article.images

Installation
============

Please refer to `raptus.article.gallery`_ for installation instructions.

.. _`raptus.article.gallery`: http://pypi.python.org/pypi/raptus.article.gallery


Usage
=====

Components
----------

Navigate to the "Components" tab of your article and select one of the gallery
components and press "save and view". Note that at least one image has to be contained
in the article in which this component is active.


