import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
from utils import rendering_sections
import unittest

class TestRenderingSections(unittest.TestCase):
    def test_render_section(self):
        self.assertEqual(
            rendering_sections(0, 481, 4),
            [(0, 120), (121, 241), (242, 362), (363, 480)]
        )

if __name__ == '__main__':
    unittest.main()
