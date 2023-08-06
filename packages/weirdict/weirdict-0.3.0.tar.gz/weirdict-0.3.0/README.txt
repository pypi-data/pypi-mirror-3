========
weirdict
========

This package offers a base implementation as well as several examples of
"normalized dicts".

A normalized dict is a python dictionary subclass whose keys are normalized
through a particular function prior to insertion/modification/deletion.


Examples
========

The example classes provided include:

* A dict whose normalization function can be passed in the constructor (and
  changed on-the-fly),

* A case-insensitive dict,

* a dict whose keys are truncated to a given length,

* a dict whose keys are computed modulo N, where N is a given int.
