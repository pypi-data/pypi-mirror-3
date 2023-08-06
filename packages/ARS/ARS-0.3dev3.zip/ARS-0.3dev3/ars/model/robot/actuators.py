
# Created on 2011.10.31
#
# @author: german

from abc import ABCMeta, abstractmethod

class Actuator:
	__metaclass__ = ABCMeta

class Servo(Actuator):
	pass

class Motor(Actuator):
	pass