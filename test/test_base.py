import numpy as np

import carna
import testsuite


class Node(testsuite.CarnaTestCase):

    def test__attach_child(self):
        node1 = carna.base.Node()
        self.assertEqual(node1.children(), 0)
        node2 = carna.base.Node()
        node1.attach_child(node2)
        self.assertEqual(node1.children(), 1)

    def test__attach_child__circular(self):
        node1 = carna.base.Node()
        node2 = carna.base.Node()
        node1.attach_child(node2)
        with self.assertRaises(RuntimeError):
            node2.attach_child(node1)

    def test__attach_child__nonfree(self):
        node1 = carna.base.Node()
        node2 = carna.base.Node()
        node3 = carna.base.Node()
        node1.attach_child(node2)
        with self.assertRaises(RuntimeError):
            node3.attach_child(node2)

    def test__detach_from_parent(self):
        node1 = carna.base.Node()
        node2 = carna.base.Node()
        self.assertFalse(node2.has_parent)
        node1.attach_child(node2)
        self.assertTrue(node2.has_parent)
        node2.detach_from_parent()
        self.assertFalse(node2.has_parent)

    def test__movable(self):
        node1 = carna.base.Node()
        self.assertTrue(node1.is_movable)
        node1.is_movable = False
        self.assertFalse(node1.is_movable)

    def test__tag(self):
        node1 = carna.base.Node()
        self.assertEqual(node1.tag, '')
        node1.tag = 'Test'
        self.assertEqual(node1.tag, 'Test')

    def test__localTransform(self):
        node1 = carna.base.Node()
        np.testing.assert_array_equal(node1.local_transform, np.eye(4))
        node1.local_transform = np.arange(16).reshape(4, 4)
        np.testing.assert_array_equal(node1.local_transform, np.arange(16).reshape(4, 4))


# # ==========================
# # Scene Graph Manipulation 1
# # ==========================

# node1 = base.Node.create()
# assert node1.children() == 0
# node2 = base.Node.create()
# node1.attach_child(node2)
# assert node1.children() == 1
# node1.free()

# # ==========================
# # Scene Graph Manipulation 2
# # ==========================

# node1 = base.Node.create("root")
# assert node1.tag == "root"
# node2 = base.Node.create()
# assert not node2.has_parent
# node1.attach_child(node2)
# assert node2.has_parent
# assert node2.parent is node1
# node2 = node2.detach_from_parent()
# assert np.allclose(node2.local_transform, np.eye(4))
# node1.free()
# node2.free()

# # ==========================
# # Math
# # ==========================

# assert np.allclose(base.math.scaling4f(1, 1, 1), np.eye(4))
# assert np.allclose(base.math.translation4f(0, 0, 0), np.eye(4))
# assert np.allclose(base.math.rotation4f([0, 1, 0], 0), np.eye(4))
