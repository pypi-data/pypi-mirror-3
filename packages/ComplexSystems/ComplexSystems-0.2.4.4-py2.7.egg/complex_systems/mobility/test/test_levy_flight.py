#-------------------------------------------------------------------------------
# Copyright (c) 2012 Vincent Gauthier.
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#-------------------------------------------------------------------------------

__author__ = """\n""".join(['Vincent Gauthier <vgauthier@luxbulb.org>'])

__all__ = ['test_levy_flight']


from complex_systems.mobility.levy_flight import * 
import unittest

class test_levy_flight(unittest.TestCase):
     
    def test_levy_flight(self):
        (X, Y, T) = levy_flight(alpha=1.5, beta=1.4, size_max=10000, s_min=0, s_max=100, duration=1000, b_c=2)
        
    def test_levy_flight_bad_parameter_alpha(self):
        self.assertRaises(ValueError, levy_flight, alpha=0.0, beta=1.4, size_max=10000, s_min=0, s_max=100, duration=1000, b_c=2)   
        
    def test_levy_flight_bad_parameter_beta(self):
        self.assertRaises(ValueError, levy_flight, alpha=0.5, beta=0.0, size_max=10000, s_min=0, s_max=100, duration=1000, b_c=2) 
    
if __name__ == '__main__':
    unittest.main()
