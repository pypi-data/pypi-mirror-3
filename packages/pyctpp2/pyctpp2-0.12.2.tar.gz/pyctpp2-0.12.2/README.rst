.. contents::
    :depth: 2

Example of usage
================

    Make template file *hello.tmpl*::

        Foo: <TMPL_var foo.bar>
        Spam: <TMPL_var foo[spam]>
        Array:
            <TMPL_var array[0].key>
            <TMPL_var array[1]['key']>

    Create Python script::

        #!/usr/bin/env python

        import pyctpp2

        if __name__ == '__main__':
            engine = pyctpp2.Engine()

            template = engine.parse('hello.tmpl')

            result = template.render({
                'foo': { 'bar': 'baz' },
                'spam': 'bar',
                'array': [
                    { 'key': 'first' },
                    { 'key': 'second' } ]
            })

    Check output::

        Foo: baz
        Spam: baz
        Array:
            first
            second

    See ``pydoc pyctpp2.Engine`` and  ``pydoc pyctpp2.Template`` for more information.

.. _CTPP2: http://ctpp.havoc.ru/

