
# Created on 2011.10.31
#
# @author: german

# TODO:	attribute the code sections that were taken from somewhere else

import ode

import ars.model.physics.adapters as phs
import ars.utils.geometry as gemut
import ars.utils.mathematical as mut

class RagDoll:

	#===========================================================================
	# RAGDOLL BODY DIMENSIONS
	#===========================================================================
	UPPER_ARM_LEN = 0.30
	FORE_ARM_LEN = 0.25
	HAND_LEN = 0.13 # wrist to mid-fingers only
	FOOT_LEN = 0.18 # ankles to base of ball of foot only
	HEEL_LEN = 0.05

	BROW_H = 1.68
	MOUTH_H = 1.53
	NECK_H = 1.50
	SHOULDER_H = 1.37
	CHEST_H = 1.35
	HIP_H = 0.86
	KNEE_H = 0.48
	ANKLE_H = 0.08

	SHOULDER_W = 0.41
	CHEST_W = 0.36 # actually wider, but we want narrower than shoulders (esp. with large radius)
	LEG_W = 0.28 # between middles of upper legs
	PELVIS_W = 0.25 # actually wider, but we want smaller than hip width

	R_SHOULDER_POS = (-SHOULDER_W * 0.5, SHOULDER_H, 0.0)
	L_SHOULDER_POS = (SHOULDER_W * 0.5, SHOULDER_H, 0.0)
	R_ELBOW_POS = mut.sub3(R_SHOULDER_POS, (UPPER_ARM_LEN, 0.0, 0.0))
	L_ELBOW_POS = mut.add3(L_SHOULDER_POS, (UPPER_ARM_LEN, 0.0, 0.0))
	R_WRIST_POS = mut.sub3(R_ELBOW_POS, (FORE_ARM_LEN, 0.0, 0.0))
	L_WRIST_POS = mut.add3(L_ELBOW_POS, (FORE_ARM_LEN, 0.0, 0.0))
	R_FINGERS_POS = mut.sub3(R_WRIST_POS, (HAND_LEN, 0.0, 0.0))
	L_FINGERS_POS = mut.add3(L_WRIST_POS, (HAND_LEN, 0.0, 0.0))

	R_HIP_POS = (-LEG_W * 0.5, HIP_H, 0.0)
	L_HIP_POS = (LEG_W * 0.5, HIP_H, 0.0)
	R_KNEE_POS = (-LEG_W * 0.5, KNEE_H, 0.0)
	L_KNEE_POS = (LEG_W * 0.5, KNEE_H, 0.0)
	R_ANKLE_POS = (-LEG_W * 0.5, ANKLE_H, 0.0)
	L_ANKLE_POS = (LEG_W * 0.5, ANKLE_H, 0.0)
	R_HEEL_POS = mut.sub3(R_ANKLE_POS, (0.0, 0.0, HEEL_LEN))
	L_HEEL_POS = mut.sub3(L_ANKLE_POS, (0.0, 0.0, HEEL_LEN))
	R_TOES_POS = mut.add3(R_ANKLE_POS, (0.0, 0.0, FOOT_LEN))
	L_TOES_POS = mut.add3(L_ANKLE_POS, (0.0, 0.0, FOOT_LEN))

	def __init__(self, world, space, offset=(0.0, 0.0, 0.0), density=1.0):
		"""Creates a ragdoll of standard size at the given offset"""

		self.world = world
		self.space = space
		self.density = density
		self.bodies = []
		self.geoms = []
		self.joints = []
		self.totalMass = 0.0

		self.offset = offset

		self.chest = self.addBody((-RagDoll.CHEST_W * 0.5, RagDoll.CHEST_H, 0.0),
			(RagDoll.CHEST_W * 0.5, RagDoll.CHEST_H, 0.0), 0.13)
		self.belly = self.addBody((0.0, RagDoll.CHEST_H - 0.1, 0.0),
			(0.0, RagDoll.HIP_H + 0.1, 0.0), 0.125)
		self.midSpine = self.add_fixed_joint(self.chest, self.belly)
		self.pelvis = self.addBody((-RagDoll.PELVIS_W * 0.5, RagDoll.HIP_H, 0.0),
			(RagDoll.PELVIS_W * 0.5, RagDoll.HIP_H, 0.0), 0.125)
		self.lowSpine = self.add_fixed_joint(self.belly, self.pelvis)

		self.head = self.addBody((0.0, RagDoll.BROW_H, 0.0), (0.0, RagDoll.MOUTH_H, 0.0), 0.11)
		self.neck = self.addBallJoint(self.chest, self.head,
			(0.0, RagDoll.NECK_H, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0), mut.pi * 0.25,
			mut.pi * 0.25, 80.0, 40.0)

		self.rightUpperLeg = self.addBody(RagDoll.R_HIP_POS, RagDoll.R_KNEE_POS, 0.11)
		self.rightHip = self.add_universal_joint(self.pelvis, self.rightUpperLeg,
			RagDoll.R_HIP_POS, mut.bkwdAxis, mut.rightAxis, -0.1 * mut.pi, 0.3 * mut.pi, -0.15 * mut.pi,
			0.75 * mut.pi)
		self.leftUpperLeg = self.addBody(RagDoll.L_HIP_POS, RagDoll.L_KNEE_POS, 0.11)
		self.leftHip = self.add_universal_joint(self.pelvis, self.leftUpperLeg,
			RagDoll.L_HIP_POS, mut.fwdAxis, mut.rightAxis, -0.1 * mut.pi, 0.3 * mut.pi, -0.15 * mut.pi,
			0.75 * mut.pi)

		self.rightLowerLeg = self.addBody(RagDoll.R_KNEE_POS, RagDoll.R_ANKLE_POS, 0.09)
		self.rightKnee = self.addHingeJoint(self.rightUpperLeg,
			self.rightLowerLeg, RagDoll.R_KNEE_POS, mut.leftAxis, 0.0, mut.pi * 0.75)
		self.leftLowerLeg = self.addBody(RagDoll.L_KNEE_POS, RagDoll.L_ANKLE_POS, 0.09)
		self.leftKnee = self.addHingeJoint(self.leftUpperLeg,
			self.leftLowerLeg, RagDoll.L_KNEE_POS, mut.leftAxis, 0.0, mut.pi * 0.75)

		self.rightFoot = self.addBody(RagDoll.R_HEEL_POS, RagDoll.R_TOES_POS, 0.09)
		self.rightAnkle = self.addHingeJoint(self.rightLowerLeg,
			self.rightFoot, RagDoll.R_ANKLE_POS, mut.rightAxis, -0.1 * mut.pi, 0.05 * mut.pi)
		self.leftFoot = self.addBody(RagDoll.L_HEEL_POS, RagDoll.L_TOES_POS, 0.09)
		self.leftAnkle = self.addHingeJoint(self.leftLowerLeg,
			self.leftFoot, RagDoll.L_ANKLE_POS, mut.rightAxis, -0.1 * mut.pi, 0.05 * mut.pi)

		self.rightUpperArm = self.addBody(RagDoll.R_SHOULDER_POS, RagDoll.R_ELBOW_POS, 0.08)
		self.rightShoulder = self.addBallJoint(self.chest, self.rightUpperArm,
			RagDoll.R_SHOULDER_POS, mut.norm3((-1.0, -1.0, 4.0)), (0.0, 0.0, 1.0), mut.pi * 0.5,
			mut.pi * 0.25, 150.0, 100.0)
		self.leftUpperArm = self.addBody(RagDoll.L_SHOULDER_POS, RagDoll.L_ELBOW_POS, 0.08)
		self.leftShoulder = self.addBallJoint(self.chest, self.leftUpperArm,
			RagDoll.L_SHOULDER_POS, mut.norm3((1.0, -1.0, 4.0)), (0.0, 0.0, 1.0), mut.pi * 0.5,
			mut.pi * 0.25, 150.0, 100.0)

		self.rightForeArm = self.addBody(RagDoll.R_ELBOW_POS, RagDoll.R_WRIST_POS, 0.075)
		self.rightElbow = self.addHingeJoint(self.rightUpperArm,
			self.rightForeArm, RagDoll.R_ELBOW_POS, mut.downAxis, 0.0, 0.6 * mut.pi)
		self.leftForeArm = self.addBody(RagDoll.L_ELBOW_POS, RagDoll.L_WRIST_POS, 0.075)
		self.leftElbow = self.addHingeJoint(self.leftUpperArm,
			self.leftForeArm, RagDoll.L_ELBOW_POS, mut.upAxis, 0.0, 0.6 * mut.pi)

		self.rightHand = self.addBody(RagDoll.R_WRIST_POS, RagDoll.R_FINGERS_POS, 0.075)
		self.rightWrist = self.addHingeJoint(self.rightForeArm,
			self.rightHand, RagDoll.R_WRIST_POS, mut.fwdAxis, -0.1 * mut.pi, 0.2 * mut.pi)
		self.leftHand = self.addBody(RagDoll.L_WRIST_POS, RagDoll.L_FINGERS_POS, 0.075)
		self.leftWrist = self.addHingeJoint(self.leftForeArm,
			self.leftHand, RagDoll.L_WRIST_POS, mut.bkwdAxis, -0.1 * mut.pi, 0.2 * mut.pi)

	def addBody(self, p1, p2, radius):
		"""
		Adds a capsule body between joint positions p1 and p2 and with given
		radius to the ragdoll.
		"""

		p1 = mut.add3(p1, self.offset)
		p2 = mut.add3(p2, self.offset)

		# cylinder length not including endcaps, make capsules overlap by half radius at joints
		cyllen = mut.dist3(p1, p2) - radius

		body = phs.Capsule(self.world, self.space, cyllen, radius, density=self.density)

		# define body rotation automatically from body axis
		za = mut.norm3(mut.sub3(p2, p1))
		if abs(mut.dot_product3(za, (1.0, 0.0, 0.0))) < 0.7:
			xa = (1.0, 0.0, 0.0)
		else:
			xa = (0.0, 1.0, 0.0)
		ya = mut.cross_product(za, xa)
		xa = mut.norm3(mut.cross_product(ya, za))
		ya = mut.cross_product(za, xa)
		rot = (xa[0], ya[0], za[0], xa[1], ya[1], za[1], xa[2], ya[2], za[2])

		body.set_position(mut.mult_by_scalar3(mut.add3(p1, p2), 0.5)) # equivalent to the midpoint
		body.set_rotation(rot)

		self.bodies.append(body)
		self.totalMass += body.get_mass()

		return body

	def add_fixed_joint(self, body1, body2):
		joint = ode.FixedJoint(self.world)
		joint.attach(body1.inner_object, body2.inner_object)
		joint.setFixed()

		joint.style = "fixed"
		self.joints.append(joint)

		return joint

	def addHingeJoint(self, body1, body2, anchor, axis, loStop = -ode.Infinity,
		hiStop = ode.Infinity):

		anchor = mut.add3(anchor, self.offset)

		joint = ode.HingeJoint(self.world)
		joint.attach(body1.inner_object, body2.inner_object)
		joint.setAnchor(anchor)
		joint.setAxis(axis)
		joint.setParam(ode.ParamLoStop, loStop)
		joint.setParam(ode.ParamHiStop, hiStop)

		joint.style = "hinge"
		self.joints.append(joint)

		return joint

	def add_universal_joint(self, body1, body2, anchor, axis1, axis2,
		loStop1 = -ode.Infinity, hiStop1 = ode.Infinity,
		loStop2 = -ode.Infinity, hiStop2 = ode.Infinity):

		anchor = mut.add3(anchor, self.offset)

		joint = ode.UniversalJoint(self.world)
		joint.attach(body1.inner_object, body2.inner_object)
		joint.setAnchor(anchor)
		joint.setAxis1(axis1)
		joint.setAxis2(axis2)
		joint.setParam(ode.ParamLoStop, loStop1)
		joint.setParam(ode.ParamHiStop, hiStop1)
		joint.setParam(ode.ParamLoStop2, loStop2)
		joint.setParam(ode.ParamHiStop2, hiStop2)

		joint.style = "univ"
		self.joints.append(joint)

		return joint

	def addBallJoint(self, body1, body2, anchor, baseAxis, baseTwistUp,
		flexLimit = mut.pi, twistLimit = mut.pi, flexForce = 0.0, twistForce = 0.0):

		anchor = mut.add3(anchor, self.offset)

		# create the joint
		joint = ode.BallJoint(self.world)
		joint.attach(body1.inner_object, body2.inner_object)
		joint.setAnchor(anchor)

		#=======================================================================
		# store the base orientation of the joint in the local coordinate system of the primary body
		# (because baseAxis and baseTwistUp may not be orthogonal, the nearest vector to baseTwistUp
		# but orthogonal to baseAxis is calculated and stored with the joint)
		#=======================================================================
		joint.baseAxis = mut.get_body_relative_vector(body1, baseAxis)
		tempTwistUp = mut.get_body_relative_vector(body1, baseTwistUp)
		baseSide = mut.norm3(mut.cross_product(tempTwistUp, joint.baseAxis))
		joint.baseTwistUp = mut.norm3(mut.cross_product(joint.baseAxis, baseSide))

		#=======================================================================
		# store the base twist up vector (original version) in the
		# local coordinate system of the secondary body
		#=======================================================================
		joint.baseTwistUp2 = mut.get_body_relative_vector(body2, baseTwistUp)

		# store joint rotation limits and resistive force factors
		joint.flexLimit = flexLimit
		joint.twistLimit = twistLimit
		joint.flexForce = flexForce
		joint.twistForce = twistForce

		joint.style = "ball"
		self.joints.append(joint)

		return joint

	def update_internal_forces(self):
		for j in self.joints:
			if j.style == "ball":
				# determine base and current attached body axes
				baseAxis = mut.rotate3(j.getBody(0).getRotation(), j.baseAxis)
				currAxis = mut.z_axis(j.getBody(1).getRotation())

				# get angular velocity of attached body relative to fixed body
				relAngVel = mut.sub3(j.getBody(1).getAngularVel(),
					j.getBody(0).getAngularVel())
				twistAngVel = mut.project3(relAngVel, currAxis)
				flexAngVel = mut.sub3(relAngVel, twistAngVel)

				# restrict limbs rotating too far from base axis
				angle = mut.acos_dot3(currAxis, baseAxis)
				if angle > j.flexLimit:
					# add torque to push body back towards base axis
					j.getBody(1).addTorque(mut.mult_by_scalar3(
						mut.norm3(mut.cross_product(currAxis, baseAxis)),
						(angle - j.flexLimit) * j.flexForce))

					# dampen flex to prevent bounceback
					j.getBody(1).addTorque(mut.mult_by_scalar3(flexAngVel,
						-0.01 * j.flexForce))

				#===============================================================
				# determine the base twist up vector for the current attached body by applying the
				# current joint flex to the fixed body's base twist up vector
				#===============================================================
				baseTwistUp = mut.rotate3(j.getBody(0).getRotation(), j.baseTwistUp)
				base2current = gemut.calc_rotation_matrix(mut.norm3(mut.cross_product(baseAxis, currAxis)),
					mut.acos_dot3(baseAxis, currAxis))
				projBaseTwistUp = mut.rotate3(base2current, baseTwistUp)

				# determine the current twist up vector from the attached body
				actualTwistUp = mut.rotate3(j.getBody(1).getRotation(),
					j.baseTwistUp2)

				# restrict limbs twisting
				angle = mut.acos_dot3(actualTwistUp, projBaseTwistUp)
				if angle > j.twistLimit:
					# add torque to rotate body back towards base angle
					j.getBody(1).addTorque(mut.mult_by_scalar3(
						mut.norm3(mut.cross_product(actualTwistUp, projBaseTwistUp)),
						(angle - j.twistLimit) * j.twistForce))

					# dampen twisting
					j.getBody(1).addTorque(mut.mult_by_scalar3(twistAngVel,
						-0.01 * j.twistForce))

	def printMass(self):
		print "total mass is %.1f kg (%.1f lbs)" % (self.totalMass,
			self.totalMass * 2.2)
