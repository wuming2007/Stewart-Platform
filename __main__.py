from StewartPlatform import StewartPlatform as sp
import numpy as np
from draw_3d_spiral import draw_3d_spiral

"""
3DOF Stewart Platform RPR configuration analysis:
    - We take 6Dof Stewart Platform as a reference.
    - We fix the platform in the home position.
    - The platfrom can only rotate in the x,y,z axis roll, pitch yaw.
"""
# define the path of urdf file path
path = "Stewart/Stewart.urdf"

# Define the joint indices for each pair of linked joints
joint_indices = [(6, 16), (35, 17), (49, 18), (42, 19), (28, 20)]

# Define the actuators for each pair of linked joints
actuator_indices = [9, 2, 31, 45, 38, 24]

# Define the stewart platform design variables
radious_platform, radious_base = 0.2, 0.2         # meters
half_angle_platform, half_angle_base = 24/2, 24/2 # degrees
design_variables = [radious_platform, radious_base, half_angle_platform, half_angle_base]

"""
Test 1 : 3DOF Stewart Platform RPR configuration:
        - For RPR configuration set flag True.
        - 30 degrees yaw within 4 seconds.
        - 20 degrees pitch within 3 seconds.
        - 15 degrees roll within 2 seconds.
        - Return back to home position within 1 seconds.
"""
trans = np.array([0, 0, 0]) # 9 cm in z axis
# Roll, pitch and yaw angles of the platform
rot1 = np.array([0, 0, 30]) # 30 degrees yaw
rot3 = np.array([0, 20, 0]) # 20 degrees pitch
rot2 = np.array([15, 0, 0]) # 15 degrees roll

# Time to reach the desired position
time1,time2,time3 = 4,3,2 # seconds
# Define the desired end effector position
data1 = [[trans, rot1,time1], [trans, rot2,time2], [trans, rot3, time3]]

"""
Test 2 : 3DOF Stewart Platform RPR configuration:
        - 30 degrees yaw and return back to pltform position within 4 seconds
        - 20 degrees pitch return back to pltform position within 3 seconds
        - 15 degrees roll return back to pltform position within 2 seconds
        - Return back to home position within 1 seconds.
"""
# Translation of the platform

data2 = [[trans, rot1, time1], [trans, -rot1, time1], 
         [trans, rot2,time2], [trans, -rot2,time2],
         [trans, rot3, time3],[trans, -rot3, time3]]

"""
Test 3 : 6DOF Stewart Platform:
        - Tracing a 3D spiral path
        - For 6DOF Stewart Platform set flag False.
"""
data5 = [[np.array([0,0.09,0]), np.array([0,0,0]), 2], 
         [np.array([0.09,0,0]), np.array([0,0,0]), 2]]
x,y,z = draw_3d_spiral()
data3 = [[np.array([x[i], y[i], z[i]]), np.array([0, 0, 0]), 0.2] for i in range(len(x))]
data3.insert(0,[np.array([0,0,0.025]), np.array([0,0,0]), 1])
data4 = [data5, data1, data2, data3]
# Create the stewart platform object
clf1 = sp(path, joint_indices, actuator_indices, design_variables)
clf2 = sp(path, joint_indices, actuator_indices, design_variables)
clf3 = sp(path, joint_indices, actuator_indices, design_variables)
clf4 = sp(path, joint_indices, actuator_indices, design_variables)
if __name__ == '__main__':
#     clf1.start_simmulation(data1)
#     clf2.start_simmulation(data2, simulation=True)
#     clf3.start_simmulation(data3,simulation=True,flag=False)
    clf4.fit(data4, flag=[True, True,True, False], simulation=True)
