#!/usr/bin/env python
"""
Library for working with colours.
If run from the command line, provide a number N, and this shall return N
colours (in HEX format) as distant as possible, according to the HSL model.

Usage:-
e.g.
python colours.py 5
"""
# Copyright (c) Alex Leach. 2011
# Contact: Alex Leach (albl500@york.ac.uk)
# University of York, Department of Biology,
# Wentworth Way, York YO10 4DU, United Kingdom
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have receive a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>
#
# Description:
# Library for working with colours.
# If run from the command line, provide a number N, and this shall return N
# colours (in HEX format) as distant as possible, according to the HSL model.
import sys
import math
try:
    import matplotlib.pyplot as plt
except ImportError:
    if __name__ =='__main__':
        sys.stderr.write( "#  matplotlib import error\n" )

class HSLColour():
    def __init__(self,angle,degrees = 360):
        self.hue = angle
#       cos_value = math.cos( angle * math.pi / degrees ) ## cos( angle/2 ) ; so cos_value goes from 1 to -1
        sin_value = math.sin( angle * 2.* math.pi /(3. * degrees) ) ## sin( angle/2 ) ; so cos_value goes from 0 to 0
        self.saturation = 95 + (sin_value * 5)  ## Saturation from 90 --> 100
        self.lightness = 60 + (sin_value * 5)   ## Lightness from 65 --> 55
    def __str__(self):
        ret = (self.hue,self.saturation,self.lightness)
        return repr(ret)

class Heat():

    # define some trig constants. (0 < x < 100 )
    sin60 = 100. * math.sqrt( 3 ) / 2  
    sin45 = 100. * math.sqrt( 2 ) / 2
    sin30 = 50

    # Compartmentalise colours into thirds. 
    # white --> blue,  yellow --> orange,  red --> black.
    # LUMINANCE LIMITS ( 0 < LUM < 100 )
    BLUE_LUM = ( 99 , sin45 )
    YELLOW_LUM = ( sin60 , 100 - sin45 )
    RED_LUM = ( 50 , 10 )

    # HUE LIMITS ( 0 < hue < 360 )
    BLUE_HUE = ( 180 , 240 )
    YELLOW_HUE = ( 80 , 30 )
    RED_HUE = ( 25 , -31 )

    # Last group ( blue --> yellow --> red --> ... )
    LAST_HUE = ( 0 , 360 )
    LAST_LUM = ( 10 , sin60 )

    def __init__( self,N=360 , groups = None ):
        self.colors = [ col for col in make_HSL_heatmap( N , groups ) ]
    def __getitem__( self, i ):
        return self.colors[i]
    def __iter__(self):
        for col in self.colors:
            yield col

    @classmethod
    def last_test( cls , col , colour_number ):
        #colour.hue = yellow_H_scale[0] + ( angle * yellow_H_range )
        group = 3
        while colour_number > cls.portions[group]:
            group += 1
        steps_to_go = len(cls.portions) - group 
        n_last_groups = len( cls.portions) - 3

        group_portion = (group -3. )/ n_last_groups
        ind_portion = float(cls.portions[group] - colour_number ) / \
                            ( cls.portions[group] - cls.portions[group-1] )
        group_angle     = 0.5 * ( 1 + math.tan( (group_portion*2-1)*math.tanh(1)) )
        ind_angle = 0.5 * ( 1 + math.tan( ( ind_portion * 2-1) * math.tanh(1)) )

        col.hue = cls.LAST_HUE[0] + ( group_angle * cls.LAST_H_RANGE )
        col.lightness = cls.LAST_LUM[0] + ( ind_angle * cls.LAST_L_RANGE )
        return col

    @classmethod
    def make_HSL_heatmap( cls, N, groups=None ):
        """Given a number N, will yield that many colours, splitting N into
        3 main colour groups.
        If optional groups is given, this should be a list indicating the 
        number of shades per colour group. 
        If N is not divisible by 3, more shades are put into the latter groups.
        """
        tests = {}
        cls.portions = []
        if groups is not None:
            step_sizes = [ 1. / n_in_group for n_in_group in groups ]
            count = 0
            counts = {}
            for n,group in enumerate(groups):
                count += group
                counts.update( { n: count } )
                fn = (lambda n: lambda x: True if x-1 < counts[n] else False )
                tests.update( { n : fn(n) } )
                cls.portions.append( count )
        else:
            step_sizes = [ 3. / N ] * 3
            third = N/3.
            cls.portions = [ third , 2*third , N ]
            for n, group in enumerate( cls.portions ):
                print 'group',group
                fn = (lambda n: lambda x: True if x-1 < int(cls.portions[n]) else False )
                tests.update( { n : fn(n) } )

        # Length of hue / luminance ranges.
        blue_H_range = cls.BLUE_HUE[1] - cls.BLUE_HUE[0]
        blue_L_range = cls.BLUE_LUM[1] - cls.BLUE_LUM[0]
        yellow_L_range = cls.YELLOW_LUM[1] - cls.YELLOW_LUM[0]
        yellow_H_range = cls.YELLOW_HUE[1] - cls.YELLOW_HUE[0]
        red_L_range = cls.RED_LUM[1] - cls.RED_LUM[0]
        red_H_range = cls.RED_HUE[1] - cls.RED_HUE[0]

        if len( tests ) > 3:
            cls.LAST_H_RANGE = cls.LAST_HUE[1] - cls.LAST_HUE[0]
            cls.LAST_L_RANGE = cls.LAST_LUM[1] - cls.LAST_LUM[0]
        
        for i in xrange(1, N+1 ):
            proportion = float(i) / N
            colour = HSLColour( proportion * 360 ) # Just get a unique saturation.
            # 3 tests for 3 colour groups (blue, yellow, red )
            # Remaining groups dealt with by self.last_test
            if tests[0](i):
                test = 0
                steps_to_go = int( cls.portions[0] )- i 
                portion = ( 1.-( steps_to_go * step_sizes[test] ) )     #      ; 0 --> 1 straight.
                angle = math.sin( 0.5 * math.pi * portion ) # sin(0) --> sin(0.5*pi)  ; 0 --> 1 sinusoidally
                colour.lightness = cls.BLUE_LUM[0] + (angle * blue_L_range) # A value between 50 & sin60
                colour.hue = cls.BLUE_HUE[0] + (angle * blue_H_range )
            elif tests[1](i):
                test = 1
                steps_to_go = int(cls.portions[1] - i )
                portion = 1. - ( steps_to_go * step_sizes[test] )
                #angle     = 0.5 + ( math.tan( (portion*2*math.tanh(1)) - (math.tanh(1) )) / 2 )
                angle     = 0.5 * ( 1 + math.tan( (portion*2-1)*math.tanh(1)) )
                colour.lightness = cls.YELLOW_LUM[0] + ( angle * yellow_L_range )
                colour.hue = cls.YELLOW_HUE[0] + ( angle * yellow_H_range )
            elif tests[2](i):
                test = 2
                steps_to_go = int(cls.portions[2]) - i
                portion = 1. - (steps_to_go * step_sizes[test] )
                angle =  math.cos( 0.5*math.pi* ( portion - 1 )  )   # cos(pi) --> cos(2*pi)
                colour.lightness = cls.RED_LUM[0] + ( angle * red_L_range )
                colour.hue = cls.RED_HUE[0] + ( angle * red_H_range )
            else:
                colour = cls.last_test( colour , i )
            if ( colour.lightness > 100. or colour.lightness < 0 ) :
                print '\ni',i
                print 'hue',colour.hue
                print 'groups ',groups
                print 'test ',test
                print 'tests[test](i) ',tests[test](i)
                print 'third',cls.portions[test]
                print 'thrids',cls.portions
                print 'steps', steps_to_go
                print 'portion',portion
                print 'angle',angle
                print 'lightness', colour.lightness
                raise ValueError # colour.lightness must be between 0 & 100
            yield colour


make_HSL_heatmap = Heat.make_HSL_heatmap

def generate_HSL_colours( N ,shift = 81, degrees = 360.):
    """Given an integer N, return N unique colours as distinct
    as possible according to the HSL model"""
    assert N > 0
    colours = []
    end_val = int( degrees + shift )
    step = round( float(degrees)/ N , 10 )
    #while shift < end_val:
    for i in xrange(N):
        yield HSLColour(shift, degrees=degrees )
        #shift = round( shift+step, 10 )  # To be safe / slow. Binary floats aren't always what they seem. Without this, shift appears < end_val when they should be equal.
        shift += step

def RGB_to_HEX(HSL):
    return '#{0[0]:02X}{0[1]:02X}{0[2]:02X}'.format(HSL)

def HSL_to_HEX( HSL ):
    RGB = HSL_to_RGB( HSL )
    HEX = RGB_to_HEX( RGB )
    return HEX

def HSL_to_RGB( HSL ):
    h,s,l = HSL.hue, HSL.saturation,HSL.lightness
    s /= 100.
    l /= 100.
    if s == 0:
        r = g = b = l * 255.
    else:
        if l <= 0.5:
            m2 = l * ( s+1. )
        else:
            m2 = l + s - l * s
        m1 = l * 2. -m2
        hue = degrees_within_360( h ) / 360.
        r = hue_to_RGB( m1, m2, hue + 1./3. )
        g = hue_to_RGB( m1, m2, hue )
        b = hue_to_RGB( m1, m2, hue - 1./3. )
    return ( int(r),int(g),int(b) )

def degrees_within_360( degrees ):
    hue = degrees / 360.
    n_over = math.floor(hue)
    hue -= n_over  
    return hue * 360.

def hue_to_RGB( m1,m2,hue):
    if hue < 0:
        hue += 1
    elif hue > 1:
        hue -= 1
    if 6*hue < 1:
        v = m1 + (m2-m1) * hue * 6.
    elif 2*hue < 1:
        v = m2
    elif 3*hue < 2:
        v = m1 + (m2-m1) * ((2./3.) - hue) * 6.
    else:
        v = m1
    return 255 * v
        
def generate_HEX_colours( N, shift=81, degrees=360. ):
    for HSL in generate_HSL_colours(N,shift,degrees):
        RGB = HSL_to_RGB( HSL )
        HEX = RGB_to_HEX( RGB )
        yield HEX

def draw_heatmap( N , groups=None ):
    cols = [ col for col in make_HSL_heatmap( N , groups ) ]
    fig = plt.figure(1)
    axis = plt.subplot( 111 )
    axis.set_title( 'Heatmap with {0} colours'.format( N ) )
    plt.axis( [0,N,0,1] )
    xvals = [] ; yvals = []
    lightx = [] ; lighty = []
    axis.yaxis.set_visible(False)
    for i in xrange( N ):
        try:
            axis.bar( i,1,width=1 , color=HSL_to_HEX( cols[i] ) )
        except ValueError:
            print HSL_to_HEX( cols[i] )
            print i, cols[i]
            raise
        xvals.append( i + 0.5 )
        yvals.append( degrees_within_360(cols[i].hue)  )
        lightx.append( i +0.5 ) ; lighty.append( cols[i].lightness )
    ax2 = plt.twinx()
    plt.axis( [0,N,0,360])
    ax2.yaxis.set_ticks_position( 'left' )
    ax2.yaxis.set_label_position( 'left' )
    ax2.xaxis.set_visible(False)
    ax2.set_ylabel('Hue (black line)' )
    plt.plot( xvals , yvals , color='#000000' )
    ax3 = plt.twinx()
    plt.axis( [0,N,0,100])
    ax3.set_ylabel( 'Luminance (white line)' )
    plt.plot( lightx,lighty, color = HSL_to_HEX(cols[0]) )
    plt.draw()
    return

def draw_vert_heatmap( N , groups=None ):
    cols = [ col for col in make_HSL_heatmap( N,groups ) ]
    fig = plt.figure(1)
    axis = plt.subplot( 111 )
    axis.set_title( 'Heatmap with {0} colours'.format( N ) )
    plt.axis( [0,1,0,N] )
    xvals = [] ; yvals = []
    lightx = [] ; lighty = []
    axis.yaxis.set_visible(True)
    axis.xaxis.set_visible(False)
    for i in xrange( N ):
        axis.bar( 0,1,width=1,bottom=i , color=HSL_to_HEX( cols[i] ) )
    plt.draw()
    return

if __name__ == '__main__':
    #draw_vert_heatmap( 66, groups=(15,13,14,24))
    print 'testing colour generator...',
    col = []
    groups = None
    if len( sys.argv ) > 2:
        groups = [ int(arg) for arg in sys.argv[1:] ]
        n_test = sum( groups )
    elif len( sys.argv ) > 1:
        n_test = int(sys.argv[1])
    else:
        n_test = 13

    print 'testing heatmap...',
    try:
        plt.ioff()
        draw_heatmap(n_test,groups=groups)
        draw_vert_heatmap( n_test, groups=groups)
        plt.show()
    except NameError:
        # matplotlib didn't import
        for i in make_HSL_heatmap(n_test,groups=groups):
            col.append(i)
        if len( col ) == n_test:
            print 'okay'
        else:
            print 'not okay. Generated {0} colours instead of {1}'.format( len(col) , n_test )
    except Exception:
        raise
    else:
        print 'okay.'

