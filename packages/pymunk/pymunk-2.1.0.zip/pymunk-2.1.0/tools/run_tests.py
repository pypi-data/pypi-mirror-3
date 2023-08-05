
import sys
sys.path.insert(0,'..')
import unittest

import tests

ts = ["test_vec2d", "test_body", "test_common", "test_constraint", "test_shape", "test_space"]

suite = unittest.TestSuite()   
for t in ts:
    suite.addTests(unittest.TestLoader().loadTestsFromName("tests." + t))

if len(sys.argv) > 1:
    m = sys.argv[1]

    for t in suite:
        for x in t:
            if m in str(x.id()):
                unittest.TextTestRunner(verbosity=2).run(x)
            #dir(x)
else:
    unittest.TextTestRunner(verbosity=2).run(suite)

