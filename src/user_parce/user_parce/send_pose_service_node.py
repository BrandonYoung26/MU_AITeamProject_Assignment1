# ========================================
#                 Modules
# ========================================
import rclpy
from rclpy.node import Node
from custom_interfaces.srv import PoseCoords, MoveTransfer

import numpy as np


# ========================================
#                   Class
# ========================================
class SendPoseService(Node):
    # ========== Initialize Class ==========
    def __init__(self):
        super().__init__('send_pose_service')
        self._srv = self.create_service(PoseCoords, 'pose_coords', self.pose_coords_cb)

        self._cli = self.create_client(MoveTransfer, 'move_transfer')
        while not self._cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('MoveTransfer service not available, waiting again...')

    # ========== Get user pose ==========
    async def pose_coords_cb(self, request, response):
        start = request.start_pos
        goal = request.goal_pos
        goal = np.array(goal, dtype=np.float64)
        self.get_logger().info(f'start: {start}')
        self.get_logger().info(f'goal: {goal}')

        self.get_logger().info("#Setting goal")


        # !!! Test
        req = MoveTransfer.Request()
        req.goal = goal
        future = await self._cli.call_async(req)

        result = MoveTransfer.Response

        response.status = result.status

        return response




# ========================================
#                   Main
# ========================================
def main(args=None):
    rclpy.init(args=args)
    node = SendPoseService()
    rclpy.spin(node)

    rclpy.shutdown()

if __name__ == '__main__':
    main()