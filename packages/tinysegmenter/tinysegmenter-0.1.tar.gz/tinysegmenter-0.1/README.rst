TinySegmenter
=============

“TinySegmenter in Python” is a Python port_ of TinySegmenter_ (which is an extremely compact (23KB) Japanese tokenizer originally written in JavaScript by Mr. Taku Kudo. It works on Python 2.5 or above.

.. _port: http://lilyx.net/tinysegmenter-in-python/
.. _TinySegmenter: http://chasen.org/~taku/software/TinySegmenter/

Authors
-------

See the original authors in ``AUTHORS`` file.

Installation
------------

See ``INSTALL`` file.

Usage
-----

Example code for direct usage::

    > import tinysegmenter
    > segmenter = tinysegmenter.TinySegmenter() 
    > print ' | '.join(segmenter.tokenize(u"私の名前は中野です")) 
    私 | の | 名前 | は | 中野 | です 


“TinySegmenter in Python”‘s interface is compatible with NLTK’s TokenizerI, although the distribution file below does not directly depend on NLTK. If you’d like to use it as a tokenizer in NLTK, you have to modify the first few lines of the code as below (so you can't use the pypi repository version for now, if you wish to do this. Get the sources.)::

    import nltk 
    import re 
    from nltk.tokenize.api import * 

    class TinySegmenter(TokenizerI):
