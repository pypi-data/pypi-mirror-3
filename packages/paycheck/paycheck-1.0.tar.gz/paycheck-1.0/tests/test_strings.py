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

    @with_checker(str, str)
    def test_concat(self, a, b):
        self.assertTrue(len(a+b) >= len(a))
        self.assertTrue(len(a+b) >= len(b))

    @with_checker(str, str)
    def test_substring2(self, a, b):
        self.assertEqual( (a+b)[len(a):], b )
    
    @with_checker(str, str, str)
    def test_substring3(self, a, b, c):
        self.assertEqual((a+b+c)[len(a):len(a)+len(b)], b)

tests = [TestStrings]

if __name__ == '__main__':
    unittest.main()
