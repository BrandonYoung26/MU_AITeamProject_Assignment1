# ========================================
#                 Modules
# ========================================
import rclpy
from rclpy.node import Node

from custom_interfaces.srv import MoveCommand, GripCommand

import numpy as np


# ========================================
#                   Class
# ========================================
class CommandRequestServices(Node):
    # ========== Initialize Class ==========
    def __init__(self):
        super().__init__('command_request_services')

        self.move_cli = self.create_client(MoveCommand, 'move_command') 
        while not self.move_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('[Command Request] MoveCommand service not available, waiting again...')

        self.grip_cli = self.create_client(GripCommand, 'grip_command')
        while not self.grip_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('[Command Request] GripCommand service not available, waiting again...')

        self.get_logger().info('[Command Request] Command Client Initialized')
   

    # ========== Move Command ==========
    def move_command(self, goal_pose):
        request = MoveCommand.Request()
        request.goal = goal_pose

        return self.move_cli.call_async(request)

    # ========== Grip Command ==========
    def grip_command(self, grip_state):
        request = GripCommand.Request()
        request.grip = grip_state
    
        return self.grip_cli.call_async(request)


    
# ========================================
#           Movement Sequencer
# ========================================
def movement_seq(node, start, end):

    seq = [
        ['grip', True],
        ['move', start[0], start[1], 0.9],
        ['move', start[0], start[1], 0.05],
        ['grip', False],
        ['move', start[0], start[1], 0.2],
        ['move', end[0], end[1], 0.2],
        ['move', end[0], end[1], 0.05],
        ['grip', True],
        ['move', end[0], end[1], 0.2],
        ['move', 0.3, 0.0, 0.3]
    ]

    # ========== Sequencer ==========
    for i in range(len(seq)):
        # Gripper Command Request
        if seq[i][0] == 'grip':
            grip_state = seq[i][1]
            node.get_logger().info(f'[Command Request] Step {i+1} - {"Close" if grip_state == False else "Open"} Gripper')

            future = node.grip_command(grip_state)
            rclpy.spin_until_future_complete(node, future)
            reseponse = future.result()
            result = reseponse.status

            if result != 1:
                node.get_logger().info(f'[Command Request] Request Failed (Code: {result}, Exiting Sequence...)')
                return

            node.get_logger().info(f'[Command Request] Request Successful')

        # Gripper Command Request
        elif seq[i][0] == 'move':
            x = seq[i][1]
            y = seq[i][2]
            z = seq[i][3]
            node.get_logger().info(f'[Command Request] Step {i+1} - Sending Goal: ({x}, {y}, {z})')

            future = node.move_command([x, y, z])
            rclpy.spin_until_future_complete(node, future)
            reseponse = future.result()
            result = reseponse.status

            if result != 1:
                node.get_logger().info(f'[Command Request] Request Failed (Code: {result}, Exiting...)')
                return

            node.get_logger().info(f'[Command Request] Request Successful')

    node.get_logger().info(f'[Command Request] Sequenced Completed Successfully.')


# ========================================
#                   Main
# ========================================
def main(args=None):
    rclpy.init(args=args)
    node = CommandRequestServices()

    start = [0.3, 0.3]
    end = [0.3, -0.3]
    movement_seq(node, start, end)

    rclpy.shutdown()

if __name__ == '__main__':
    main()