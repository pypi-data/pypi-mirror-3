import pymunk as p
from pymunk.vec2d import Vec2d
import unittest

####################################################################
        
class UnitTestBody(unittest.TestCase):
    def setUp(self):
        p.reset_shapeid_counter()
        
    def test(self):
        b = p.Body(10,100)
        self.assertEqual(b.mass, 10)
        self.assertEqual(b.moment, 100)
        b.reset_forces()
        b.apply_force((10,10))
        
    def testSleep(self):
        b = p.Body(1,1)
        s = p.Space()
        s.add(b)
        
        self.assertFalse(b.is_sleeping)
        
        b.sleep()
        self.assert_(b.is_sleeping)
        
        b.activate()
        self.assertFalse(b.is_sleeping)
        
    def testSleepWithGroup(self):
        b1 = p.Body(1,1)
        b2 = p.Body(2,2)
        s = p.Space()
        s.add(b1,b2)
        b2.sleep()
        b1.sleep_with_group(b2)
        self.assert_(b1.is_sleeping)
        b2.activate()
        self.assertFalse(b1.is_sleeping)
        
        
    def testKineticEnergy(self):
        b = p.Body(1,10)
        self.assertEqual(b.kinetic_energy, 0)
        b.apply_impulse((10,0))
        self.assertEqual(b.kinetic_energy, 100)
        
    def testIsRogue(self):
        b = p.Body(1,1)
        self.assert_(b.is_rogue)
        s = p.Space()
        s.add(b)
        self.assertFalse(b.is_rogue)
        
    def testStatic(self):
        bd = p.Body(1,1)
        bs = p.Body()
        self.assertFalse(bd.is_static)
        self.assert_(bs.is_static)
        
    def testConversion(self):
        b = p.Body(1,1)
        b.position = 10,20
        self.assertEqual(b.local_to_world((1,1)), Vec2d(11,21))
        self.assertEqual(b.world_to_local((1,1)), Vec2d(-9,-19))
        
    def testPositonFunction(self):
        s = p.Space()
        b = p.Body(1,1)
        def f(body, dt):
            body.position += 0,dt
        
        b.position_func=f
        s.add(b)
        s.step(10)
        self.assertEqual(b.position.y, 10)
        s.step(1)
        s.step(1)
        self.assertEqual(b.position.y, 12)
        
        b.position_func = p.Body.update_position
        s.step(1)
        self.assertEqual(b.position.y, 12)
        
    def testVelocityFunction(self):
        s = p.Space()
        b = p.Body(1,1)
        def f(body, gravity, damping, dt):
            body.velocity += 5*gravity
        
        b.velocity_func=f
        s.gravity = 1,0
        s.add(b)
        s.step(10)
        return
        self.assertEqual(b.velocity.x, 5)
        s.step(0.1)
        s.step(0.1)
        self.assertEqual(b.velocity.x, 15)
        
        b.velocity_func = b.update_velocity
        s.step(1)
        self.assertEqual(b.velocity.x, 16)
        
    def testVelocityLimit(self):
        s = p.Space()
        s.gravity = 1000,0
        b = p.Body(1,1)
        b.velocity_limit = 1
        s.add(b)
        s.step(1)
        self.assertEqual(b.velocity_limit, 1)
        self.assertEqual(b.velocity.x, 1)
        
    def testAngularVelocityLimit(self):
        s = p.Space()
        b = p.Body(1,1)
        b.angular_velocity_limit = 1
        s.add(b)
        b.apply_force((1000,0), (0,10))
        b.apply_force((-1000,0), (0,-10))
        s.step(1)
        self.assertEqual(b.angular_velocity_limit, 1)
        self.assertEqual(abs(b.angular_velocity), 1)
####################################################################
if __name__ == "__main__":
    print ("testing pymunk version " + p.version)
    unittest.main()