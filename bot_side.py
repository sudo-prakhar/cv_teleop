'''
@ Author: Prakhar Pradeep
@ Email: ppradee2@andrew.cmu.edu
@ Project: Touri
'''

import stretch_body.robot
from stretch_body.hello_utils import ThreadServiceExit
import firebase_admin
from firebase_admin import credentials, db

################################# Bot init ######################################################

# Using LLPy to actuate the robot
robot = stretch_body.robot.Robot()
# Init robot
robot.startup()

################################# Normalize values ######################################################

def normailize_wrist(value, upper_bound, lower_bound):
    '''
    Translates raw values recieved from user side to bot's joint angles (Gripper)
    IN: Value, Upper bound (human pose), Lower bound (human pose)
    OUT: Robot's joint angle (Gripper)
    '''
    value = -value if value < 0 else value
    value = lower_bound if value < lower_bound else value
    value = upper_bound if value > upper_bound else value

    diff = upper_bound - lower_bound
    base = lower_bound

    value = 65 * (value - base)/diff 
    return value - 25

def normailize_wrist_yaw(value, upper_bound, lower_bound):
    '''
    Translates raw values recieved from user side to bot's joint angles (Wrist)
    IN: Value, Upper bound (human pose), Lower bound (human pose)
    OUT: Robot's joint angle (Wrist)
    '''
    value = -value if value < 0 else value
    value = lower_bound if value < lower_bound else value
    value = upper_bound if value > upper_bound else value

    diff = upper_bound - lower_bound
    base = lower_bound

    value = 1.57 * (value - base)/diff 
    return value


################################# Actuation functions ######################################################
# NOTE: The functions below can be merged into one. Separated for scalability reasons.
############################################################################################################

def change_gripper_yaw(position_value):
    '''
    Moves the end-effector to a particular angle
    IN: Desired angle for end-effector's yaw
    '''
    try:
        #Queue new targets to devices
        # Range 0 to 1.57
        robot.end_of_arm.move_to('wrist_yaw', position_value)
        #Synchronized send of new position targets 
        robot.push_command()
    except (KeyboardInterrupt, SystemExit, ThreadServiceExit):
        pass


def change_gripper_pos(position_value):
    '''
    Moves the gripper to a particular angle
    IN: Desired angle for end-effector's yaw
    '''
    try:
        #Queue new targets to devices
        # Range 0 to 45
        robot.end_of_arm.move_to('stretch_gripper', position_value)
        #Synchronized send of new position targets 
        robot.push_command()
        
    
    except (KeyboardInterrupt, SystemExit, ThreadServiceExit):
        pass

################################# Callbacks functions ######################################################

def listener_angle(event):
    '''
    Callback function that reacts in real-time to data change on the cloud database
    IN: Event - object type defined in Firebase's library
    '''
    raw_wrist_angle = event.data
    norm_angle = normailize_wrist(raw_wrist_angle, 170, 20)
    print("\n####################################################")
    print("WRIST ANGLE: {}".format(raw_wrist_angle))
    print("####################################################\n")
    change_gripper_pos(norm_angle)
    
def listener_yaw(event):
    '''
    Callback function that reacts in real-time to data change on the cloud database
    IN: Event - object type defined in Firebase's library
    '''
    raw_wrist_yaw = event.data
    norm_yaw = normailize_wrist_yaw(raw_wrist_yaw, 120, 70)

    print("\n####################################################")
    print("WRIST YAW: {}".format(raw_wrist_yaw))
    print("####################################################\n")

    change_gripper_yaw(norm_yaw)
    
    

if __name__ == "__main__":

    # Path to database key
    cred = credentials.Certificate("/home/hello-robot/Desktop/bot_side_server/keys/touri-65f07-firebase-adminsdk-wuv71-3751c21aa8.json")
    
    # Init database
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://touri-65f07-default-rtdb.firebaseio.com/'})

    #Add listeners to particular nodes
    db.reference("/hand/wrist_angle").listen(listener_angle)
    db.reference("/hand/wrist_yaw").listen(listener_yaw)
