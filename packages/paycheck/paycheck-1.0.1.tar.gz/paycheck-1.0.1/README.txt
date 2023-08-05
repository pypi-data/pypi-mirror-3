Hey! PayCheck!
--------------

PayCheck is a half-baked implementation of
`ScalaCheck <http://code.google.com/p/scalacheck/>`_, which itself is an
implementation of
`QuickCheck <http://www.cs.chalmers.se/~rjmh/QuickCheck/>`_ for
Haskell. PayCheck is useful for defining a specification of what a
function
should do, rather than testing its results for a given input.

Thanks to gcross for some of the `more recent
changes <http://github.com/gcross/paycheck/tree/master>`_

Installing PayCheck
~~~~~~~~~~~~~~~~~~~

::

    <code>
    sudo easy_install paycheck
    </code>

That’s it. Get going.

A Quick Example
~~~~~~~~~~~~~~~

Let’s steal an example right from ScalaCheck. Here are the string
functions
ported to PayCheck. See what’s going on? We’re defining the types of the
parameters in with\_checker, then values of that type are getting passed
to the
function.

::

    <code>
    import unittest
    from paycheck import with_checker

    class TestStrings(unittest.TestCase):
        """
        More-or-less a direct port of the string testing example from the ScalaCheck
        doc at: http://code.google.com/p/scalacheck/
        """

        @with_checker(str, str)
        def test_starts_with(self, a, b):
            self.assertTrue((a+b).startswith(a))

        @with_checker(str, str)
        def test_ends_with(self, a, b):
            self.assertTrue((a+b).endswith(b))

        # Is this really always true?
        @with_checker(str, str)
        def test_concat(self, a, b):
            self.assertTrue(len(a+b) > len(a))
            self.assertTrue(len(a+b) > len(b))

        @with_checker(str, str)
        def test_substring2(self, a, b):
            self.assertEquals( (a+b)[len(a):], b )

        @with_checker(str, str, str)
        def test_substring3(self, a, b, c):
            self.assertEquals((a+b+c)[len(a):len(a)+len(b)], b)

    if __name__ == '__main__':
        unittest.main()
    </code>

Then give the ol’ test a run. You’ll likely see a problem:

::

    <code>
    $ python test_strings.py
    F....
    ======================================================================
    FAIL: test_concat (__main__.TestStrings)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "paycheck/checker.py", line 11, in wrapper
        test_func(self, *v)
      File "test_strings.py", line 20, in test_concat
        self.assertTrue(len(a+b) > len(a))
    AssertionError: Failed for input ('UGzo2LP<(9Gl_*o*GH$H<+{wPiNk?', '')

    ----------------------------------------------------------------------
    Ran 5 tests in 0.051s

    FAILED (failures=1)
    </code>

As predicted, test*concat has bombed; note that PayCheck is nice
enough to tell you which inputs caused the problem. In this case, we
see that propety test*concat fails for the empty string, which is caused
by the fact that we used “>” instead of “>=”.

Nested and More Complex Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Container and nested types are specified to PayCheck “by analogy”.
That is, unlike scalar types, which are specified by giving the type
that you want, container types are specified by creating a non-empty
container of the type you want which contains a specification of the
type that you want generated containers to contain; note that the
contained element is itself allowed to be a container, allowing for
arbitrarily nested types. PayCheck will infer from your containers
the type of container and contained elements that you want to
generate. This includes dictionaries: it will look at the first
key/value mapping that it sees and infer from it both the key type and
the value type. Containers will be generated with between 0 and
paycheck.generator.LIST\_LEN elements.

The following examples illustrate how this works:

::

    <code>
    import unittest
    from paycheck import with_checker

    class TestTypes(unittest.TestCase):

        @with_checker(int)
        def test_int(self, i):
            self.assertTrue(isinstance(i, int))

        @with_checker([int])
        def test_get_list(self, list_of_ints):
            self.assertTrue(isinstance(list_of_ints, list))
            for i in list_of_ints:
                self.assertTrue(isinstance(i, int))

        @with_checker([{str: int}])
        def test_list_of_dict_of_int_string(self, list_of_dict_of_int_string):
            self.assertTrue(isinstance(list_of_dict_of_int_string, list))

            for dict_of_int_string in list_of_dict_of_int_string:
                self.assertTrue(isinstance(dict_of_int_string, dict))

                for key, value in dict_of_int_string.items():
                    self.assertTrue(isinstance(key, str))
                    self.assertTrue(isinstance(value, int))

    if __name__ == '__main__':
        unittest.main()
    </code>

