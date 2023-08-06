
# Created on 2011.08.09
#
# @author: german

# TODO:	attribute the code sections that were taken from somewhere else
# TODO: create a test for calc_rotation_matrix

"""
Functions to perform operations over vectors and matrices;
deal with homogeneous transforms; convert angles and other structures.
"""

import math
from math import sqrt, pi, cos, sin, acos

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

# axes used to determine constrained joint rotations
rightAxis = (1.0, 0.0, 0.0)
leftAxis = (-1.0, 0.0, 0.0)
upAxis = (0.0, 1.0, 0.0)
downAxis = (0.0, -1.0, 0.0)
bkwdAxis = (0.0, 0.0, 1.0)
fwdAxis = (0.0, 0.0, -1.0)

#===============================================================================
# added to the original refactored code
#===============================================================================

def radians_to_degrees(radians_):
	return math.degrees(radians_)

# TODO: mix with the corresponding scalar-argument function
def vec3_radians_to_degrees(vector_):
	result = []
	for radians_ in vector_:
		result.append(radians_to_degrees(radians_))
	return tuple(result)

def degrees_to_radians(degrees_):
	return math.radians(degrees_)

# TODO: mix with the corresponding scalar-argument function
def vec3_degrees_to_radians(vector_):
	result = []
	for degrees_ in vector_:
		result.append(degrees_to_radians(degrees_))
	return tuple(result)

def rot_matrix_to_hom_transform(rot_matrix):
	"""From transform.r2t in Corke's Robotic Toolbox (python) rot_matrix 3x3
	matrix.	It may be a tuple, tuple of tuples or the result of numpy.mat()"""
	import numpy as np

	if isinstance(rot_matrix, tuple):
		if len(rot_matrix) == 9:
			rot_matrix = (rot_matrix[0:3], rot_matrix[3:6], rot_matrix[6:9])

	return np.concatenate( (np.concatenate((rot_matrix, np.zeros((3,1))),1),
						np.mat([0,0,0,1])) )

def matrix3_multiply(matrix1, matrix2):
	"""returns the matrix multiplication of matrix1 and matrix2"""
	#TODO: check objects are valid, or use exceptions to catch errors raised by numpy

	import numpy as np

	a1 = np.array(matrix1)
	a2 = np.array(matrix2)
	result = np.dot(a1, a2)

	return matrix_as_3x3_tuples(tuple(result.flatten()))

def matrix_as_tuple(matrix_):
	"""matrix_: nested tuples, e.g. ((1,0),(1,1),(2,5))"""
	#TODO: improve a lot
	return gut.nested_iterable_to_tuple(matrix_)

def matrix_as_3x3_tuples(tuple_9):
	#TODO: improve a lot

	matrix = None
	if isinstance(tuple_9, tuple):
		if len(tuple_9) == 9:
			matrix = (tuple_9[0:3], tuple_9[3:6], tuple_9[6:9])
	return matrix

class Transform:
	def __init__(self, position, rot_matrix):
		"""
		position: a 3-tuple
		rot_matrix: a 9-tuple
		"""
		if not rot_matrix:
			rot_matrix = []
			rot_matrix[0:3] = (1,0,0)
			rot_matrix[3:6] = (0,1,0)
			rot_matrix[6:9] = (0,0,1)
			rot_matrix = tuple(rot_matrix)

		row1 = rot_matrix[0:3] + (position[0],)
		row2 = rot_matrix[3:6] + (position[1],)
		row3 = rot_matrix[6:9] + (position[2],)
		row4 = (0,0,0,1)
		self.matrix = (row1,row2,row3,row4)

	def __str__(self):
		return str(self.matrix)

	def get_long_tuple(self):
		return gut.nested_iterable_to_tuple(self.matrix)

	def get_position(self):
		raise NotImplementedError()

	def get_rotation_matrix(self):
		raise NotImplementedError()

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
	#TODO: convert it so it can handle vector of any dimension
	l = length3(vector)
	if l > 0.0:
		return (vector[0] / l, vector[1] / l, vector[2] / l)
	else:
		return (0.0, 0.0, 0.0)

def dot_product3(vector1, vector2):
	"""Returns the dot product of 3-vectors vector1 and vector2"""
	#TODO: convert it so it can handle vector of any dimension
	return vector1[0] * vector2[0] + vector1[1] * vector2[1] + vector1[2] * vector2[2]

def cross_product(vector1, vector2):
	"""Returns the cross_product product of 3-vectors vector1 and vector2"""
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

def calc_rotation_matrix(axis, angle):
	"""
	Returns the row-major 3x3 rotation matrix defining a rotation around axis by
	angle.

	Formula is the same as the one presented here (as of 2011.12.01):
	http://goo.gl/RkW80

	<math>
	R = \begin{bmatrix}
	\cos \theta +u_x^2 \left(1-\cos \theta\right) &
	u_x u_y \left(1-\cos \theta\right) - u_z \sin \theta &
	u_x u_z \left(1-\cos \theta\right) + u_y \sin \theta \\
	u_y u_x \left(1-\cos \theta\right) + u_z \sin \theta &
	\cos \theta + u_y^2\left(1-\cos \theta\right) &
	u_y u_z \left(1-\cos \theta\right) - u_x \sin \theta \\
	u_z u_x \left(1-\cos \theta\right) - u_y \sin \theta &
	u_z u_y \left(1-\cos \theta\right) + u_x \sin \theta &
	\cos \theta + u_z^2\left(1-\cos \theta\right)
	\end{bmatrix}
	</math>
	"""

	cos_theta = cos(angle)
	sin_theta = sin(angle)
	t = 1.0 - cos_theta
	return (
		t * axis[0]**2 + cos_theta,
		t * axis[0] * axis[1] - sin_theta * axis[2],
		t * axis[0] * axis[2] + sin_theta * axis[1],
		t * axis[0] * axis[1] + sin_theta * axis[2],
		t * axis[1]**2 + cos_theta,
		t * axis[1] * axis[2] - sin_theta * axis[0],
		t * axis[0] * axis[2] - sin_theta * axis[1],
		t * axis[1] * axis[2] + sin_theta * axis[0],
		t * axis[2]**2 + cos_theta)

def make_OpenGL_matrix(rotation, position):
	"""Returns an OpenGL compatible (column-major, 4x4 homogeneous)
	transformation matrix from ODE compatible (row-major, 3x3) rotation matrix
	rotation and position vector position"""
	return (
		rotation[0], rotation[3], rotation[6], 0.0,
		rotation[1], rotation[4], rotation[7], 0.0,
		rotation[2], rotation[5], rotation[8], 0.0,
		position[0], position[1], position[2], 1.0)

def get_body_relative_vector(body, vector):
	"""Returns the 3-vector vector transformed into the local coordinate system
	of ODE body 'body'"""
	return rotate3(transpose3(body.get_rotation()), vector)

#===============================================================================
# TESTS
#===============================================================================

def _test_angular_conversions(angle_):
	#x = 2.0/3*math.pi
	y = radians_to_degrees(angle_)
	z = degrees_to_radians(y)
	dif = angle_ - z

	print('radians: %f' % angle_)
	print('degrees: %f' % y)
	print('difference: %f' % dif)

def _test_rot_matrix_to_hom_transform():

	import numpy as np
	rot1 = np.mat([[1,2,3],[4,5,6],[7,8,9]])
	rot2 = ((1,2,3),(4,5,6),(7,8,9))
	rot3 = (1,2,3,4,5,6,7,8,9)
	ht1 = rot_matrix_to_hom_transform(rot1)
	ht2 = rot_matrix_to_hom_transform(rot2)
	ht3 = rot_matrix_to_hom_transform(rot3)

	#print(rot1)
	#print(rot2)
	print(ht1)
	print(ht2)
	print(ht3)

def _test_Transform():

	pos = (10,20,30)
	rot = (0,0,1,1,0,0,0,1,0)
	t = Transform(pos, rot)

	print(pos)
	print(rot)
	print(t)
	print(t.get_long_tuple())

if __name__ == '__main__':

	_test_rot_matrix_to_hom_transform()
	_test_angular_conversions(2.0/3*math.pi)
	_test_angular_conversions(4.68*math.pi)

	radians_ = (2.0/3*math.pi, 2.0*math.pi, 1.0/4*math.pi)
	degrees_ = (120, 360, 45)
	print(vec3_radians_to_degrees(radians_))
	print(vec3_degrees_to_radians(degrees_))
	print(radians_)

	_test_Transform()