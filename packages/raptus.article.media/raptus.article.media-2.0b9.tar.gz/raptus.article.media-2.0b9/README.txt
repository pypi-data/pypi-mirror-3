Introduction
============

raptus.article.media provides audio and video support for Articles.

The following features for raptus.article are provided by this package:

Content
-------
    * Audio - Based on File - add your audio files in a article.
    * Video - Based on File - add your video files in a article.
    * VideoEmbed - Based on Link - add your reference to your video in a article.
    
Components
----------
    * Audio (List of the audio files contained in the article)
    * Video (List of the video files contained in the article)

Dependencies
------------
    * collective.flowplayer
    * Products.ContentTypeValidator
    * raptus.article.core
    * plone.app.imaging

Installation
============

To install raptus.article.media into your Plone instance, locate the file
buildout.cfg in the root of your Plone instance directory on the file system,
and open it in a text editor.

Add the actual raptus.article.media add-on to the "eggs" section of
buildout.cfg. Look for the section that looks like this::

    eggs =
        Plone

This section might have additional lines if you have other add-ons already
installed. Just add the raptus.article.media on a separate line, like this::

    eggs =
        Plone
        raptus.article.media

Note that you have to run buildout like this::

    $ bin/buildout

Then go to the "Add-ons" control panel in Plone as an administrator, and
install or reinstall the "raptus.article.default" product.

Note that if you do not use the raptus.article.default package you have to
include the zcml of raptus.article.media either by adding it
to the zcml list in your buildout or by including it in another package's
configure.zcml.

Plone 3 compatibility
---------------------

This packages requires plone.app.imaging which requires two pins in buildout
when using Plone 3, which there are::

    Products.Archetypes = 1.5.16
    plone.scale = 1.2


Migration
=========

Blob-storage
------------

call this view on myplone/@@blob-article-media-migration and run the migration.
all teaser have a separate view at myplone/@@blob-article-teaser-migration.


Usage
=====

Add video/audio
---------------
You may now add videos, embedded videos and audio file in your article. 
Click the "Add new" menu and select "Video", "Embedded video" or "Audio" in the pull down menu.
You get the standard plone form to add your video, embedded video or audio file. 

Components
----------
Navigate to the "Components" tab of your article, select the video or audio component
and press "save and view". Note that at least one video or audio file has to be contained
in the article in which this component is active.

Supported media types
=====================

Audio
-----

* audio/mpeg
* audio/x-mp3
* audio/x-mpeg
* audio/mp3

Video embed
-----------

* YouTube
* GoogleVideo
* Vimeo
* MyVideo

Video
-----

* video/x-flv
* application/x-flash-video
* flv-application/octet-stream
* video/flv
* video/mp4
* video/mp4v-es
* video/x-m4v

Supporting additional video formats
-----------------------------------

To extend the supported video formats with

* video/x-avi
* video/x-msvideo
* video/x-ms-wmv
* video/quicktime

include stxnext.transform.avi2flv in your buildout and reinstall 
raptus.article.media.

Go to `http://pypi.python.org/pypi/stxnext.transform.avi2flv 
<http://pypi.python.org/pypi/stxnext.transform.avi2flv>`_ to read
more about the server side requirements of stxnext.transform.avi2flv.

Copyright and credits
=====================

raptus.article is copyrighted by `Raptus AG <http://raptus.com>`_ and licensed under the GPL. 
See LICENSE.txt for details.
