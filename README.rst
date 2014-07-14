===============================
PyVideo Scraper
===============================

Building on the `Gist of Miguel Grinberg`_ and merging with my own fork of Nick Facano's `pytube`_ I've hacked this together to scan `pyvideo.org`_ pages and download the video content from youtube.

To get going grab my fork of `pytube`_ (it's been slightly modified to have a non-verbose mode) run python setup.py install in the pytube directory and then all you have to do is download this repo - it doesn't need to be installed...

.. _Gist of Miguel Grinberg: https://gist.github.com/miguelgrinberg/5f52ceb565264b1e969a
.. _pytube: https://github.com/johnnycakes79/pytube
.. _pyvideo.org: http://pyvideo.org/

Known Bugs
----------

* When running on a long list of videos (SciPy 2014 - 57 Videos for example) the script crashes out with 429 Error: Too many requests... will look into this soon.

ToDo
--------

* Fix this repo with proper tests and documentation.
* Generalise the scirpt to also 'search' youtube and download the results.
