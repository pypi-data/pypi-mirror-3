Introduction
============

The ``horae.cache`` package provides simple decorators for caching. There are decorators
available for caching vocabularies (contextual or global) and for caching method and
function output on the request.

Usage
=====

Vocabulary
----------

There are three different ways to cache a vocabulary:

**Global cache**
  Caches the vocabulary globally
**Contextual cache**
  Caches the vocabulary in the given context
**Contextual parent cache**
  Caches the vocabulary in the defined parent of the given context

Every type of cache has a corresponding invalidation function to clear the cache for
the given vocabulary. This is especially usable when using dynamic vocabularies which
change over time for example a vocabulary of content objects of a given type::

    import grok
    
    from zope.schema import vocabulary
    from some.module.interfaces import ISampleContent
    from horae.cache import vocabulary
    
    @vocabulary.cache_global
    def all_sample_contents(context):
        # find all content objects of type ISampleContent
        return vocab
    vocabulary.getVocabularyRegistry().register(
        'allsamplecontents',
        all_sample_contents)
    
    @grok.subscribe(ISampleContent, grok.IObjectModifiedEvent)
    @grok.subscribe(ISampleContent, grok.IObjectMovedEvent)
    def invalidate_all_sample_contents_cache(obj, event):
        vocabulary.invalidate_global(all_sample_contents)

The contextual cache is used for context specific vocabularies and are used the same way
as the global cache::

    @vocabulary.cache_contextual
    def sample_contents_in_context(context):
        # find all content objects of type ISampleContent
        # in the given context
        return vocab
    vocabulary.getVocabularyRegistry().register(
        'samplecontentsincontext',
        sample_contents_in_context)
    
    @grok.subscribe(ISampleContent, grok.IObjectModifiedEvent)
    @grok.subscribe(ISampleContent, grok.IObjectMovedEvent)
    def invalidate_sample_contents_in_context_cache(obj, event):
        # iterate over all the parents of the object and call:
        vocabulary.invalidate_contextual(parent,
                                         sample_contents_in_context)

The contextual parent cache is used slightly different. It takes an optional interface as
a parameter to find the parent to cache the vocabulary on. The cache steps up the object
hierarchy until it finds a parent implementing the given interface. If no interface is
given the immediate parent of the vocabulary context is taken as the cache context. An
example usage may look like this::

    from some.module.interfaces import ISampleContainer

    @vocabulary.cache_contextual_parent(ISampleContainer)
    def sample_contents_in_parent_of_context(context):
        # find all content objects of type ISampleContent in
        # the first found parent implementing ISampleContainer
        # of the given context
        return vocab
    vocabulary.getVocabularyRegistry().register(
        'samplecontentsinparentofcontext',
        sample_contents_in_parent_of_context)
    
    @grok.subscribe(ISampleContent, grok.IObjectModifiedEvent)
    @grok.subscribe(ISampleContent, grok.IObjectMovedEvent)
    def invalidate_sample_contents_in_context_cache(obj, event):
        vocabulary.invalidate_contextual_parent(
            obj,
            ISampleContainer,
            sample_contents_in_parent_of_context)

Request
-------

To cache the output of a function for the current request simply add the
``horae.cache.request.cache`` decorator::

    from horae.cache import request
    
    @request.cache()
    def some_heavy_computation(arg1, arg2, kwarg1=True, kwarg2=True):
        # do the heavy computation
        return result_of_the_heavy_computation

The ``horae.cache.request.cache`` takes two optional arguments ``args`` and ``kwargs``
using which one may define what arguments and/or keyword arguments are relevant for the
output. If in the example above the output would be the same if arg2 and kwarg2 was set
differently the decorator could look like this to improve the caching::

    @request.cache(args=(0,), kwargs=('kwarg1',))
    def some_heavy_computation(arg1, arg2, kwarg1=True, kwarg2=True):
        # do the heavy computation
        return result_of_the_heavy_computation

Dependencies
============

* `plone.memoize <http://pypi.python.org/pypi/plone.memoize>`_
* `grok <http://pypi.python.org/pypi/grok>`_
