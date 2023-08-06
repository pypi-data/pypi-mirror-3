.. Edit at http://rst.ninjs.org/

=================================================================
django-template-minimizer - Minimize your templates not your HTML
=================================================================

:Download: http://pypi.python.org/pypi/django-template-minimizer/
:Source: http://github.com/Charles-Kaminski/django-template-minimizer
:License: MIT

--

The ``django-template-minimizer`` project is a Django manage.py command you can install in your Django application.  Running this command minimizes your Django templates and eliminates the need to reprocess your HTML to minimize it; as the HTML is now being put together in minimized form.

The command minimizes django templates along with the html, in-line ``<script>`` javascript, and in-line ``<style>`` css inside the templates.  The command includes a minimize and an undo option.  The minimizers for html, css, and javascript are plugable so you can override or add your own.

Installing django-template-minimizer
====================================

You can install ``django-template-minimizer`` either via the Python Package Index (PyPI) or from source.

To install using ``pip`` (recommended)::

    $ pip install django-template-minimizer

To install using ``easy_install``::

    $ easy_install django-template-minimizer

Register the app in your Django project's settings file::

    import tmin
    ...
    INSTALLED_APPS += ('tmin',)

To install from source, download the source from github (http://github.com/Charles-Kaminski/django-template-minimizer/downloads).  Decompress it and put it in the folder with your django project as another django app.  Register the app in your Django project's settings file.  

Usage
-----

**Commands**::

    $ python manage.py minimizetemplates    -> help text
    $ python manage.py minimizetemplates -m -> minimize
    $ python manage.py minimizetemplates -u -> undo
    
Use these commands to minimize (or unminimize) Django templates after development.  This way, your templates are small when they are evaluated and the HTML served is already minimized; eliminiating any post-processing minimization step.  

Use the comment tags ``{# NOMINIFY #} {# ENDNOMINIFY #}`` inside your templates to wrap content you do not want minified.  

Uses the setting ``TEMPLATE_DIRS`` in your Django settings file to tell the command where to find templates to minimize.::

    TEMPLATE_DIRS = [...]

Customization
-------------

The minimizer command uses default minimizers for html, style tag embeded css, and script tag embeded javascript. You can override these and chain any number of your own minimizers using the settings below.  These settings go in the Django settings file. Custom minimizers must be functions that accept text as a string parameter and return text as a string.:: 

    JAVASCRIPT_MINIMIZERS = [my_function_1, my_function_2, ...]
    CSS_MINIMIZERS        = [my_function_3, my_function_4, ...]
    HTML_MINIMIZERS       = [my_function_5, my_function_6, ...]

To turn off a minimizer, use the following pattern::

    f = lambda x: x
    JAVASCRIPT_MINIMIZERS = [f,]

You can tell the minimizer command to add an aggressive HTML minimizer to the end of the HTML minimizer chain.  This minimizer will remove (instead of just collapse) the remaining space between '``>``' & '``<``' character. Django tags, Django variables, Script content, Style content and anything wrapped in ``{# NOMINIFY #} {# ENDNOMINIFY #}`` tags are not affected.  To do this, set the following setting to True in your Django settings file::

    ADD_AGGRESSIVE_HTML_MINIMIZER = True

Method
------

For each template, the minimizer command:  

1. Replaces any ``{# NOMINIFY #} {# ENDNOMINIFY #}`` tags and content with a unique identifier and saves the content in memory so that it is excluded from the rest of the process.

2. Remaining Django comments are removed.

3. Django tags and django variables are replaced with unique identifiers.  The tags and variables are saved in memory.  This approach "protects" the tags and variables from the minimizers.  It also allows you to use Django tags and variables inside your javascript and CSS without ill effect by the CSS or javascript minimizer.

4. HTML script tags and content are replaced with unique identifiers. The tags and content are saved in memory for additional processing.  The type attribute for the script tag is checked to see if the script content is javascript.  If no type is provided, then javascript is assumed.  Any javascript is then run through the javascript minimizers.

5. An almost identical process to step 4 is implemented on the HTML style tags for css.

6. If the ``ADD_AGGRESSIVE_HTML_MINIMIZER`` flag is set to True, then an additional HTML minimizer is added to the HTML minimizer chain.  This additional minimizer removes any left over space between the '``>``' and '``<``' characters.

7. The remaining text (with the identifiers) is run through the html minimizers.

8. All of the content saved in memory and associated with unique identifiers are put back.

9. The original template is moved to an archive folder.  The minimized template is put in the original place location.

Limitations
-----------

Use the ``{# NOMINIFY #} {# ENDNOMINIFY #}`` comment tags to overcome these limiations.

1. The default javascript and css minimizers do not handle script tags inside script tags or style tags inside style tags; an unusual occurance.

    | ``eg: <script>bla bla<script>bla</script>bla</script>``

2. The minimizer collapses all white space not in a django tag, django variable, javascript, or inline css.  This includes whitespace inside ``<pre>``, ``<textarea>``, and similar tags; and whitespace inside html attributes.