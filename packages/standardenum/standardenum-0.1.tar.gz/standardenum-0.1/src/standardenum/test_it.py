import unittest

class Tests(unittest.TestCase):
    def _getTarget(self):
        from standardenum import StandardEnum
        return StandardEnum

    def test_it(self):
        target = self._getTarget()
        dummy = type('dummy', (target,), 
            dict(
                A=1,
                B=2,
                C=3,
            ))
        self.assertTrue(hasattr(dummy, 'A'))
        self.assertTrue(hasattr(dummy, 'B'))
        self.assertTrue(hasattr(dummy, 'C'))


    def test_int(self):
        target = self._getTarget()
        dummy = type('dummy', (target,), 
            dict(
                A=1,
                B=2,
                C=3,
            ))
        self.assertEqual(int(getattr(dummy, 'A')), 1)
        
