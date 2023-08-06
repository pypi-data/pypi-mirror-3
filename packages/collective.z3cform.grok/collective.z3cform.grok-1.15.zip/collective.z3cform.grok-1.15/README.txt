Introduction
=============

    This package enables the use of z3c forms in grok.View style inside a plone environment.

    Note that you have two wrappers and a basic form class:

    - *FormWrapper* to use the basic ``z3c.form`` template
    - *PloneFormWrapper*  is a basic z3c.form wrapper with some plone integration (fieldsets & kss) (from ``plone.app.z3cform``)
    - *PloneForm*  is a basic z3c.form with some plone integration (fieldsets & groups) (from plone.app.z3cform)
    - A *TestCase* to test your code with z3cform.grok with either using directly itself or by sublassing it

.. contents::

Credits
======================================
|makinacom|_

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact us <mailto:python@makina-corpus.org>`_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com

Basic Usage
=============

Declare a form in 'foo.py' module
::


    >>> import plone.z3cform.fieldsets.extensible.ExtensibleForm$
    >>> import z3c.form.form.Form
    >>> class Myform(plone.z3cform.fieldsets.extensible.ExtensibleForm, z3c.form.form.Form):
    ...    """A z3c.form"""
    ...    ingoreContext = True or False # override me

Note that ``collective.z3cform.grok.grok.PloneForm`` is a shortcut to the previous declaration, see implementation.

Then a Wrapper
::

    >>> from collective.z3cform.grok.grok import PloneFormWrapper
    >>> class myview(PloneFormWrapper):
    ...     form = Myform


Write a basic template, in foo_templates/myview.py, for example:
::

    <tal metal:use-macro="context/main_template/macros/master">
      <html xmlns="http://www.w3.org/1999/xhtml"
        xmlns:tal="http://xml.zope.org/namespaces/tal"
        xmlns:metal="http://xml.zope.org/namespaces/metal"
        xmlns:i18n="http://xml.zope.org/namespaces/i18n"
        i18n:domain="nmd.sugar.forms"
        xml:lang="en" lang="en"
        tal:define="lang language"
        tal:attributes="lang lang; xml:lang lang">
        <body>
          <metal:main fill-slot="body">
            <tal:block tal:content="structure python:view.render_form()"></tal:block>
          </metal:main>
        </body>
      </html>
    </tal>


Et voila, you can access your form @

    - http://url/@@myview

Basic grok testing in a third party package
=============================================

Import the basic testcase
::

    >>> from collective.z3cform.grok.tests.test_doctests import DocTestCase as dt
    >>> from collective.z3cform.grok.tests.test_doctests import collective_z3cform_grok_setUp
    >>> from collective.z3cform.grok.tests.test_doctests import collective_z3cform_grok_tearDown

Compose a testcase with one of your favourite testcases
::

    >>> class DocTestCase(MyFunctionalTestCase, dt):
    ...    def setUp_hook(self, *args, **kwargs):
    ...        MyFunctionalTestCase.setUp(self)
    ...    def tearDown_hook(self, *args, **kwargs):
    ...        MyFunctionalTestCase.tearDown(self)
    ...    def afterSetUp(self):
    ...        """."""
    ...        MyFunctionalTestCase.afterSetUp(self)
    ...

Make a doc_suite soap assembling the whole
::

    >>> def test_doctests_suite(directory=None, globs=None, suite=None, testklass=None):
    ...     if not testklass: testklass=DocTestCase
    ...     if not directory:
    ...         directory, _f = os.path.split(os.path.abspath(__file__))
    ...     elif os.path.isfile(directory):
    ...         directory = os.path.dirname(directory)
    ...     files = [os.path.join(directory, f) for f in os.listdir(directory)
    ...                                   if f.endswith('.txt')]
    ...     if not globs:
    ...         globs={}
    ...     g = globals()
    ...     for key in g:
    ...         globs.setdefault(key, g[key])
    ...     directory = directory
    ...
    ...     if not suite:
    ...         suite = unittest.TestSuite()
    ...     if files:
    ...         options = doctest.REPORT_ONLY_FIRST_FAILURE |\
    ...                   doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    ...         for test in files:
    ...             ft = ztc.ZopeDocFileSuite(
    ...                 test,
    ...                 test_class=testklass,
    ...                 optionflags=options,
    ...                 globs=globs,
    ...                 setUp=collective_z3cform_grok_setUp,
    ...                 tearDown=collective_z3cform_grok_tearDown,
    ...                 module_relative = False,
    ...             )
    ...             suite.addTest(ft)
    ...     return suite
    >>> def test_suite():
    ...     """."""
    ...     suite = unittest.TestSuite()
    ...     return test_doctests_suite(suite=suite)


 Et voila, all files ending with txt in the tests directory will be tested with that magic TestCase.



