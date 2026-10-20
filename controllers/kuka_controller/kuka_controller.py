#!/usr/bin/env python3

from controller import Robot, Motor
import math
import time
import sys
import os

# Add libraries path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../libraries'))

class KukaPickPlaceController:
    def __init__(self):
        # Initialize robot
        self.robot = Robot()
        self.timestep = int(self.robot.getBasicTimeStep())
        
        print("Kuka Controller Started")
        
        # Get arm motors (Kuka YouBot has 5 arm joints)
        self.arm_motors = []
        arm_motor_names = ['arm_1', 'arm_2', 'arm_3', 'arm_4', 'arm_5']
        
        for name in arm_motor_names:
            motor = self.robot.getDevice(name)
            if motor:
                self.arm_motors.append(motor)
                print(f"Found motor: {name}")
            else:
                print(f"Warning: Motor {name} not found")
        
        # Get gripper motors
        self.gripper_motors = []
        gripper_names = ['finger::left', 'finger::right']
        
        for name in gripper_names:
            motor = self.robot.getDevice(name)
            if motor:
                self.gripper_motors.append(motor)
                print(f"Found gripper motor: {name}")
            else:
                print(f"Warning: Gripper motor {name} not found")
        
        # Define positions
        self.home_position = [0.0, 0.2, -0.1, 0.0, 0.0]
        self.pick_position = [0.5, 0.8, -0.6, 0.5, 0.0]
        self.place_position = [-0.5, 0.8, -0.6, 0.5, 0.0]
        
        self.current_step = 0
        print("Controller initialization completed")
        
    def move_arm_to_position(self, target_position, steps=100):
        """Smoothly move arm to target position"""
        print(f"Moving arm to position: {target_position}")
        
        current_positions = [motor.getTargetPosition() for motor in self.arm_motors]
        
        for step in range(steps):
            # Calculate intermediate position
            progress = step / steps
            for i, motor in enumerate(self.arm_motors):
                intermediate_pos = current_positions[i] + (target_position[i] - current_positions[i]) * progress
                motor.setPosition(intermediate_pos)
            
            self.robot.step(self.timestep)
        
        # Set final position
        for i, motor in enumerate(self.arm_motors):
            motor.setPosition(target_position[i])
        
        # Wait for movement to complete
        for _ in range(50):
            self.robot.step(self.timestep)
            
        return True
    
    def open_gripper(self):
        """Open the gripper"""
        print("Opening gripper")
        for motor in self.gripper_motors:
            motor.setPosition(0.03)  # Open position
        
        # Wait for gripper to open
        for _ in range(50):
            self.robot.step(self.timestep)
    
    def close_gripper(self):
        """Close the gripper"""
        print("Closing gripper")
        for motor in self.gripper_motors:
            motor.setPosition(0.0)  # Closed position
        
        # Wait for gripper to close
        for _ in range(50):
            self.robot.step(self.timestep)
    
    def pick_sequence(self):
        """Execute pick sequence"""
        print("=== STARTING PICK SEQUENCE ===")
        
        # Move to pre-pick position
        pre_pick = [0.3, 0.6, -0.4, 0.3, 0.0]
        if not self.move_arm_to_position(pre_pick):
            return False
        
        # Move to pick position
        if not self.move_arm_to_position(self.pick_position):
            return False
        
        # Close gripper
        self.close_gripper()
        
        # Lift object
        lift_position = [0.3, 0.6, -0.3, 0.3, 0.0]
        if not self.move_arm_to_position(lift_position):
            return False
        
        print("Pick sequence completed successfully")
        return True
    
    def place_sequence(self):
        """Execute place sequence"""
        print("=== STARTING PLACE SEQUENCE ===")
        
        # Move to pre-place position
        pre_place = [-0.3, 0.6, -0.4, 0.3, 0.0]
        if not self.move_arm_to_position(pre_place):
            return False
        
        # Move to place position
        if not self.move_arm_to_position(self.place_position):
            return False
        
        # Open gripper
        self.open_gripper()
        
        # Move away
        if not self.move_arm_to_position(pre_place):
            return False
        
        print("Place sequence completed successfully")
        return True
    
    def run(self):
        """Main control loop"""
        print("Kuka Pick and Place Controller Running")
        
        # Initial setup
        self.open_gripper()
        self.move_arm_to_position(self.home_position)
        
        sequence_state = "pick"
        attempt_count = 0
        
        while self.robot.step(self.timestep) != -1:
            self.current_step += 1
            
            if sequence_state == "pick":
                if self.pick_sequence():
                    sequence_state = "place"
                    attempt_count = 0
                else:
                    attempt_count += 1
                    if attempt_count > 3:
                        print("Too many failed attempts, returning home")
                        self.move_arm_to_position(self.home_position)
                        sequence_state = "pick"
                        attempt_count = 0
            
            elif sequence_state == "place":
                if self.place_sequence():
                    sequence_state = "completed"
                else:
                    attempt_count += 1
                    if attempt_count > 3:
                        print("Too many failed attempts, returning home")
                        self.move_arm_to_position(self.home_position)
                        sequence_state = "pick"
                        attempt_count = 0
            
            elif sequence_state == "completed":
                print("=== MISSION COMPLETED ===")
                self.move_arm_to_position(self.home_position)
                break
            
            # Safety: don't run forever
            if self.current_step > 10000:
                print("Safety timeout reached")
                break

# Create and run controller
if __name__ == "__main__":
    controller = KukaPickPlaceController()
    controller.run()
