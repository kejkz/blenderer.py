import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
from utils import rendering_sections
import unittest

class TestRenderingSections(unittest.TestCase):
    def test_render_section(self):
        self.assertEqual(
            rendering_sections(1, 481, 4),
            [(1, 121), (122, 242), (243, 363), (364, 481)]
        )

if __name__ == '__main__':
    unittest.main()
