# ========================================
#                 Modules
# ========================================
import rclpy
from rclpy.node import Node
from custom_interfaces.srv import PoseCoords, MoveTransfer


# ========================================
#                   Class
# ========================================
class SendPoseService(Node):
    # ========== Initialize Class ==========
    def __init__(self):
        super().__init__('send_pose_service')
        self._srv = self.create_service(PoseCoords, 'pose_coords', self.pose_coords_cb)
        self._cli = self.create_client(MoveTransfer, 'move_transfer')

    # ========== Get user pose ==========
    def pose_coords_cb(self, request, response):
        start = request.start_pos
        goal = request.goal_pos
        self.get_logger().info(f'start: {start}')
        self.get_logger().info(f'goal: {goal}')

        response.status = 0

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