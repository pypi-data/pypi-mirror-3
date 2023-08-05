Django Dirbrowser
=================
**Django app for browse a local server direcotry.**

This app is user to give acces to a local directory and still using django auth,
django templates and django middleware.

Requires django version 1.3 or greater.

.. contents:: Contents
    :depth: 5

Installation
------------
#. Install or add ``django-dirbrowser`` to your Python path.

   pip install django-dirbrowser

or with wasy_intall

   easy_install django-dirbrowser

Usage
-----

#. Add ``dirbrowser`` to your ``INSTALLED_APPS`` setting.

#. Add dirbrowse serve to your project's ``urls.py`` file::


    from dirbrowser.views import serve

    (r'^browse/(?P<path>.*)$', serve, {'document_root': CURRENT_DIR}),

#. Or personalize it on your own views::

    from dirbrowser.views import serve

    def mybrowser(reques, path):
        extra_context = {.. some extra vars ..}

        return serve(request, document_root='path_to_my_root_dir',
                    template="custom_template.html",
                    extra_context=extra_context)

The ``serve`` view accepts the parameters:

- document_root : Path to the root directory to serve
- template : Template used to show index page (if show_indexes is True)
- extra_context : Extra context to the template
- show_indexes : if True show the directory index page. Default is False


