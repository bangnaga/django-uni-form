===
FAQ
===

How did this all get started?
=============================

In December 2008, while working for `NASA's Science Mission Directorate`_, my team began to use Django_ and Pinax_. We needed to make all the forms in Pinax `Section 508`_ compatible, and the thought of going through all of 30+ forms and rewriting `{{ form }}` as a block of `{% for field in form %}` with all the template logic seemed like way too much work.

So with the encouragement of Katie Cunningham, `James Tauber`_ and `Jannis Leidel`_ I took the Django docs on forms and combined it with Dragan Babic's excellent Uni-Form css/javascript library and created the ubiquitous `as_uni_form` filter. After that, fixing all the forms in Pinax to be section 508 compliant was trivial.

Not long before PyCon 2009 James Tauber suggested the `{% uni_form form helper %}` API, where one could trivially create forms without writing any HTML.

At PyCon 2009 Jannis Leidel helped me through releasing the 0.3 release of django-uni-form on PyPI. It was also at that PyCon that I believe I switched the library from Google Project Hosting to Github.

.. _Django: http://djangoproject.com
.. _Pinax: http://pinaxproject.com
.. _`NASA's Science Mission Directorate`: http://science.nasa.gov
.. _`Section 508`: http://en.wikipedia.org/wiki/Section_508
.. _`James Tauber`: http://jtauber.com/
.. _`Jannis Leidel`: http://twitter.com/jezdez
