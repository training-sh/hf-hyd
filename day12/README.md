unit testing starter

a test suit with more than one test class

```
def add (a, b): return a + b

# Write a test class for it, 

# creater a test class TestMathFunction(......)
#     setup, teardown, test_add 

class TestMathFunction(unittest.TestCase):
    def setUp(self):
        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    def test_add(self):
        result = add ( 1, 2)
        #                actual value, expected
        self.assertEqual(result, 3)

```

```
import unittest

suite = unittest.TestSuite()

suite.addTests(
    unittest.defaultTestLoader.loadTestsFromTestCase(TestShoppingCart)
)

suite.addTests(
    unittest.defaultTestLoader.loadTestsFromTestCase(TestMathFunction)
)

result = unittest.TextTestRunner(verbosity=2).run(suite)

print("Tests run:", result.testsRun)
print("Successful:", result.wasSuccessful())
```
