"""Small geometry helpers shared across the package."""

import math
from typing import Tuple

from geometry_msgs.msg import PoseStamped

from warehouse_waypoints.config.waypoints import Waypoint


def yaw_to_quaternion(yaw: float) -> Tuple[float, float, float, float]:
    """
    Convert a 2D heading into a (x, y, z, w) quaternion.

    Args
    ----
    yaw : float
        Heading in radians around the Z axis.

    Returns
    -------
    Tuple[float, float, float, float]
        The (x, y, z, w) quaternion components. x and y are always 0
        since this is a planar rotation.

    """
    return (0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0))


def waypoint_to_pose_stamped(
    waypoint: Waypoint,
    frame_id: str,
    stamp,
) -> PoseStamped:
    """
    Build a PoseStamped message from a Waypoint.

    Args
    ----
    waypoint : Waypoint
        The waypoint to convert.
    frame_id : str
        The TF frame the pose is expressed in (typically map).
    stamp
        A ROS time message from node.get_clock().now().to_msg().

    Returns
    -------
    PoseStamped
        A fully populated PoseStamped message.

    """
    pose = PoseStamped()
    pose.header.frame_id = frame_id
    pose.header.stamp = stamp
    pose.pose.position.x = waypoint.x
    pose.pose.position.y = waypoint.y
    qx, qy, qz, qw = yaw_to_quaternion(waypoint.yaw)
    pose.pose.orientation.x = qx
    pose.pose.orientation.y = qy
    pose.pose.orientation.z = qz
    pose.pose.orientation.w = qw
    return pose
