okonomi
=======

Incredibly simple static javascript file handling.

from any template, as many times as you want::

    {% jsrequire /path/to/my/js.js %}

or::

    {% jsrequire http://google.com/some/api %}

``okonomi`` will take care of getting just the right ``<script>`` includes into the
HEAD of your template using the hideous ``${JS}`` sigil that you must include in
a base template somewhere.


django settings
---------------
* ``OKONOMI_STATIC_URL`` set this to whatever makes sense for your django project.
* ``OKONOMI_STATIC_PATH`` set this to whatever makes sense for your django project.
* ``OKONOMI_HTML_PATH_TEMPLATE`` defaults to ``<script type="text/javascript" src="%s"></script>\n``
* ``OKONOMI_HTML_URL_TEMPLATE`` defaults to ``<script type="text/javascript" src="%s"></script>\n``


Requirements
============

Locally hosted media
--------------------

* ${JS} sigil in HEAD or somewhere::

    {% jsrequire /formchecking.js %}

* add ``/formchecking.js`` to ``set()`` in context

... (repeat in various templates) ...

* middleware:
    * generate key from what is in the set()
    * not cached?
        * read all the js files, concat, cache

    * insert ``<script src="/js/cache_key"></script>`` for ``${JS}``


Remote hosted media
-------------------

* ``${JS}`` sigil in HEAD or somewhere::

    {% jsrequire https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.js %}

* add url to set() in context

... (repeat in various templates) ...

* middleware:
    * insert ``<script src="url"></script>`` for each remote include


author
------
Nathaniel Smith <nate.smith@coxinc.com>
for Cox Media Group Digital & Strategy

license
-------
okonomi is licensed under the MIT license.
