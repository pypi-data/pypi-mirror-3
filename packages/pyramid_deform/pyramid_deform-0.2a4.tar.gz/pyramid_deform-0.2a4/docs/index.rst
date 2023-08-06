pyramid_deform
==============

``pyramid_deform`` provides bindings for the Pyramid web framework to the
`Deform <http://docs.repoze.org/deform>`_ form library.

Installation
------------

Install using setuptools, e.g. (within a virtualenv)::

  $ easy_install pyramid_deform

Configuring translations
------------------------

pyramid_deform provides an ``includeme`` hook that will set up translation
paths so that the translations for deform and colander are registered.  It
also adds a Pyramid static view for the deform JavaScript and CSS resources.
To use this in your project, add ``pyramid_deform`` to the
``pyramid.includes`` in your PasteDeploy configuration file.  An example::

  [myapp:main]
  ...
  pyramid.includes = pyramid_debugtoolbar pyramid_tm pyramid_deform

Configuring template search paths
---------------------------------

pyramid_deform allows you to add template search paths in the
configuration.  An example::

  [myapp:main]
  ...
  pyramid_deform.template_search_path = myapp:templates/deform

Thus, if you put a ``form.pt`` into your application's
``templates/deform`` directory, that will override deform's default
``form.pt``.

FormView Usage
--------------

Consider this `colander
<http://docs.pylonsproject.org/projects/colander/en/latest/>`_ schema::

  from colander import Schema, SchemaNode, String
  from deform.widget import RichTextWidget, TextAreaWidget

  class PageSchema(Schema):
      title = SchemaNode(String())
      description = SchemaNode(
          String(),
          widget=TextAreaWidget(cols=40, rows=5),
          missing=u"",
          )
      body = SchemaNode(
          String(),
          widget=RichTextWidget(),
          missing=u"",
          )

You can then write a ``PageEditView`` using
``pyramid_deform.FormView`` like this::

  from pyramid_deform import FormView

  class PageEditView(FormView):
      schema = PageSchema()
      buttons = ('save',)

      def save_success(self, appstruct):
          context = self.request.context
          context.title = appstruct['title']
          context.description = appstruct['description']
          context.body = appstruct['body']
          self.request.session.flash(u"Your changes have been saved.")
          return HTTPFound(location=self.request.path_url)

Note that ``save_success`` is only called when the form input
validates.  E.g. it's not called when the ``title`` is left blank, as
it's a required field.

The ``PageEditView`` is registered like any other Pyramid view.  Maybe
like this::

  from myapp.resources import Page

  config.add_view(
      PageEditView,
      context=Page,
      name='edit',
      permission='edit',
      renderer='myapp:templates/form.pt',
      )

Your template in ``myapp:templates/form.pt`` will receive ``form`` as
a variable: this is the rendered form.  Your template might look
something like this::

  <html>
    <head>
    <!-- CSS -->
    <tal:block repeat="reqt css_links|[]">
      <link rel="stylesheet" 
            href="${request.static_url('deform:static/%s' % reqt')}" 
            type="text/css" />
    </tal:block>
    <!-- JavaScript -->
    <tal:block repeat="reqt js_links|[]">
      <script type="text/javascript"
              src="${request.static_url('deform:static/%s' % reqt)}"
       ></script>
    </tal:block>
    </head>
    <body>
      <h1>Edit ${context.title}</h1>
      <form tal:replace="structure form" />
    </body>
  </html>

Wizard
------

XXX

CSRF Schema
-----------

::
    >>> class LoginSchema(CSRFSchema):
    >>>     pass
    >>> schema = LoginSchema.get_schema(self.request)


SessionFileUploadTempStore
--------------------------

A Deform "FileUploadTempStore" which uses the Pyramid sessioning machinery
and files on disk to store file uploads in the case of a validation failure
exists in this package at :class:`pyramid_deform.SessionFileUploadTempStore`.

Usage::

   from pyramid_deform import SessionFileUploadTempStore
   from colander import Schema
   import deform.widget
   import deform.schema
   import colander

   @colander.deferred
   def upload_widget(node, kw):
       request = kw['request']
       tmpstore = SessionFileUploadTempStore(request)
       return deform.widget.FileUploadWidget(tmpstore)

   class FileSchema(Schema):
       file = colander.SchemaNode(
           deform.schema.FileData(),
           widget = upload_widget,
           )

   def aview(request):
       schema = schema.bind(request=request)
       ...

To use the tempstore you will have to put a ``pyramid_deform.tempdir``
setting in your Pyramid's settings (usually in the ``.ini`` file that you use
to start your application).  This must point to an existing directory.  You
must also configure a Pyramid session factory.

Note that the directory named by ``pyramid_deform.tempdir`` will accrue lots
of garbage.  The tempstore doesn't clean up after itself.  You'll need to set
up a cron job or equivalent to delete files older than a day or so from that
directory.

Reporting Bugs / Development Versions
-------------------------------------

Visit https://github.com/Pylons/pyramid_deform/issues to report bugs.
Visit https://github.com/Pylons/pyramid_deform to download development or
tagged versions.

Indices and tables
------------------

* :ref:`modindex`
* :ref:`search`
