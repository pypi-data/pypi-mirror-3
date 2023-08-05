Import requirements::

    >>> import yafowil.loader
    >>> import yafowil.widget.autocomplete
    >>> from yafowil.base import factory

Render plain, source is string::

    >>> widget = factory('autocomplete', name='root', 
    ...                  props={'source': 'http://www.foo.bar/baz'})
    >>> pxml(widget())
    <div class="yafowil-widget-autocomplete">
      <input class="autocomplete" id="input-root" name="root" type="text"/>
      <div class="autocomplete-source hiddenStructure">http://www.foo.bar/baz</div>
      <div class="autocomplete-params hiddenStructure">delay,300|minLength,1|type,remote</div>
    </div>
    <BLANKLINE>
            
Render plain, source is list::

    >>> widget = factory('autocomplete', name='root', 
    ...                  props={'source': ['foo', 'bar']})
    >>> pxml(widget())
    <div class="yafowil-widget-autocomplete">
      <input class="autocomplete" id="input-root" name="root" type="text"/>
      <div class="autocomplete-source hiddenStructure">foo|bar</div>
      <div class="autocomplete-params hiddenStructure">delay,300|minLength,1|type,local</div>
    </div>
    <BLANKLINE>

Render plain, source is callable::

    >>> def test_source(widget, data):
    ...     return 'http://from.callable/'
    >>> widget = factory('autocomplete', name='root', 
    ...                  props={'source': test_source})
    >>> pxml(widget())
    <div class="yafowil-widget-autocomplete">
      <input class="autocomplete" id="input-root" name="root" type="text"/>
      <div class="autocomplete-source hiddenStructure">http://from.callable/</div>
      <div class="autocomplete-params hiddenStructure">delay,300|minLength,1|type,remote</div>
    </div>
    <BLANKLINE>

Extraction::

    >>> data = widget.extract({'root': 'abc'})
    >>> data.printtree()
    <RuntimeData root, value=<UNSET>, extracted='abc' at ...>

Render, invalid source type::

    >>> widget = factory('autocomplete', name='root', 
    ...                  props={'source': None})
    >>> widget()
    Traceback (most recent call last):
    ...
    ValueError: resulting source must be tuple/list or string
