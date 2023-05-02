# Description: This file is used to test the stewart platform
import pybullet as p
import time
import pybullet_data
import os 
from inv_kinematics import inv_kinematics as ik
import numpy as np

class StewartPlatform:
    def __init__(self, path, joint_indices, actuator_indices, design_variable) -> None:
        self.path = path
        self.joint_indices = joint_indices
        self.actuator_indices = actuator_indices
        self.design_variable = design_variable
        self.prev_target = np.zeros(len(actuator_indices))

    def cls(self):
        os.system('cls')
    def set_env(self):
        physicsClient = p.connect(p.GUI)#or p.DIRECT for non-graphical version
        # physicsClient = p.connect(p.DIRECT)#or p.DIRECT for non-graphical version
        p.setAdditionalSearchPath(pybullet_data.getDataPath()) #optionally
        p.setGravity(0,0,-9.81)
        planeId = p.loadURDF("plane.urdf")
        cubeStartPos = [0,0,0]
        cubeStartOrientation = p.getQuaternionFromEuler([0,0,0])
        # Load the Stewart Platform
        self.robotId = p.loadURDF(self.path,cubeStartPos, cubeStartOrientation, 
                        flags=p.URDF_USE_MATERIAL_COLORS_FROM_MTL,useFixedBase = 1)
                        
        # Set the camera position and orientation
        camera_target_position = [0, 0, 0]
        camera_distance = 1.5
        camera_yaw = 50
        camera_pitch = -35
        camera_roll = 0
        p.resetDebugVisualizerCamera(cameraDistance = camera_distance, cameraYaw = camera_yaw,
                                    cameraPitch = camera_pitch,
                                    cameraTargetPosition = camera_target_position, 
                                    physicsClientId = physicsClient)
        self.n = p.getNumJoints(self.robotId)  # Get the number of joints in the robot
        self.Ind = {}                            # Create a dictionary to store the joint indices
        for i in range(self.n):
            joint_info = p.getJointInfo(self.robotId, i)
            self.Ind[joint_info[0]]=joint_info[1]
        
    def set_constraints(self):
        # Create a fixed constraint for each pair of linked joints
        for parent_joint, child_joint in self.joint_indices:
            # Create the constraint
            constraint_id = p.createConstraint(self.robotId, parent_joint, self.robotId, child_joint, p.JOINT_FIXED, [0,0,0.1], [0,0,0], [0,0,0])
            # If you need to store the constraint ID for later use, you can add it to a list or dictionary here
            p.changeConstraint(constraint_id, maxForce=1e20)

        # Disable the motors for all joints
        for i in range(self.n):
            maxForce = 0
            mode = p.VELOCITY_CONTROL
            p.setJointMotorControl2(self.robotId, i,
                                    controlMode=mode, force=maxForce)
        
    def init_stewart(self,flag):
        # Design variables
        r_P,r_B, gama_P,gama_B = self.design_variable
        self.clf = ik(r_P,r_B,gama_P,gama_B)
        # compute the leg length for the initial position
        translation = np.array([0, 0, 0])       # translation in meters
        rotation = np.array([0, 0, 0])         # rotation in degrees
        self.l  = self.clf.solve(translation, rotation)
        if flag:
            translation = np.array([0, 0, 0.1])
            leg_1  = self.clf.solve(translation, rotation)
            self.linear_actuator(leg_1-self.l, 1)
            time.sleep(1.)
        # print("leg length",self.l,leg_l0)
        return 
    
    # Motor driver function
    def linear_actuator(self, linear_distance, actuation_duration):
        # Calculate the step size and the PWM parameters
        frequency = 50                                   # 50 Hz
        max_force = 1000                                 # 100 N.M
        steps = int(actuation_duration * frequency)  # pwm steps
        pwm_period = 1.0 / frequency                  # pwm period
        duty_cycle = 0.5                            # 50% duty cycle
        pwm_high_time = pwm_period * duty_cycle 
        actuation_step = [l / steps for l in linear_distance]
        # Actuate the linear actuators
        for i in range(steps):
            # Read the pwm signal
            pwm_signal = i * pwm_period % pwm_period < pwm_high_time
            # pwm signal is high then actuate the linear actuator
            if pwm_signal:
                # print("PWM signal is high")
                for j in range(len(self.actuator_indices)):
                    target_position = actuation_step[j] * i + self.prev_target[j]
                    # print(target_position)
                    p.setJointMotorControl2(self.robotId, self.actuator_indices[j], p.POSITION_CONTROL,
                                            targetPosition=target_position, force=max_force)
            # pwm signal is low then stop the linear actuator
            else:
                # print("PWM signal is low")
                for j in range(len(self.actuator_indices)):
                    p.setJointMotorControl2(self.robotId, self.actuator_indices[j], p.POSITION_CONTROL,
                                        targetPosition=p.getJointState(self.robotId, self.actuator_indices[j])[0],
                                        force=max_force)
            time.sleep(1./(5*frequency))
            p.stepSimulation()
            
        self.prev_target = np.array(actuation_step) * i+ self.prev_target
        print("actuation step",self.prev_target)
        return 
        
    def start_simmulation(self, data, flag = True):
        
        self.set_env()         # set the environment
        self.set_constraints()  # set the constraints
        logging_id = p.startStateLogging(p.STATE_LOGGING_VIDEO_MP4, "simulation.mp4")
        self.init_stewart(flag)  # initialize the stewart platform
        for i in data:
            trans,rot,t = i
            l = self.clf.solve(trans, rot) # compute the leg length
            dl = l-self.l                    # compute the leg actuation distance
            self.linear_actuator(dl, t)         # actuate the linear actuator
            # time.sleep(1)
        cubePos, cubeOrn = p.getBasePositionAndOrientation(self.robotId)
        for i in range (50):
            p.stepSimulation()
            time.sleep(1./240.)
            cubePos, cubeOrn = p.getBasePositionAndOrientation(self.robotId)
        # print(cubePos,cubeOrn)
        # Stop recording the simulation
        p.stopStateLogging(logging_id)
        p.disconnect()
        return