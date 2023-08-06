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

__all__ = ['levy_flight', 'distance']


def levy_flight(alpha, beta, sample_length, size_max, velocity, f_min, f_max, s_min, s_max, duration=90000, b_c=1):
    '''
    This code is based on the following paper:
    
    .. [Rhee08] Injong Rhee, Minsu Shin, Seongik Hong, Kyunghan Lee and Song Chong, "On the Levy-walk Nature of Human Mobility", INFOCOM, Arizona, USA, 2008
    
    :Example:
    >>> from complex_systems.mobility.levy_flight import *
    >>> levy_flight(alpha=0.66, beta=0.99, sample_length=1, size_max=83000, velocity=1.0, f_min=8, f_max=83000, s_min=0.8, s_max=430, duration=500, b_c=2)
    
    :Parameters:
    - `alpha` : float 
        Levy exponent for flight length distribution, 0 < alpha <= 2
    - `beta`  : float 
        Levy exponent for pause time distribution, 0 < beta <= 2
    - `sample_length` : int
        Sample time in mins
    - `size_max` : int 
        size of simulation area
    - `velocity` : float
        speed in m/s
    - `f_min` : int
        min flight length
    - `f_max` : int
        max flight length
    - `s_min` : int 
        min pause time (second)
    - `s_max` : int  
        max pause time (second)
    - `duration` : int 
        simulation duration (minutes)
    - `b_c` : int 
        boundary condition: 
            - wrap-around if b_c=1
            - reflection boundary if b_c=2
    
    :Returns: 
    - `X` : list(int) 
        X location
    - `Y` : list(int) 
        Y location
    - `T` : list(float) 
        time in seconds
    '''
    
    import stabrnd as R
    import numpy as N
    
    # Pause Time scale parameter
    pt_scale = 1.0
    # Flight Length scale parameter
    fl_scale = 10.0
    
    # DEBUG
    DEBUG = False
    
    delta = 0.0

    
    # Velocity in meter per mins
    velocity = velocity * 60.0
    if DEBUG: print 'velocity (m/mins): ', velocity 

    num_step = int(N.ceil(float(duration)/sample_length))
    num_step_gen = 4 * num_step
    
    if DEBUG: print 'num steps: ', num_step 
    
    # Constant speed
    mu = 0.0
    
    # Bounds of the simulation area
    max_x = size_max
    max_y = size_max 

    A = []
    B = []
    x = [0] * (num_step_gen + 1)
    y = [0] * (num_step_gen + 1)
    t = [0] * (num_step_gen + 1)
    x_sampled = [0] * (num_step + 1)
    y_sampled = [0] * (num_step + 1)
    t_sampled = [0] * (num_step + 1)
    dist = [0] * num_step_gen
    
    if alpha < .1 or alpha > 2 :
        raise ValueError('Alpha must be in [.1,2] for function stabrnd.')

    if beta < .1 or beta > 2 :
        raise ValueError('Beta must be in [.1,2] for function stabrnd.')

    # Generate flight length
    while len(A) < num_step_gen:
        A_temp = N.abs(R.stabrnd(alpha, 0, fl_scale, delta, num_step, 1))
        A_temp = A_temp[A_temp > f_min]
        A_temp = A_temp[A_temp < f_max]
        A = N.append(A, A_temp)
        
    A = N.round(A[0:num_step_gen])
    
    # Generate pause time
    while len(B) < num_step_gen:
        B_temp = N.abs(R.stabrnd(beta, 0, pt_scale, 0, num_step, 1))
        B_temp = B_temp[B_temp > s_min]
        B_temp = B_temp[B_temp < s_max]
        B = N.append(B, B_temp)
    
    B = N.round(B[0:num_step_gen])
    
    # Initial Step
    x[0] = max_x * N.random.rand()
    y[0] = max_y * N.random.rand()
    t[0] = 0
    
    
    j = 1
    
    for i in N.arange(1, num_step_gen, 2):
        theta = 2 * N.pi * N.random.rand()
        next_x = N.round(x[i - 1] + A[i] * N.cos(theta))
        next_y = N.round(y[i - 1] + A[i] * N.sin(theta))
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
        t[i] = t[i - 1] + N.power(float(dist[i])/velocity, 1 - mu)
        t[i + 1] = t[i] + N.abs(B[i])
        x[i + 1] = x[i]
        y[i + 1] = y[i]
        
        if t[i + 1] > duration: 
            break
    k = 1
    t_sampled[0] = 0.0
    x_sampled[0] = x[0]
    y_sampled[0] = y[0]
    for j in range(1,num_step):
        while not (j * sample_length) < t[k]:
            k += 1
        
        if t[k] > duration:
            break
        
        p_ratio =  (t[k] - (j*sample_length)) / (t[k] - ((j-1) * sample_length))
        x_sampled[j] = x[k] * p_ratio + x_sampled[j - 1] * (1 - p_ratio)
        y_sampled[j] = y[k] * p_ratio + y_sampled[j - 1] * (1 - p_ratio)
        t_sampled[j] = (j*sample_length)
            
    if DEBUG: print 'Simulation length : ', len(x)
    
    X = N.round(x[0:i])
    Y = N.round(y[0:i])
    T = t[0:i]
    X_sampled = N.round(x_sampled[0:j])
    Y_sampled = N.round(y_sampled[0:j])
    T_sampled = t_sampled[0:j]
    return X, Y, T, A, B, X_sampled, Y_sampled, T_sampled
    
def distance(X,Y):
    '''
    Calculate the Euclidian distance between two vectors
    
    .. math::
        distance( (x_t,y_t), (x_{t+1},y_{t+1}) ) \\ \\forall t
        
    :Example:
    >>> from complex_systems.mobility.levy_flight import *
    >>> X = [0,0,0]
    >>> Y = [1,2,3]
    >>> distance(X,Y)
    [1.0,1.0]

    :Parameters:
    - `X`: list(float)
        X coordinates     
    - `Y`: list(float)
        Y coordinates
    
    :Returns:
    - `dist` : list
            Euclidian distance
    '''
    import numpy as N
    dist = [N.sqrt(float((X[t+1] - X[t]) ** 2 + (Y[t+1] - Y[t]) ** 2)) for t in range(len(X)-1)]
    return dist