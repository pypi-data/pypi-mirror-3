=============
Release notes
=============
MOD (Nov 16, 2011)
	- This Package was modified by Kevin Carter, to be compatible with the UK API.  
	- python-cloudservers was completely changed so that it is now python-ukcloudservers  which will create a command ukcloudservers

1.1 (May 6, 2010)
=================

* Added a ``--files`` option to :program:`ukcloudservers boot` supporting
  the upload of (up to five) files at boot time.
  
* Added a ``--key`` option to :program:`ukcloudservers boot` to key the server
  with an SSH public key at boot time. This is just a shortcut for ``--files``,
  but it's a useful shortcut.
  
* Changed the default server image to Ubuntu 10.04 LTS.