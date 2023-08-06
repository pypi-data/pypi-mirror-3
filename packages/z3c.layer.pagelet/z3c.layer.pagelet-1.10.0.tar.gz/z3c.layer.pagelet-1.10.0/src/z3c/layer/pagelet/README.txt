==============================
Pagelet-based Layer for Zope 3
==============================

This package contains the pagelet layer. This layer supports a correct set of
component registration and can be used for inheritation in custom skins.

Right now the default implementation in Zope3 has different restriction in the
traversal concept and use to much registration on the default layer.

Important
---------

This layer ia based on the pagelet pattern. This means every page e.g. the
error page is based on the pagelet concept.


``IPageletBrowserLayer`` Layer
------------------------------

The pagelet layer is useful for build custom presentation skins without access
to ZMI menus like ``zmi_views`` etc. This means there is no menu item
registred if you use this layer.

This layer is *NOT* derived from ``IDefaultBrowserLayer`` layer. Therefore it
provides only a minimal set of the most important public views such as
``@@absolute_url`` which get registered in zope packages for the IHTTPRequest
and IBrowserRequest.  Next to this views, this package will only provide error
views and traversers which are normaly regsitered in the following zope
packages:

- ``zope.app.http.exception``
- ``zope.app.publication``
- ``zope.browserresource``
- ``zope.traversing``

Note, this package does not depend on all the packages described above. We only
need to depend on the same interfaces where this package will define views and
traversers for.


Testing
-------

For testing the ``IPageletBrowserLayer`` layer we use the testing skin defined
in the tests package which uses the ``IPageletBrowserLayer`` layer as the only
base layer.  This means, that our testing skin provides only the views defined
in the minimal package and it's testing views defined in tests.

Login as manager first:

  >>> from zope.app.wsgi.testlayer import Browser
  >>> manager = Browser()

Check if we can access the ``page.html`` view which is registred in the
``ftesting.zcml`` file with our skin:

  >>> skinURL = 'http://localhost/++skin++PageletTestSkin'
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> manager.open(skinURL + '/page.html')
  >>> manager.url
  'http://localhost/++skin++PageletTestSkin/page.html'

  >>> print manager.contents
  <!DOCTYPE...
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
  <title>PageletTestLayout</title>
  </head>
  <body>
    test page
  <BLANKLINE>
  </body>
  </html>
  <BLANKLINE>

Not Found
~~~~~~~~~

Now check the not found page which is a exception view on the exception
``zope.publisher.interfaces.INotFound``:

  >>> manager.open(skinURL + '/foobar.html')
  Traceback (most recent call last):
  ...
  httperror_seek_wrapper: HTTP Error 404: Not Found

  >>> print manager.contents
  <!DOCTYPE...
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
  <title>PageletTestLayout</title>
  </head>
  <body>
    <div>
    <br />
    <br />
    <h3>
      The page you are trying to access is not available
    </h3>
    <br />
    <b>
      Please try the following:
    </b>
    <br />
    <ol>
      <li>
        Make sure that the Web site address is spelled correctly.
      </li>
      <li>
        <a href="javascript:history.back(1);">
          Go back and try another URL.
        </a>
      </li>
    </ol>
  </div>
  <BLANKLINE>
  </body>
  </html>
  <BLANKLINE>

User error
~~~~~~~~~~

And check the user error page which is a view registred for
``zope.exceptions.interfaces.IUserError`` exceptions:

  >>> manager.open(skinURL + '/@@usererror.html')
  >>> print manager.contents
  <!DOCTYPE ...
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
  <title>PageletTestLayout</title>
  </head>
  <body>
    <div>
    <div>simply user error</div>
  </div>
  <BLANKLINE>
  </body>
  </html>
  <BLANKLINE>

Common exception (system error)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

And check error view registred for
``zope.interface.common.interfaces.IException``, it sets the HTTP status
code to 500 if called during tests or if development mode is switched on:

  >>> manager.open(skinURL + '/@@systemerror.html')
  Traceback (most recent call last):
  HTTPError: HTTP Error 500: Internal Server Error
  >>> print manager.contents
  <!DOCTYPE...
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
  <title>PageletTestLayout</title>
  </head>
  <body>
    <div>
    <br />
    <br />
    <h3>A system error occurred</h3>
    <br />
    <b>Please contact the administrator.</b>
    <a href="javascript:history.back(1);">
      Go back and try another URL.
    </a>
  </div>
  <BLANKLINE>
  </body>
  </html>
  <BLANKLINE>

Unauthorized
~~~~~~~~~~~~

To check the ``zope.security.interfaces.IUnauthorized`` view, we use a
new unregistred user (test browser). As we have defined an
unauthenticatedPrincipal in ZCML (see tests/ftesting.zcml) ``401
Unauthorized`` is returned instead of ``403 Forbidden`` which would
show up otherwise:

  >>> unauthorized = Browser()
  >>> unauthorized.open(skinURL + '/@@forbidden.html')
  Traceback (most recent call last):
  HTTPError: HTTP Error 401: Unauthorized

  >>> print unauthorized.contents
  <!DOCTYPE ...
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
  <title>PageletTestLayout</title>
  </head>
  <body>
    <div>
    <br />
    <br />
    <h3>Unauthorized</h3>
    <br />
    <b>You are not authorized.</b>
  </div>
  </body>
  </html>

Forbidden
~~~~~~~~~

When an authorized user tries to access a URL where he does not have enough
permissions he gets a ``403 Forbidden``, the displayed page contents are the
same like ``401 Unauthorized``. When an authentication utility is registered
it might display a log-in form:

  >>> authorized = Browser()
  >>> authorized.addHeader('Authorization', 'Basic tester:tester')
  >>> authorized.open(skinURL + '/@@forbidden.html')
  Traceback (most recent call last):
  HTTPError: HTTP Error 403: Forbidden

  >>> print authorized.contents
    <!DOCTYPE ...
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
    <title>PageletTestLayout</title>
    </head>
    <body>
      <div>
      <br />
      <br />
      <h3>Unauthorized</h3>
      <br />
      <b>You are not authorized.</b>
    </div>
    </body>
    </html>
