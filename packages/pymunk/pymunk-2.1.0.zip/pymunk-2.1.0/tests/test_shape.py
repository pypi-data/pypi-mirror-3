import pymunk as p
from pymunk.vec2d import Vec2d
import unittest

####################################################################

class UnitTestShape(unittest.TestCase):
    def setUp(self):
        p.reset_shapeid_counter()
    
    def testShape(self):
        s = p.Space()
        b = p.Body(10,10)
        b.position = 10,0
        c = p.Circle(b,5)
        c.cache_bb()
        self.assertFalse( c.point_query((0,0)) )
        self.assert_( c.point_query((11,1)) )
        
        info = c.segment_query((0,-50),(0,50))
        self.assertEqual(info, None)
        info = c.segment_query((10,-50),(10,50))
        self.assertEqual(info.get_hit_point().x, 10)
        self.assertEqual(info.get_hit_distance(), 45)
        self.assertAlmostEqual(info.n.y, -1.0)
        
    
####################################################################
if __name__ == "__main__":
    print ("testing pymunk version " + p.version)
    unittest.main()