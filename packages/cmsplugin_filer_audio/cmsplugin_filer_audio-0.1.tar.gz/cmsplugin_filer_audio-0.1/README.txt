Django CMS Audio Filer Plugin
=============================

This plugin plays a mp3 file using Flowplayer. Uses django-filer for the
file storage.

The plugin uses it's own flowplayer 3.2.11 with the audio plugin version
3,2,9.


Installation
------------

Install the python module:

    pip install cmsplugin_filer_audio

Add the 'cmsplugin_filer_audio' to INSTALLED_APPS


Usage
-----

1. Add 'Audio' plugin to a  pageholder.

2. Set the title, choose the file and decide if the player will start
   automatically or not.
