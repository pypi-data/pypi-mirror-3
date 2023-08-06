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

__all__ = ['test_levy_flight_w_plots']

from complex_systems.mobility.levy_flight import * 

def test_levy_flight_w_plots():
    import numpy as N
    import pylab as plt
    from scikits.statsmodels.tools.tools import ECDF
    
    (X, Y, T, A, B, X_sampled, Y_sampled, T_sampled) = levy_flight(alpha=0.66, 
                                                                   beta=0.99,
                                                                   sample_length = 1, 
                                                                   size_max=83000,
                                                                   velocity=1.0, 
                                                                   f_min=8, 
                                                                   f_max=83000, 
                                                                   s_min=0.8, 
                                                                   s_max=430, 
                                                                   duration=500, 
                                                                   b_c=2)
    print X_sampled
        
    plt.figure()
    plt.plot(X_sampled, Y_sampled, 'ro-')
    plt.plot(X, Y, 'o-')
      
    ecdf = ECDF(A)
    x = N.linspace(min(A), max(A))
    y = 1 - ecdf(x)
    
    plt.figure()
    plt.loglog(x, y, 'r', linewidth=2.0)
    plt.xlim(1, max(A))
    plt.ylim(min(y), max(y))
    plt.grid(True, which="both")
    plt.xlabel('Distance [m]')
    plt.ylabel('CCDF P(X > x)')
    
    ecdf = ECDF(B)
    x = N.linspace(min(B), max(B))
    y = 1 - ecdf(x)
    plt.figure()
    plt.loglog(x, y, 'r', linewidth=2.0)
    plt.xlim(0.1, max(B))
    plt.ylim(min(y), max(y))
    plt.grid(True, which="both")
    plt.xlabel('Pause Time [mins]')
    plt.ylabel('CCDF P(X > x)')

    plt.show()


if __name__ == '__main__':
    test_levy_flight_w_plots()