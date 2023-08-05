Introduction
============

``horae.sphinx.grok`` is an extension for the `Sphinx <http://sphinx.pocoo.org>`_
documentation generator. It provides two new autodoc directives ``autogrok`` and
``autogrokfunction``. By using those directives instead of the stock ``autoclass``
and ``autofunction`` ones additional grok specific information is given about
the class or function.

If the ``autogrok`` directive is as an example used on the following class definition::

    class ExampleAdapter(grok.Adapter):
        """
        An adapter demonstrating the autogrok directive
        """
        grok.context(IAdaptee)
        grok.implements(ISomeFunctionality)
        grok.name('example')

The reStructuredText output of the docstring would look like this::

    An adapter demonstrating the autogrok directive
    
    :context:
        :class:`IAdaptee`
    :implements:
        :class:`ISomeFunctionality`
    :name:
        example

The ``autogrokfunction`` is doing the same for functions::

    @grok.adapter(IAdaptee, name="example")
    @grok.implementer(ISomeFunctionality)
    def example_adapter_factory(context):
        """
        An adapter factory demonstrating the autogrokfunction directive
        """
        return ExampleAdapter(context)

Which would result in::

    An adapter factory demonstrating the autogrokfunction directive
    
    :context:
        :class:`IAdaptee`
    :implements:
        :class:`ISomeFunctionality`
    :name:
        example
