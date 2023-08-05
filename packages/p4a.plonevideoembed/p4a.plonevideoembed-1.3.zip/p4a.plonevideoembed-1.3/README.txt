p4a.plonevideoembed
===================

Project Description
-------------------
*p4a.plonevideoembed* uses *p4a.videoembed* to allow you to embed a video that
is hosted on a remote video sharing site. Simply:

* choose *Link* from the *add new...* menu
* paste in a link to:

  * YouTube http://www.youtube.com/
  * Google Video http://video.google.fr
  * Yahoo Video http://video.yahoo.com/
  * Revver (both http://revver.com and http://one.revver.com)
  * Vimeo http://vimeo.com
  * Vmix http://vmix.com
  * Blip.tv http://blip.tv
  * iFilm http://ifilm.com
  * MySpace http://vids.myspace.com
  * MetaCafe http://metacafe.com
  * College Humor http://collegehumor.com
  * Veoh http://veoh.com
  * flash video (.flv) using http://www.longtailvideo.com/players/jw-flv-player
  * (.mov .qt .m4v) ># The original revver QT embed
  * VH1 http://vh1.com
  * Live Leak http://liveleak.com
  * Video detective http://videodetective.com
  * Dailymotion http://www.dailymotion.com

and the video will be added to your Plone site complete with all the metadata.

Installation
------------
*p4a.plonevideoembed* requires *Plone 3.3+*.
 
Add these lines to your buildout.cfg file, and re-run your buildout.
Then install the add-ons from the Add/Remove products page in the
Plone Control Panel.::

    [buildout]
    ...
    
    eggs = 
        ...
        p4a.plonevideoembed
    
    [instance]
    ...
    
    zcml = 
        ...
        p4a.plonevideoembed

Features
--------

Video Links
~~~~~~~~~~~
* Add a normal link and Plone auto-recognizes it as a video link,
  and embeds an appropriate video player
* Video player support for many video hosting providers (listed above)
* Metadata extraction support for:

  * Youtube
  * Google Video
  * Blip.tv
  * Revver

* Extracted metadata includes:

  * thumbnail
  * title
  * description
  * tags
  * author

* FLV URL extraction support for Youtube and Blip.tv.
