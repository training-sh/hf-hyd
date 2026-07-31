unit testing starter

a test suit with more than one test class

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
