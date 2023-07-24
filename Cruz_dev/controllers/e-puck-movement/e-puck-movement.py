import math, random
from controller import Robot, Motor, Supervisor, DistanceSensor

# Create the Robot instance.
robot = Robot()

# Get the time step.
time_step = int(robot.getBasicTimeStep())

# Get the Supervisor instance
supervisor = Supervisor()

# Variables for following the wall
following_wall = False
distance = float('inf')

# Create Motor devices.
left_motor = None
right_motor = None

# Global position.
position_x = 0.0
position_z = 0.0

# Set E-puck angular speed in rad/s.
MAX_SPEED = 6.28
WALL = False

# Set target position.
target_x = 0.8#round(random.uniform(-0.4, 0.4),2)
target_z = 0.5#round(random.uniform(-0.4, 0.4),2)
print("Target Position: ({}, {})".format(target_x, target_z))

# Genable proximity sensors.
ps = []
for ind in range(8):
    sensor_name = 'ps' + str(ind)
    ps.append(robot.getDevice(sensor_name))
    ps[ind].enable(time_step)

# Function to set motor velocity to move forward.
def move_forward():
    left_motor.setVelocity(MAX_SPEED)
    right_motor.setVelocity(MAX_SPEED)
    
# Function to stop the robot from moving.
def motor_stop():
    left_motor.setVelocity(0)
    right_motor.setVelocity(0)
    
# Function to rotate the robot to the left.
def rotate_left():
    left_motor.setVelocity(-MAX_SPEED/2)
    right_motor.setVelocity(MAX_SPEED/2)
    
# Function to rotate the robot to the right.
def rotate_right():
    left_motor.setVelocity(MAX_SPEED/2)
    right_motor.setVelocity(-MAX_SPEED/2)
    
#Determine if the robot has hit an obstacle
def hit_obstacle():
    for sensor in ps:
        if sensor.getValue() > 80.5:
            print("WALL")
            return True
    return False
    
    
def position_difference(current_x, current_z):
    # Calculate the difference between the current position and the target position
    diff_x = target_x - current_x
    diff_z = target_z - current_z

    # Calculate the distance to the target position
    distance = ((diff_x **2) +  (diff_z **2)) **0.5
    return distance, diff_x, diff_z
    
# Function to move towards goal and adjust rotation
def face_towards_goal(diff_x, diff_z):
    print("rotating to goal...")
    motor_stop()
    # Calculate the desired direction towards the target position
    desired_direction = math.atan2(diff_z, diff_x)
    
    # calculate the difference between the desired and the current direction of the e-puck
    diff_direction = desired_direction - supervisor.getFromDef("epuck").getOrientation()[3]
    
    # Adjust the difference to the range (-pi, pi)
    if diff_direction > math.pi:
        diff_direction -= 2 * math.pi
    elif diff_direction < -math.pi:
        diff_direction += 2 * math.pi
    # Set the motor velocitied to rotate the e-puck towards the desired direction
    if round(diff_direction, 2) > 0:
        print("rotating left", diff_direction)
        rotate_left()
    elif round(abs(diff_direction),2 ) < 0.001 or round(abs(diff_direction),1) == 3.1:
        print("Moving forward")
        move_forward()
    else:
        print("rotating right", diff_direction)
        rotate_right()
    
#Determine how the robot will follow the wall
def follow_wall():
        print("following wall...")
        left_wall = ps[5].getValue() > 80
        left_corner = ps[6].getValue() > 80
        front_wall = ps[7].getValue() > 80
        
        l_speed = MAX_SPEED
        r_speed = MAX_SPEED
        
        if front_wall:
            print("turning right")
            l_speed = MAX_SPEED
            r_speed = -MAX_SPEED
        else:
            if left_wall:
                print("Driving forward")
                l_speed = MAX_SPEED
                r_speed = MAX_SPEED
            
            else:
                # Gets closer to the wall
                print("Turn left")
                l_speed = MAX_SPEED/8
                r_speed = MAX_SPEED
            
            if left_corner:
                print("Came too close, drive right")
                l_speed = MAX_SPEED
                r_speed = MAX_SPEED/8
                
        left_motor.setVelocity(l_speed)
        right_motor.setVelocity(r_speed)

# Get a handler to the motors and set target position to infinity (speed control).
left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

#set the desired tolerance
tolerance = 0.055

# Main loop:
# - Perform simulation steps until Webots is stopping the controller.
while robot.step(time_step) != -1:
    # Print sensor information
    for ind in range(8):
        print("ind: {}, val: {}".format(ind, ps[ind].getValue()))
    
    # Get the current position of the e-puck
    position = supervisor.getFromDef("epuck").getPosition()
    current_x = position[0]
    current_z = position[2]
    
    # Get the distance between the current and target position
    distance, diff_x, diff_z = position_difference(current_x, current_z)
        
    # Check if target is reached
    # Stop the e-puck if it has reached the target position
    if distance <= tolerance:
        motor_stop()
        print("Reached destination")
        print("Destination: ({},{})".format(target_x,target_z))
        print("Current: ({},{})".format(round(current_x, 2),round(current_z, 2)))
        break
    # if has not reached target position
    else:
        # Check if you are near an obstacle
        if hit_obstacle():
            WALL = True
            print(WALL)
        if WALL:
            follow_wall()
        else:
            position_difference(current_x, current_z)
            face_towards_goal(diff_x, diff_z)
            move_forward()

        
    # Set the motor speeds
    # left_motor.setVelocity(left_speed)
    # right_motor.setVelocity(right_speed)


    
# Enter here exit cleanup code.
