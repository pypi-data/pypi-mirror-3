Introduction
============

This package registers moment.js_ in the Plone resource registries.

If you need translations you need to add files from the resources/lang
directory in your policy package.

If for example you would like to be able to translate to Dutch you need to
include this to your jsregistry.xml ::

    <javascript authenticated="False" cacheable="True" compression="safe" conditionalcomment="" 
                cookable="True" enabled="True" expression=""
                id="++resource++collective.js.moment/lang/nl.js" inline="False"/>


About moment.js
===============

A lightweight (4.8k) javascript date library for parsing, manipulating,
and formatting dates.

You can find the code of moment.js on github_.

Credits
=======

Companies
---------

|fourdigits|_

* `Contact us <mailto:info@fourdigits.nl>`_

Authors
-------

- Franklin Kingma aka kingel <franklin@fourdigits.nl>

.. Contributors

.. |fourdigits| image:: http://www.fourdigits.nl/++theme++fourdigits.theme/images/logo.png
.. _fourdigits:  http://www.fourdigits.nl
.. _moment.js: http://momentjs.com/
.. _github: https://github.com/timrwood/moment/
