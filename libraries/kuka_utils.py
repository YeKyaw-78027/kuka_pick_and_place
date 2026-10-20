#!/usr/bin/env python3

import math
import numpy as np

class KukaKinematics:
    """Simple kinematics utilities for Kuka robot"""
    
    @staticmethod
    def calculate_distance(pos1, pos2):
        """Calculate distance between two 3D points"""
        return math.sqrt(
            (pos1[0]-pos2[0])**2 + 
            (pos1[1]-pos2[1])**2 + 
            (pos1[2]-pos2[2])**2
        )
    
    @staticmethod
    def simple_ik(target_position):
        """Simple inverse kinematics for demonstration"""
        x, y, z = target_position
        
        # Simple heuristic joint calculation
        joint1 = math.atan2(y, x) if abs(x) > 0.01 else 0
        joint2 = 0.8
        joint3 = -0.6
        joint4 = 0.5
        joint5 = 0.0
        
        return [joint1, joint2, joint3, joint4, joint5]

class SafetyMonitor:
    """Monitor robot safety conditions"""
    
    def __init__(self):
        self.obstacle_history = []
    
    def check_joint_limits(self, joint_angles):
        """Check if joint angles are within safe limits"""
        limits = [
            (-3.14, 3.14),  # Joint 1
            (0.1, 1.0),     # Joint 2
            (-1.0, -0.1),   # Joint 3
            (-1.0, 1.0),    # Joint 4
            (-1.0, 1.0)     # Joint 5
        ]
        
        for i, angle in enumerate(joint_angles):
            if angle < limits[i][0] or angle > limits[i][1]:
                return False, f"Joint {i+1} out of limits: {angle}"
        
        return True, "All joints within limits"
