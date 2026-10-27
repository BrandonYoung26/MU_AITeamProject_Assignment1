# ========================================
#                 Modules
# ========================================
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup

from moveit_msgs.msg import MotionPlanRequest, Constraints, PositionConstraint, OrientationConstraint, JointConstraint
from moveit_msgs.action import MoveGroup
from shape_msgs.msg import SolidPrimitive

from geometry_msgs.msg import PoseStamped, Quaternion

from custom_interfaces.srv import MoveCommand, GripCommand

import numpy as np



# ========================================
#                Node Class
# ========================================
class RX200MoveItActionClient(Node):
    # ========== Initialize Class ==========
    def __init__(self):
        super().__init__('rx200_moveit_control')

        self.cb_group = ReentrantCallbackGroup()

        # Robot action client
        self._client = ActionClient(self, MoveGroup, '/move_action', callback_group=self.cb_group)
        while not self._client.wait_for_server(1.0):
            self.get_logger().warning("[Action Client] Warning - Action server not up")

        # Input Pose
        self._srv = self.create_service(MoveCommand, 'move_command', self._move_command_cb, callback_group=self.cb_group)

        # Input Gripper
        self._srv = self.create_service(GripCommand, 'grip_command', self._grip_command_cb, callback_group=self.cb_group)
        

        self.arm_group = "interbotix_arm"
        self.gripper_group = "interbotix_gripper"
        self.ee_link = "rx200/ee_gripper_link"
        self.base_link = "rx200/base_link"
        self.gripper_joint = 'left_finger'

        # initial position
        move_goal = self.send_ee_pose(0.3, 0.0, 0.3)
        grip_goal = self.send_gr_pose(True)
        self._client.send_goal_async(move_goal, self._feedback_cb)
        self._client.send_goal_async(grip_goal, self._feedback_cb)

        self.get_logger().info('[Action Client] RX200 MoveIt Client Initialised')


# ========== EE Position ==========
    def send_ee_pose(self, x, y, z, w=1.0):
        p = PoseStamped()
        p.header.frame_id = self.base_link
        p.pose.position.x = x
        p.pose.position.y = y
        p.pose.position.z = z 

        # Yaw for y axis travel with flat gripper
        yaw = np.arctan2(y, x)
        qz = np.sin(yaw/2)
        qw = np.cos(yaw/2)

        p.pose.orientation = Quaternion(x=0.0, y=0.0, z=qz, w=qw)

        # moveit action request
        req = MotionPlanRequest()
        req.group_name = self.arm_group
        req.max_velocity_scaling_factor = 0.1
        req.max_acceleration_scaling_factor = 0.1
        req.allowed_planning_time = 5.0
        req.num_planning_attempts = 10


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

        # !!! Deprecated
        #future = self._client.send_goal_async(goal, self._feedback_cb)
        #future.add_done_callback(self._goal_response_cb)

        return goal

# ========== Gripper Actuation ==========
    def send_gr_pose(self, open=True):
        req = MotionPlanRequest()
        req.group_name = self.gripper_group
        req.allowed_planning_time = 2.0
        req.num_planning_attempts = 1

        # joint constraint
        jc = JointConstraint()
        jc.joint_name = self.gripper_joint
        jc.position = 0.35 if open else 0.13
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

        # !!! Deprecated
        #future = self._client.send_goal_async(goal)
        #future.add_done_callback(self._goal_response_cb)

        return goal


# ========== Feedback Callback ==========
    def _feedback_cb(self, feedback_msg):
        state = feedback_msg.feedback.state # why not future (question)
        self.get_logger().info(f'[Action Client] Current state: {state}')


# ========== Command Move Callback ==========
    async def _move_command_cb(self, request, response):
        request_goal = request.goal
        self.get_logger().info(f'[Action Client] goal: {request_goal}')

        moveit_goal = self.send_ee_pose(request_goal[0], request_goal[1], request_goal[2])

        handle_goal = await self._client.send_goal_async(moveit_goal, self._feedback_cb)
        if not handle_goal.accepted:
            response.status = -1
            return response
        
        result = await handle_goal.get_result_async()
        code = result.result.error_code.val
        self.get_logger().info(f'[Action Client] Result code {code}')

        response.status = code

        return response


# ========== Command Gripper Callback ==========
    async def _grip_command_cb(self, request, response):
        request_goal = request.grip
        self.get_logger().info(f'[Action Client] grip: {request_goal}')

        moveit_goal = self.send_gr_pose(request_goal)

        handle_goal = await self._client.send_goal_async(moveit_goal, self._feedback_cb)
        if not handle_goal.accepted:
            response.status = -1
            return response
        
        result = await handle_goal.get_result_async()
        code = result.result.error_code.val
        self.get_logger().info(f'[Action Client] Result code {code}')

        response.status = code

        return response


# ========== !!! Deprecated: Response Callback ==========
    def _goal_response_cb(self, future):
        handle_goal = future.result()
        if not handle_goal.accepted:
            self.get_logger().warning('[Action Client] Warning - Goal rejected by MoveIt Server.')
            return 
        self.get_logger().info('[Action Client] Goal accepected.')
        handle_goal.get_result_async().add_done_callback(self._result_cb)


# ========== !!! Deprecated: Result Callback ==========
    def _result_cb(self, future):
        result = future.result().result
        code = result.error_code.val
        self.get_logger().info(f'[Action Client] Result code {code}')



# ========================================
#                   Main
# ========================================
def main(args=None):
    rclpy.init(args=args)
    node = RX200MoveItActionClient()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()