Introduction
============

``horae.datetime`` provides `zope.formlib <http://pypi.python.org/pypi/zope.formlib>`_
input widgets for ``Date`` and ``Datetime`` fields of `zope.schema
<http://pypi.python.org/pypi/zope.schema>`_. Both widgets use the
`datepicker widget of jQuery UI <http://jqueryui.com/demos/datepicker>`_
to select the date. The ``Datetime`` widget additionally provides two
input fields to enter the hour and minute for the time. The hour and
minute fields are enhanced by the `Spinbox jQuery plugin
<http://www.softwareunity.com/jquery/JQuerySpinBtn>`_.

Usage
=====

The widgets may either be registered through ``ZCML`` as new default input
widgets for ``Date`` and ``Datetime`` fields or by defining the widget as
``custom_widget`` on a `zope.formlib <http://pypi.python.org/pypi/zope.formlib>`_
form. Registration as default widget has to be done either in an ``overrides.zcml``
or the registrations have to be bound to a specific browser layer.

Registration using the ``overrides.zcml`` would look like this::

    <configure xmlns='http://namespaces.zope.org/zope'>
    
      <view
          type="zope.publisher.interfaces.browser.IBrowserRequest"
          for="zope.schema.interfaces.IDatetime"
          provides="zope.app.form.interfaces.IInputWidget"
          factory="horae.datetime.widget.DatetimeWidget"
          permission="zope.Public"
          />
    
      <view
          type="zope.publisher.interfaces.browser.IBrowserRequest"
          for="zope.schema.interfaces.IDate"
          provides="zope.app.form.interfaces.IInputWidget"
          factory="horae.datetime.widget.DateWidget"
          permission="zope.Public"
          />
    
    </configure>

Dependencies
============

* `fanstatic <http://pypi.python.org/pypi/fanstatic>`_
* `zope.fanstatic <http://pypi.python.org/pypi/zope.fanstatic>`_
* `js.jquery <http://pypi.python.org/pypi/js.jquery>`_
* `js.jqueryui <http://pypi.python.org/pypi/js.jqueryui>`_
