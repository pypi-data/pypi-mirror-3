Softserve.py
============

Use `softserve.py` if your other servers are just too fast.

When would servers be *too* fast?
---------------------------------

Say you're developing a webapp and want to see how it renders to a user with
network lag (e.g. a [flash of unstyled content][fouc], [flash of unstyled
text][fout], delays in dynamically requesting and loading content via
JavaScript). Just serving files locally doesn't really delay anything, and the
[Web Inspector][webinspector], while useful, doesn't give you a good
qualitative sense for what the user would experience on a slow network
connection.

[fouc]: http://en.wikipedia.org/wiki/Flash_of_unstyled_content
[fout]: http://blog.typekit.com/2010/10/29/font-events-controlling-the-fout/
[webinspector]: http://trac.webkit.org/wiki/WebInspector

Use `softserve.py` and test your web app. Make sure it doesn't suck on a slow
net connection.

Installation
------------

Install with `pip install softserve`.

Use
---

Run with `softserve.py [path to your files here]` (by default, uses current
working directory). Options:

* `--port`: run from alternate port
* `--min`: minimum delay time in milliseconds
* `--max`: maximum delay time in milliseconds

License
-------

MIT license.
