#
# Project: BOORL: Bond-Orientational Order Recognition Library
# File name: core.py
# Description:  This file contains the core classes of the application 
#   
# @author Nasser Mohieddin Abukhdeir, University of Waterloo
#		  Yasamin Salmasi, University of Waterloo
#		  Ryan W. Young, University of Waterloo
#         http://www.chemeng.uwaterloo.ca/faculty/abukhdeir.html, Copyright (C) 2012.
# @version $Id: 
#   
# @see The GNU Public License (GPL)
#
#
# This program is free software; you can redistribute it and/or modify 
#  it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or 
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License 
# for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program; if not, write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


# Standard library imports
import numpy as np


import matplotlib 
import scipy   

from matplotlib import delaunay as dla
from scipy import ndimage as nd


filename=input('please enter a  data file name(*.npy): ')  # The data file(*.npy) has to be in the same directory as this code.
array = np.load(filename) 
array1 = (array - array.min()) / (array.max() - array.min()) # Normalizes the data into 0-1 range.

 

def iteration(array1, x):
	''' iteration(array1, x)a

	Find the threshold value according to the iteration method.

	Parameters
	----------
	array1 -- array_like
		  Array containing the normalized simulation data.
	x -- float
	     The permissible limit of variation.

	Returns
	-------
	t -- float
	     The desired Threshold value.
	
	Notes
	-----

	See Also
	--------

	Examples
	--------
	 

	'''

	to = 0.0 
	t = np.mean(array1)  # The first threshold value is the mean of the data.
	while abs(t - to) > x:
		indices1 = np.where(array1 > t)  # Finds the loaction of all the entries greater than t.
		indices2 = np.where(array1 < t)
		h = np.mean(array1[indices1])  # Finds the mean of all those entries which are greater than t.
		b = np.mean(array1[indices2])
		to = t  # The old threshold value.
		t = (h + b) / 2  # The new threshold value.			
	return t

#This function computes an array of binary values (zeroes and ones) from the given data; counts and labels the non-zero values as features, finds the center of mass of each feature and finds the nearest neighbours to each feature using deluanay triangulation algorithm.

def dl(array1, thresh):
	''' delaunay(array1, thresh)
	
	Find the nearest neighbors to center of mass of each feature, using deluanay triangulation algorithm.

	Parameters
	----------
	array1 -- array-like
		  Array containing the normalized simulation data
	thresh -- float
		  The desired threshold value in range 0-1 
	
	Returns
	-------
	ed -- array-like
              An array of integers giving the indices of each edge in triangulation.
	coords -- list of tuples 
 		  Coordinates of center of masses.

	Notes
	-----
	
	See Also  
	--------
	matplotpoint.delaunay.delaunay: compute the delaunay triangulation of a cloud of 2-D points. 
	
	Examples
	--------
	

	'''

	
	array2 = np.where(array1>thresh, 1, 0)  # computes a binary image from the imported simulation data.
	(lbls, num) = nd.label(array2)  # counts and labels the non-zero values as features.
	coords = nd.center_of_mass(array2, lbls, range(1, num+1)) # finds the center of mass of each feature.
	coords = np.array(coords)
	(cc, edg, tri_p, tri_n) = dla.delaunay(coords[:,0], coords[:,1]) # computes the delaunay triangulation of a set of center of masses. 
	print('indices of edges:', edg)
	
 	 

	
