
# Created on 2011.08.09
#
# @author: german

# TODO:	attribute the code sections that were taken from somewhere else

"""
Functions to perform operations over vectors and matrices;
deal with homogeneous transforms; convert angles and other structures.
"""

import itertools
from math import sqrt, pi, cos, sin, acos, atan, atan2, degrees, radians
import operator

import numpy as np

import generic as gut

#===============================================================================
# rotation directions are named by the third (z-axis) row of the 3x3 matrix, because ODE capsules
# are oriented along the Z-axis
#===============================================================================

rightRot = (0.0, 0.0, -1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0)
leftRot = (0.0, 0.0, 1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 0.0)
upRot = (1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0)
downRot = (1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0)
bkwdRot = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)

X_AXIS = (1.0, 0.0, 0.0)
X_AXIS_NEG = (-1.0, 0.0, 0.0)
Y_AXIS = (0.0, 1.0, 0.0)
Y_AXIS_NEG = (0.0, -1.0, 0.0)
Z_AXIS = (0.0, 0.0, 1.0)
Z_AXIS_NEG = (0.0, 0.0, -1.0)

# axes used to determine constrained joint rotations
rightAxis = X_AXIS
leftAxis = X_AXIS_NEG
upAxis = Y_AXIS
downAxis = Y_AXIS_NEG
bkwdAxis = Z_AXIS  # direction: out of the screen
fwdAxis = Z_AXIS_NEG  # direction: into the screen

#===============================================================================
# added to the original refactored code
#===============================================================================

def radians_to_degrees(radians_):
	return degrees(radians_)

# TODO: combine with the corresponding scalar-argument function
def vec3_radians_to_degrees(vector_):
	result = []
	for radians_ in vector_:
		result.append(radians_to_degrees(radians_))
	return tuple(result)

def degrees_to_radians(degrees_):
	return radians(degrees_)

# TODO: combine with the corresponding scalar-argument function
def vec3_degrees_to_radians(vector_):
	result = []
	for degrees_ in vector_:
		result.append(degrees_to_radians(degrees_))
	return tuple(result)

def matrix3_multiply(matrix1, matrix2):
	"""returns the matrix multiplication of matrix1 and matrix2"""
	#TODO: check objects are valid, or use exceptions to catch errors raised by numpy

	a1 = np.array(matrix1)
	a2 = np.array(matrix2)
	result = np.dot(a1, a2)

	return matrix_as_3x3_tuples(tuple(result.flatten()))

def matrix_as_tuple(matrix_):
	"""\matrix_: nested tuples, e.g. ((1,0),(1,1),(2,5))"""
	#TODO: improve a lot
	return gut.nested_iterable_to_tuple(matrix_)

def matrix_as_3x3_tuples(tuple_9):
	#TODO: improve a lot

	matrix = None
	if isinstance(tuple_9, tuple):
		if len(tuple_9) == 9:
			matrix = (tuple_9[0:3], tuple_9[3:6], tuple_9[6:9])
	return matrix

#===============================================================================
# Original code but formatted and some refactor
#===============================================================================

def sign(x):
	"""Returns 1.0 if x is positive, -1.0 if x is negative or zero"""
	if x > 0.0: return 1.0
	else: return -1.0

def length2(vector):
	"""Returns the length of a 2-dimensions vector"""
	return sqrt(vector[0]**2 + vector[1]**2)

def length3(vector):
	"""Returns the length of a 3-dimensions vector"""
	#TODO: convert it so it can handle vector of any dimension
	return sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)

def neg3(vector):
	"""Returns the negation of 3-vector vector"""
	#TODO: convert it so it can handle vector of any dimension
	return (-vector[0], -vector[1], -vector[2])

def add3(vector1, vector2):
	"""Returns the sum of 3-vectors vector1 and vector2"""
	#TODO: convert it so it can handle vector of any dimension
	return (vector1[0] + vector2[0], vector1[1] + vector2[1], vector1[2] + vector2[2])

def sub3(vector1, vector2):
	"""Returns the difference between 3-vectors vector1 and vector2"""
	#TODO: convert it so it can handle vector of any dimension
	return (vector1[0] - vector2[0], vector1[1] - vector2[1], vector1[2] - vector2[2])

def mult_by_scalar3(vector, scalar):
	"""Returns 3-vector vector multiplied by scalar scalar"""
	#TODO: convert it so it can handle vector of any dimension
	return (vector[0] * scalar, vector[1] * scalar, vector[2] * scalar)

def div_by_scalar3(vector, scalar):
	"""Returns 3-vector vector divided by scalar scalar"""
	#TODO: convert it so it can handle vector of any dimension
	return (vector[0] / scalar, vector[1] / scalar, vector[2] / scalar)

def dist3(vector1, vector2):
	"""Returns the distance between point 3-vectors vector1 and vector2"""
	#TODO: convert it so it can handle vector of any dimension
	return length3(sub3(vector1, vector2))

def norm3(vector):
	"""Returns the unit length 3-vector parallel to 3-vector vector"""
	#l = length3(vector)
	#if l > 0.0:
	#	return (vector[0] / l, vector[1] / l, vector[2] / l)
	#else:
	#	return (0.0, 0.0, 0.0)
	return unitize(vector)

def unitize(vector_):
	"""Unitize a vector, i.e. return a unit-length vector parallel to `vector`

	"""
	len_ = sqrt(sum(itertools.imap(operator.mul, vector_, vector_)))
	size_ = len(vector_)

	if len_ > 0.0:
		div_vector = (len_,) * size_  # (len_, len_, len_, ...)
		return tuple(itertools.imap(operator.div, vector_, div_vector))
	else:
		return (0.0, 0.0, 0.0)

def dot_product3(vector1, vector2):
	"""Returns the dot product of 3-vectors vector1 and vector2"""
	return dot_product(vector1, vector2)

def dot_product(vec1, vec2):
	"""Efficient dot-product operation between two vectors of the same size.
	source: http://docs.python.org/library/itertools.html

	"""
	return sum(itertools.imap(operator.mul, vec1, vec2))

def cross_product(vector1, vector2):
	"""Returns the cross_product product of length-3 vectors `vector1` and
	`vector2`

	"""
	return (vector1[1] * vector2[2] - vector1[2] * vector2[1],
		vector1[2] * vector2[0] - vector1[0] * vector2[2],
		vector1[0] * vector2[1] - vector1[1] * vector2[0])

def project3(vector, unit_vector):
	"""Returns projection of 3-vector vector onto unit 3-vector unit_vector"""
	#TODO: convert it so it can handle vector of any dimension
	return mult_by_scalar3(vector, dot_product3(norm3(vector), unit_vector))

def acos_dot3(vector1, vector2):
	"""Returns the angle between unit 3-vectors vector1 and vector2"""
	x = dot_product3(vector1, vector2)
	if x < -1.0: return pi
	elif x > 1.0: return 0.0
	else: return acos(x)

def rotate3(rot_matrix, vector):
	"""Returns the rotation of 3-vector vector by 3x3 (row major) matrix rot_matrix"""
	return (vector[0] * rot_matrix[0] + vector[1] * rot_matrix[1] + vector[2] * rot_matrix[2],
		vector[0] * rot_matrix[3] + vector[1] * rot_matrix[4] + vector[2] * rot_matrix[5],
		vector[0] * rot_matrix[6] + vector[1] * rot_matrix[7] + vector[2] * rot_matrix[8])

def transpose3(matrix):
	"""Returns the inversion (transpose) of 3x3 rotation matrix matrix"""
	#TODO: convert it so it can handle vector of any dimension
	return (matrix[0], matrix[3], matrix[6],
		matrix[1], matrix[4], matrix[7],
		matrix[2], matrix[5], matrix[8])

def z_axis(rot_matrix):
	"""Returns the z-axis vector from 3x3 (row major) rotation matrix rot_matrix"""
	#TODO: convert it so it can handle vector of any dimension, and any column
	return (rot_matrix[2], rot_matrix[5], rot_matrix[8])

#===============================================================================
# TESTS
#===============================================================================

def _test_angular_conversions(angle_):
	#x = 2.0/3*pi
	y = radians_to_degrees(angle_)
	z = degrees_to_radians(y)
	dif = angle_ - z

	print('radians: %f' % angle_)
	print('degrees: %f' % y)
	print('difference: %f' % dif)

if __name__ == '__main__':

	_test_angular_conversions(2.0 / 3 * pi)
	_test_angular_conversions(4.68 * pi)

	radians_ = (2.0 / 3 * pi, 2.0 * pi, 1.0 / 4 * pi)
	degrees_ = (120, 360, 45)
	print(vec3_radians_to_degrees(radians_))
	print(vec3_degrees_to_radians(degrees_))
	print(radians_)
