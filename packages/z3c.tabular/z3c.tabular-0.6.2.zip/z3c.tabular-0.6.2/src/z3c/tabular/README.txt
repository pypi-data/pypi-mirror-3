==========
Form Table
==========

The goal of this package is to offer a modular table rendering library which
includes built in support for update forms. This will allow us to adapt items
rendered as table row items to forms. This could prevent to use traversable
exposed forms for such items. But this is just one of the benefits. See more
below.


Form support
------------

We need to setup the form defaults first:

  >>> from z3c.form.testing import setupFormDefaults
  >>> setupFormDefaults()

And load the formui confguration, which will make sure that all macros get
registered correctly.

  >>> from zope.configuration import xmlconfig
  >>> import zope.component
  >>> import zope.viewlet
  >>> import zope.component
  >>> import zope.app.publisher.browser
  >>> import z3c.macro
  >>> import z3c.template
  >>> import z3c.formui
  >>> xmlconfig.XMLConfig('meta.zcml', zope.component)()
  >>> xmlconfig.XMLConfig('meta.zcml', zope.viewlet)()
  >>> xmlconfig.XMLConfig('meta.zcml', zope.app.publisher.browser)()
  >>> xmlconfig.XMLConfig('meta.zcml', z3c.macro)()
  >>> xmlconfig.XMLConfig('meta.zcml', z3c.template)()
  >>> xmlconfig.XMLConfig('configure.zcml', z3c.formui)()

And load the z3c.tabular configure.zcml:

  >>> import z3c.tabular
  >>> xmlconfig.XMLConfig('configure.zcml', z3c.tabular)()


Sample data setup
-----------------

Let's create a sample container which we can use as our iterable context:

  >>> from zope.container import btree
  >>> class Container(btree.BTreeContainer):
  ...     """Sample container."""
  ...     __name__ = u'container'
  >>> container = Container()

and set a parent for the container:

  >>> root['container'] = container

and create a sample content object which we use as container item:

  >>> import zope.interface
  >>> import zope.schema
  >>> class IContent(zope.interface.Interface):
  ...     """Content interface."""
  ...
  ...     title = zope.schema.TextLine(title=u'Title')
  ...     number = zope.schema.Int(title=u'Number')

  >>> class Content(object):
  ...     """Sample content."""
  ...     zope.interface.implements(IContent)
  ...     def __init__(self, title, number):
  ...         self.__name__ = title.lower()
  ...         self.title = title
  ...         self.number = number

Now setup some items:

  >>> container[u'first'] = Content('First', 1)
  >>> container[u'second'] = Content('Second', 2)
  >>> container[u'third'] = Content('Third', 3)


FormTable setup
---------------

The ``FormTable`` offers a sub form setup for rendering items within a form.
Let's first define a form for our used items:


  >>> from z3c.form import form
  >>> from z3c.form import field
  >>> class ContentEditForm(form.EditForm):
  ...     fields = field.Fields(IContent)

Now we can define our ``FormTable`` including the SelectedItemColumn:

  >>> from z3c.table import column
  >>> import z3c.tabular.table
  >>> class ContentFormTable(z3c.tabular.table.SubFormTable):
  ...
  ...     subFormClass = ContentEditForm
  ...
  ...     def setUpColumns(self):
  ...         return [
  ...             column.addColumn(self, column.SelectedItemColumn,
  ...                              u'selectedItem', weight=1),
  ...             ]

And support the div form layer for our request:

  >>> from z3c.formui.interfaces import IDivFormLayer
  >>> from zope.interface import alsoProvides
  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> alsoProvides(request, IDivFormLayer)

Now we can render our table. As you can see the ``SelectedItemColumn`` renders
a link which knows hot to select the item:

  >>> contentSubFormTable = ContentFormTable(container, request)
  >>> contentSubFormTable.__name__ = 'view.html'
  >>> contentSubFormTable.update()
  >>> print contentSubFormTable.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="subFormTable" id="subFormTable">
    <div class="viewspace">
      <div>
      <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
          <td valign="top">
            <div>
              <table class="contents">
                <thead>
                  <tr>
                    <th>Name</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="even">
                    <td><a href="http://127.0.0.1/container/view.html?subFormTable-selectedItem-0-selectedItems=first">first</a></td>
                  </tr>
                  <tr class="odd">
                    <td><a href="http://127.0.0.1/container/view.html?subFormTable-selectedItem-0-selectedItems=second">second</a></td>
                  </tr>
                  <tr class="even">
                    <td><a href="http://127.0.0.1/container/view.html?subFormTable-selectedItem-0-selectedItems=third">third</a></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </td>
          <td valign="top">
          </td>
        </tr>
      </table>
    </div>
    </div>
    <div>
      <div class="buttons">
  <input id="subFormTable-buttons-delete"
         name="subFormTable.buttons.delete"
         class="submit-widget button-field" value="Delete"
         type="submit" />
  <input id="subFormTable-buttons-edit"
         name="subFormTable.buttons.edit"
         class="submit-widget button-field" value="Edit"
         type="submit" />
  <input id="subFormTable-buttons-cancel"
         name="subFormTable.buttons.cancel"
         class="submit-widget button-field" value="Cancel"
         type="submit" />
      </div>
    </div>
  </form>


Now we are ready to select an item by click on the link. We simulate this by
set the relevant data in the request:

  >>> selectRequest = TestRequest(form={
  ...     'subFormTable-selectedItem-0-selectedItems': 'second'})
  >>> alsoProvides(selectRequest, IDivFormLayer)
  >>> selectedItemTable = ContentFormTable(container, selectRequest)
  >>> selectedItemTable.__name__ = 'view.html'
  >>> selectedItemTable.update()
  >>> print selectedItemTable.render()
  <form action="http://127.0.0.1" method="post" enctype="multipart/form-data" class="edit-form" name="subFormTable" id="subFormTable">
    <div class="viewspace">
      <div>
      <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
          <td valign="top">
            <div>
              <table class="contents">
    <thead>
      <tr>
        <th>Name</th>
      </tr>
    </thead>
    <tbody>
      <tr class="even">
        <td><a href="http://127.0.0.1/container/view.html?subFormTable-selectedItem-0-selectedItems=first">first</a></td>
      </tr>
      <tr class="selected odd">
        <td><a href="http://127.0.0.1/container/view.html?subFormTable-selectedItem-0-selectedItems=second">second</a></td>
      </tr>
      <tr class="even">
        <td><a href="http://127.0.0.1/container/view.html?subFormTable-selectedItem-0-selectedItems=third">third</a></td>
      </tr>
    </tbody>
  </table>
            </div>
          </td>
          <td valign="top">
            <div class="tableForm">
              <form action="http://127.0.0.1" method="post" enctype="multipart/form-data" class="edit-form" name="form" id="form">
    <div class="viewspace">
        <div class="required-info">
           <span class="required">*</span>&ndash; required
        </div>
      <div>
            <div id="form-widgets-title-row" class="row required">
                <div class="label">
                  <label for="form-widgets-title">
                    <span>Title</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget">
      <input id="form-widgets-title" name="form.widgets.title" class="text-widget required textline-field" value="Second" type="text" />
  </div>
            </div>
            <div id="form-widgets-number-row" class="row required">
                <div class="label">
                  <label for="form-widgets-number">
                    <span>Number</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget">
      <input id="form-widgets-number" name="form.widgets.number" class="text-widget required int-field" value="2" type="text" />
  </div>
            </div>
      </div>
    </div>
    <div>
      <div class="buttons">
  <input id="form-buttons-apply" name="form.buttons.apply" class="submit-widget button-field" value="Apply" type="submit" />
      </div>
    </div>
  </form>
            </div>
          </td>
        </tr>
      </table>
    </div>
    </div>
    <div>
      <div class="buttons">
  <input id="subFormTable-buttons-delete" name="subFormTable.buttons.delete" class="submit-widget button-field" value="Delete" type="submit" />
  <input id="subFormTable-buttons-edit" name="subFormTable.buttons.edit" class="submit-widget button-field" value="Edit" type="submit" />
  <input id="subFormTable-buttons-cancel" name="subFormTable.buttons.cancel" class="submit-widget button-field" value="Cancel" type="submit" />
      </div>
    </div>
  </form>


Clicking the ``Edit`` button at the same time should hold the same result:

  >>> selectRequest = TestRequest(form={
  ...     'subFormTable-selectedItem-0-selectedItems': 'second',
  ...     'subFormTable.buttons.edit': 'Edit'})
  >>> alsoProvides(selectRequest, IDivFormLayer)
  >>> selectedItemTable = ContentFormTable(container, selectRequest)
  >>> selectedItemTable.__name__ = 'view.html'
  >>> selectedItemTable.update()
  >>> print selectedItemTable.render()
  <form action="http://127.0.0.1" method="post" enctype="multipart/form-data" class="edit-form" name="subFormTable" id="subFormTable">
    <div class="viewspace">
      <div>
      <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
          <td valign="top">
            <div>
              <table class="contents">
    <thead>
      <tr>
        <th>Name</th>
      </tr>
    </thead>
    <tbody>
      <tr class="even">
        <td><a href="http://127.0.0.1/container/view.html?subFormTable-selectedItem-0-selectedItems=first">first</a></td>
      </tr>
      <tr class="selected odd">
        <td><a href="http://127.0.0.1/container/view.html?subFormTable-selectedItem-0-selectedItems=second">second</a></td>
      </tr>
      <tr class="even">
        <td><a href="http://127.0.0.1/container/view.html?subFormTable-selectedItem-0-selectedItems=third">third</a></td>
      </tr>
    </tbody>
  </table>
            </div>
          </td>
          <td valign="top">
            <div class="tableForm">
              <form action="http://127.0.0.1" method="post" enctype="multipart/form-data" class="edit-form" name="form" id="form">
    <div class="viewspace">
        <div class="required-info">
           <span class="required">*</span>&ndash; required
        </div>
      <div>
            <div id="form-widgets-title-row" class="row required">
                <div class="label">
                  <label for="form-widgets-title">
                    <span>Title</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget">
      <input id="form-widgets-title" name="form.widgets.title" class="text-widget required textline-field" value="Second" type="text" />
  </div>
            </div>
            <div id="form-widgets-number-row" class="row required">
                <div class="label">
                  <label for="form-widgets-number">
                    <span>Number</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget">
      <input id="form-widgets-number" name="form.widgets.number" class="text-widget required int-field" value="2" type="text" />
  </div>
            </div>
      </div>
    </div>
    <div>
      <div class="buttons">
  <input id="form-buttons-apply" name="form.buttons.apply" class="submit-widget button-field" value="Apply" type="submit" />
      </div>
    </div>
  </form>
            </div>
          </td>
        </tr>
      </table>
    </div>
    </div>
    <div>
      <div class="buttons">
  <input id="subFormTable-buttons-delete" name="subFormTable.buttons.delete" class="submit-widget button-field" value="Delete" type="submit" />
  <input id="subFormTable-buttons-edit" name="subFormTable.buttons.edit" class="submit-widget button-field" value="Edit" type="submit" />
  <input id="subFormTable-buttons-cancel" name="subFormTable.buttons.cancel" class="submit-widget button-field" value="Cancel" type="submit" />
      </div>
    </div>
  </form>

Unless ``allowEdit`` is ``False``.
In this case the editform won't appear.

  >>> selectRequest = TestRequest(form={
  ...     'subFormTable-selectedItem-0-selectedItems': 'second',
  ...     'subFormTable.buttons.edit': 'Edit'})
  >>> alsoProvides(selectRequest, IDivFormLayer)
  >>> selectedItemTable = ContentFormTable(container, selectRequest)
  >>> selectedItemTable.__name__ = 'view.html'
  >>> selectedItemTable.allowEdit = False
  >>> selectedItemTable.update()
  >>> print selectedItemTable.render()
    <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="subFormTable" id="subFormTable">
    <div class="viewspace">
      <div>
      <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
          <td valign="top">
            <div>
              <table class="contents">
                <thead>
                  <tr>
                    <th>Name</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="even">
                    <td><a href="http://127.0.0.1/container/view.html?subFormTable-selectedItem-0-selectedItems=first">first</a></td>
                  </tr>
                  <tr class="selected odd">
                    <td><a href="http://127.0.0.1/container/view.html?subFormTable-selectedItem-0-selectedItems=second">second</a></td>
                  </tr>
                  <tr class="even">
                    <td><a href="http://127.0.0.1/container/view.html?subFormTable-selectedItem-0-selectedItems=third">third</a></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </td>
          <td valign="top">
          </td>
        </tr>
      </table>
    </div>
    </div>
    <div>
      <div class="buttons">
        <input id="subFormTable-buttons-delete"
               name="subFormTable.buttons.delete"
               class="submit-widget button-field" value="Delete"
               type="submit" />
        <input id="subFormTable-buttons-cancel"
               name="subFormTable.buttons.cancel"
               class="submit-widget button-field" value="Cancel"
               type="submit" />
      </div>
    </div>
  </form>
