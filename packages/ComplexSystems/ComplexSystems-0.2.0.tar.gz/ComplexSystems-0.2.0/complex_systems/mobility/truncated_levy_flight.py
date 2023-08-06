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

__all__ = ['truncated_levy_flight',
           'main']


def truncated_levy_flight(alpha, beta, size_max, s_min, s_max, duration=90000, b_c=1):
    '''
    This code is based on the following paper. Injong Rhee, Minsu Shin, Seongik
    Hong, Kyunghan Lee and Song Chong, On the Levy-walk Nature of Human
    Mobility, INFOCOM, Arizona, USA, 2008
    
    [X,Y,T] = truncated_levy_flight(alpha,beta,size_max,s_min,s_max,duration,b_c)
    
    Example :
         (X,Y,T) = truncated_levy_flight(1, 1, 1500, 30, 60*60, 3*60, 1)
    
    INPUT:
        alpha : float 
            Levy exponent for flight length distribution, 0 < alpha <= 2
        
        beta  : float 
            Levy exponent for pause time distribution, 0 < beta <= 2
        
        size_max : int 
            size of simulation area
        
        s_min : int 
            min pause time (second)
        
        s_max : int  
            max pause time (second)
        
        duration : int 
            total simulation (minutes)
        
        b_c : int 
            boundary condition: 
                wrap-around if b_c=1
                reflection boundary if b_c=2
    OUTPUT:
        X : int 
            X location
        
        Y : int 
            Y location
        
        T : float 
            time in seconds
    '''
    
    import stabrnd as R
    import numpy as N
    
    # Pause Time scale parameter
    pt_scale = 1.0
    # Flight Length scale parameter
    fl_scale = 10.0
    
    delta = 0.0
    m = 100
    n = 1
    
    # Sampling period (second)
    time_size = 60

    # Simulation time
    # Example 90000 sec = 25 hours
    end_time = duration * time_size
    
    # Constant speed
    mu = 0.0
    
    # Bounds of the simulation area
    max_x = size_max
    max_y = size_max
    # f_min/f_max : min/max flight length
    f_min = 5
    f_max = size_max
    
    num_step = 50000

    A = []
    B = []
    x = [0] * num_step
    y = [0] * num_step
    t = [0] * num_step
    x_mobile = [0] * num_step
    y_mobile = [0] * num_step
    t_mobile = [0] * num_step
    dist = [0] * num_step
    
    if alpha < .1 or alpha > 2 :
        raise ValueError('Alpha must be in [.1,2] for function stabrnd.')

    if beta < .1 or beta > 2 :
        raise ValueError('Beta must be in [.1,2] for function stabrnd.')

    # Generate flight length
    while len(A) < num_step:
        A_temp = N.abs(R.stabrnd(alpha, 0, fl_scale, delta, num_step, n))
        A_temp = A_temp[A_temp > f_min]
        A_temp = A_temp[A_temp < f_max]
        A = N.append(A, A_temp)
        
    A = N.round(A[0:num_step])
    
    # Generate pause time
    while len(B) < num_step:
        B_temp = N.abs(R.stabrnd(beta, 0, pt_scale, 0, num_step, 1))
        B_temp = B_temp[B_temp > s_min]
        B_temp = B_temp[B_temp < s_max]
        B = N.append(B, B_temp)
    
    B = N.round(B[0:num_step])
    
    # Initial Step
    x[1] = max_x * N.random.rand()
    y[1] = max_y * N.random.rand()
    t[1] = 0
    
    j = 1
    
    for i in N.arange(2, num_step, 2):
        theta = 2 * N.pi * N.random.rand()
        next_x = N.round(x[i - 1] + A[i / 2] * N.cos(theta))
        next_y = N.round(y[i - 1] + A[i / 2] * N.sin(theta))
        # Boundary of the simulation Area
        # Wrap around
        if b_c == 1:
            if next_x < 0:
                x[i] = max_x + next_x
            elif next_x > max_x:
                x[i] = next_x - max_x
            else:
                x[i] = next_x
    
            if next_y < 0:
                y[i] = max_y + next_y
            elif next_y > max_y:
                y[i] = next_y - max_y
            else:
                y[i] = next_y
        # Boundary of the simulation Area
        # Reflection
        elif b_c == 2:
            if next_x < 0:
                x[i] = -next_x
            elif next_x > max_x:
                x[i] = max_x - (next_x - max_x)
            else:
                x[i] = next_x
    
            if next_y < 0:
                y[i] = -next_y
            elif next_y > max_y:
                y[i] = max_y - (next_y - max_y)
            else:
                y[i] = next_y
        # end of boundary
    
        dist[i] = N.sqrt(float((next_x - x[i - 1]) ** 2 + (next_y - y[i - 1]) ** 2))
        t[i] = t[i - 1] + N.power(dist[i], 1 - mu)
        t[i + 1] = t[i] + N.abs(B[i / 2])
        x[i + 1] = x[i]
        y[i + 1] = y[i]
        
        while j * time_size < t[i + 1]:
            if j * time_size < t[i]:
                p_ratio = float((j * time_size - t[i - 1]) / (t[i] - t[i - 1]))
                x_temp = next_x * p_ratio + x[i - 1] * (1 - p_ratio)
                y_temp = next_y * p_ratio + y[i - 1] * (1 - p_ratio)
                
                # Boundary of the simulation Area
                # wrap around
                if b_c == 1:
                    if x_temp < 0:
                        x_temp = max_x + x_temp
                    elif x_temp > max_x:
                        x_temp = x_temp - max_x
                
                    if y_temp < 0:
                        y_temp = max_y + y_temp
                    elif y_temp > max_y:
                        y_temp = y_temp - max_y
                # reflection
                elif b_c == 2 :
                    if x_temp < 0:
                        x_temp = -x_temp
                    elif x_temp > max_x:
                        x_temp = max_x - (x_temp - max_x)
                    
                    if y_temp < 0:
                        y_temp = -next_y
                    elif next_y > max_y:
                        y_temp = max_y - (next_y - max_y)
                # end of reflection            
                x_mobile[j] = x_temp
                y_mobile[j] = y_temp
                t_mobile[j] = j * time_size
            else:
                x_mobile[j] = x[i]
                y_mobile[j] = y[i]
                t_mobile[j] = j * time_size
            j = j + 1
        
        if t[i + 1] > end_time: 
            break
        
    if t[i] < end_time:
        raise ImportWarning("Not enought simulation step generated, reduce the duration or increase s_max")
       
    X = N.round(x_mobile[1:duration])
    Y = N.round(y_mobile[1:duration])
    T = t_mobile[1:duration]
    return X, Y, T
    
def distance(X,Y):
    '''
    Calculate the Euclidian distance between vector distance (Xi,Yi)(t) and (Xi,Yi)(t+1) for all t,i
    '''
    import numpy as N
    dist = [N.sqrt(float((X[t+1] - X[t]) ** 2 + (Y[t+1] - Y[t]) ** 2)) for t in range(len(X)-1)]
    return dist

if __name__ == '__main__':
    import numpy as N
    import pylab as plt
    from scikits.statsmodels.tools.tools import ECDF
    
    (X, Y, T) = truncated_levy_flight(alpha=1.5, beta=1.4, size_max=10000, s_min=0, s_max=100, duration=5, b_c=2)
    #print X, Y, T
        
    plt.figure()
    plt.plot(X, Y, 'o-')
    A = distance(X,Y)  
    ecdf = ECDF(A)
    x = N.linspace(min(A), max(A))
    y = 1 - ecdf(x)
    plt.figure()
    plt.loglog(x, y, 'r', linewidth=2.0)
    plt.xlim(min(A), max(A))
    plt.ylim(min(y), max(y))
    plt.grid(True, which="both")
    plt.xlabel('Distance [m]')
    plt.ylabel('CCDF P(X > x)')
    plt.show()
