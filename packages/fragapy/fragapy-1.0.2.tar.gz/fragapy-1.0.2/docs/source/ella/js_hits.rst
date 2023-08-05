.. _js_hits:

====================
JavaScript HitCounts
====================

Ella's HitCount implementation is nice but sucks a little when you need to
cache the pages as a whole. When this happens, your hitcounts get lost :(

To avoid it, we offer JavaScript reimplementation solving the problem.

Instead of solving the hit in the Django template, we use tracking image
that fires an unseen request to a view which simply increases the HitCount
of the placement.

Installation
============

First, add ``fragapy.ella.js_hits`` to your ``INSTALLED_APPS``.

Then, make your ``urls.py`` look similar to this::

    urlpatterns = patterns('',
        ...
        (r'^hc/', include('fragapy.ella.js_hits.urls')),
        ...
    )
    
Usage
=====

Usage is very easy, you only need to add the following piece of Django in your
``page/object.html`` template::

    {% js_hitcount placement %}
    
This results in something like this being rendered::

    <!-- JS HITS -->
    <script type="text/javascript">var t=new Image();t.src="/hc/hit/46054/?1319720968.942793";</script>
    <noscript>&lt;img src="/hc/hit/46054/?1319720968.942793" /&gt;</noscript>
    <!-- /JS HITS -->
    
What does that do? If browser supports JavaScript, image will be created on backgroud 
with src pointing to our view. This fires up the server view which increases
the ``HitCount`` for the ``Placement``. If browser doesn't support the JavaScript
he will render the **<noscript>** alternative with same result.

Because we want to count the hit with the best accuracy possible, it is recommended
that you place the ``js_hitcount`` templatetag right before the **</body>** in 
your template.
