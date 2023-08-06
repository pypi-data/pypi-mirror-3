======================
EyeFi Server Framework
======================

Requirements
-------------

* ``twisted core`` and ``web`` for the network and protocol handling
* ``soappy`` for the protocol
* ``simplejson`` for the google api
* ``pyexiv > 0.2`` for tagging images. http://tilloy.net/dev/pyexiv2/.
  Ubuntu packages are available at
  https://launchpad.net/~pyexiv2-developers/+archive/ppa
* ``flickrapi`` for the flickr upload


Installation
------------

You can run the server either from the tarball or install it as root::

  # python setup.py install

or::

  # python setup.py develop


Get the card's MAC and upload key
---------------------------------

At the moment, EyeFi cards still have to be activated using the
Windows/OSC application bundled with the card. EyeFi Center or EyeFi
Manager will write some configuration to the card and negotiate a unique
upload key with the card and the api.eye.fi server. This procedure works
also in a virtualbox with the usb card reader passed through to the
guest OS. But it does not seem to work with the card's filesystem simply
exposed to the guest. After the procedure, the mac and the key can be
found in ``/Users/*/AppData/Roaming/Eye-Fi/Settings.xml (Windows 7)``.


Configure wireless networks
---------------------------

eyefi-config is a nice open source tool to do that. Alternatively, the
windows application can also be used here.


Configure the server
--------------------

Write a configuration file. Copy ``conf/example.conf`` to ``/etc/eyefi.conf`` or
``~/.eyefi.conf`` or ``./eyefi.conf`` and edit it. The files are read in this
order and override/amend each other.  Insert the mac and the key you
have obtained above in one of these files.  The configuration files can
include an arbitrary number of card sections. A single card named "``card``"
can also be configured via the commandline.


Run the server
--------------

If you want to use the flickr upload, you have to run the server in the
foreground once to get the flickr token::

  $ twistd -n eyefi
 
After that it works also in the background::

  $ twistd eyefi

Get info about generic twisted options::

  $ twistd -h

Get info about the eyefi options::

  $ twistd eyefi -h
