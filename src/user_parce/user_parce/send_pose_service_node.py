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
        ['move', start[0], start[1], 0.2],
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
                return -1

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
#               User Input
# ========================================
def user_input(node):
    while True:

        while True:
            try:
                user_input = input('\nPlease Enter Start x and y position in meters e.g. 0.2 0.4 (or q to quit): ').strip().lower()

                # Quit
                if user_input == 'q':
                    print('Exiting...')
                    return
                
                pos_1 = user_input.split()

                # Not enough values
                if len(pos_1) < 2:
                    print('ERROR - Missing Parameters')
                    continue

                x1 = float(pos_1[0])
                y1 = float(pos_1[1])

                # Out of rough range
                if ((x1**2 + y1**2) < 0.08) or ((-0.4 < x1 < 0) and (abs(y1) < 0.2)):
                    print('ERROR - Too close to base')
                    continue
                elif (abs(y1) > 0.4) and (x1 == 0.0):
                    print('ERROR - y value too large, robot will tip')
                    continue
                elif (x1**2 + y1**2) > 0.25:
                    print('ERROR - Out of reach')
                    continue

                break

            except:
                ValueError
                print('ERROR - Invalid Input.')

        while True:
            try:
                user_input = input('\nPlease Enter End x and y position in meters e.g. 0.3 0.2 (or q to quit): ').strip().lower()

                # Quit
                if user_input == 'q':
                    print('Exiting...')
                    return
                
                pos_2 = user_input.split()

                # Not enough values
                if len(pos_2) < 2:
                    print('ERROR - Missing Parameters')
                    continue
                
                x2 = float(pos_2[0])
                y2 = float(pos_2[1])

                # Out of rough range
                if ((x2**2 + y2**2) < 0.08) or ((-0.4 < x2 < 0) and (abs(y2) < 0.2)):
                    print('ERROR - Too close to base')
                    continue
                elif (abs(y2) > 0.4) and (x2 == 0.0):
                    print('ERROR - y value too large, robot will tip')
                    continue
                elif (x2**2 + y2**2) > 0.25:
                    print('ERROR - Out of reach')
                    continue

                break
        
            except:
                ValueError
                print('ERROR - Invalid Input.')

            print()

        start = [float(x1), float(y1)]
        end = [float(x2), float(y2)]
        response = movement_seq(node, start, end)

        if response == -1:
            pass

    return
        


# ========================================
#                   Main
# ========================================
def main(args=None):
    rclpy.init(args=args)
    node = CommandRequestServices()
    user_input(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()