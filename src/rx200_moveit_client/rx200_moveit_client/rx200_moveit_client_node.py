# ========================================
#                 Modules
# ========================================
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from moveit_msgs.msg import MotionPlanRequest, Constraints, PositionConstraint, OrientationConstraint, JointConstraint
from moveit_msgs.action import MoveGroup
from shape_msgs.msg import SolidPrimitive

from geometry_msgs.msg import PoseStamped, Quaternion

from custom_interfaces.srv import MoveTransfer


# ========================================
#                   Class
# ========================================
class RX200MoveItActionClient(Node):
    # ========== Initialize Class ==========
    def __init__(self):
        super().__init__('rx200_moveit_control')

        # Robot action client
        self._client = ActionClient(self, MoveGroup, '/move_action')
        while not self._client.wait_for_server(1.0):
            self.get_logger().warning("[WARNING] Action server not up")

        # input server
        self._srv = self.create_service(MoveTransfer, 'move_transfer', self._move_transfer_cb)
        

        self.arm_group = "interbotix_arm"
        self.gripper_group = "interbotix_gripper"
        self.ee_link = "rx200/ee_gripper_link"
        self.base_link = "rx200/ee_base_link"
        self.gripper_joint = 'left_finger'

        # initial config parameters
        #self.send_gr_pose(True)

        self.declare_parameter('gripper_start_state', value = True)
        self.send_gr_pose(self.get_parameter('gripper_start_state').value)


        self.get_logger().info('RX200 MoveIt Client Initialised')

# ========== EE Position ==========
    def send_ee_pose(self, x, y, z, w=1.0):
        p = PoseStamped()
        p.header.frame_id = self.base_link
        p.pose.position.x = x
        p.pose.position.y = y
        p.pose.position.z = z 
        p.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=w) #--fix--

        # moveit action request
        req = MotionPlanRequest()
        req.group_name = self.arm_group
        #req.pipeline_id = "pilz_industrial_motion_planner"
        #req.planner_id = "LIN"  # --- linear?
        #req.max_velocity_scaling_factor = 0.5
        #req.max_acceleration_scaling_factor = 0.5
        req.allowed_planning_time = 5.0
        req.num_planning_attempts = 3


        # position tolerence
        pc = PositionConstraint()
        pc.header.frame_id = self.base_link
        pc.link_name = self.ee_link
        sp = SolidPrimitive()
        sp.type = SolidPrimitive.SPHERE
        sp.dimensions = [0.01]
        pc.constraint_region.primitives = [sp]
        pc.constraint_region.primitive_poses = [p.pose]
        pc.weight = 1.0

        # orientation tolerance
        oc = OrientationConstraint()
        oc.header.frame_id = self.base_link
        oc.link_name = self.ee_link
        oc.orientation = p.pose.orientation
        oc.absolute_x_axis_tolerance = 0.05
        oc.absolute_y_axis_tolerance = 0.05
        oc.absolute_z_axis_tolerance = 0.05
        oc.weight = 1.0

        # goal tolerance 
        gc = Constraints()
        gc.position_constraints = [pc]
        gc.orientation_constraints = [oc]
        req.goal_constraints = [gc]

        goal = MoveGroup.Goal()
        goal.request = req
        goal.planning_options.plan_only = False
        goal.planning_options.replan = True
        goal.planning_options.look_around = False

        future = self._client.send_goal_async(goal, self._feedback_cb)
        future.add_done_callback(self._goal_response_cb)

# ========== Gripper Actuation ==========
    def send_gr_pose(self, open=True):
        req = MotionPlanRequest()
        req.group_name = self.gripper_group
        req.allowed_planning_time = 2.0
        req.num_planning_attempts = 1

        # joint constraint
        jc = JointConstraint()
        jc.joint_name = self.gripper_joint
        jc.position = 0.35 if open else 0.0
        jc.tolerance_above = 0.01
        jc.tolerance_below = 0.01
        jc.weight = 1.0

        # goal constraints
        gc = Constraints()
        gc.joint_constraints = [jc]
        req.goal_constraints = [gc]


        goal = MoveGroup.Goal()
        goal.request = req
        goal.planning_options.plan_only = False
        future = self._client.send_goal_async(goal)
        future.add_done_callback(self._goal_response_cb)

# ========== Response Callback ==========
    def _goal_response_cb(self, future):
        handle_goal = future.result()
        if not handle_goal.accepted:
            self.get_logger().warning('[Warning] Goal rejected by MoveIt Server.')
            return 
        self.get_logger().info('Goal accepected.')
        handle_goal.get_result_async().add_done_callback(self._result_cb)

# ========== Feedback Callback ==========
    def _feedback_cb(self, feedback_msg):
        state = feedback_msg.feedback.state # why not future (question)
        self.get_logger().info(f'Current state: {state}')

# ========== Result Callback ==========
    def _result_cb(self, future):
        result = future.result().result
        code = result.error_code.val
        self.get_logger().info(f'[Results] Result code {code}')

    def _move_transfer_cb(self, request, response):
        goal = request.goal
        self.send_ee_pose(goal[0], goal[1], goal[2])
        self.get_logger().info(f'goal: {goal}')
        

        response.status = 0

        return response


# ========================================
#                   Main
# ========================================
def main(args=None):
    rclpy.init(args=args)
    node = RX200MoveItActionClient()
    node.send_ee_pose(0.3, 0.0, 0.3)
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()