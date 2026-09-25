"""
Publishes color-coded RViz markers for the warehouse waypoints.

This module is only responsible for building and publishing
visualization_msgs/MarkerArray messages. It has no knowledge of
navigation state machines or Nav2 goals beyond which name is active.
"""

import time
from typing import Dict, Optional, Tuple

from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray

from warehouse_waypoints.config.waypoints import Waypoint

MAP_FRAME_ID: str = 'map'
MARKER_TOPIC: str = '/waypoint_markers'

# Marker geometry
SPHERE_SCALE_METERS: float = 0.3
SPHERE_HEIGHT_METERS: float = 0.15
LABEL_HEIGHT_METERS: float = 0.55
LABEL_TEXT_SCALE_METERS: float = 0.25

# Colors as (r, g, b, a), each in [0.0, 1.0]
ACTIVE_GOAL_COLOR: Tuple[float, float, float, float] = (
    0.0, 0.8, 0.1, 1.0
)  # green
INACTIVE_GOAL_COLOR: Tuple[float, float, float, float] = (
    0.0, 0.3, 1.0, 1.0
)  # blue
LABEL_COLOR: Tuple[float, float, float, float] = (
    1.0, 1.0, 1.0, 1.0
)  # white

# RViz subscribers that join right when the active goal changes can miss a
# single publish; publishing again shortly after covers that case.
REPUBLISH_DELAY_SEC: float = 0.2


def _set_color(
    marker: Marker, rgba: Tuple[float, float, float, float]
) -> None:
    """Apply an (r, g, b, a) tuple to a Marker's color field."""
    marker.color.r, marker.color.g, marker.color.b, marker.color.a = rgba


def _build_sphere_marker(
    waypoint: Waypoint,
    marker_id: int,
    stamp,
    is_active: bool,
) -> Marker:
    """
    Build the sphere marker representing one waypoint's position.

    Args:
    ----
    waypoint : Waypoint
        The waypoint to visualize.
    marker_id : int
        Unique marker ID within the waypoints namespace.
    stamp
        Current ROS time to stamp the marker with.
    is_active : bool
        True if this waypoint is the currently active Nav2 goal.

    Returns
    -------
    Marker
        A populated SPHERE Marker.

    """
    marker = Marker()
    marker.header.frame_id = MAP_FRAME_ID
    marker.header.stamp = stamp
    marker.ns = 'waypoints'
    marker.id = marker_id
    marker.type = Marker.SPHERE
    marker.action = Marker.ADD
    marker.pose.position.x = waypoint.x
    marker.pose.position.y = waypoint.y
    marker.pose.position.z = SPHERE_HEIGHT_METERS
    marker.pose.orientation.w = 1.0
    marker.scale.x = marker.scale.y = marker.scale.z = SPHERE_SCALE_METERS
    _set_color(marker, ACTIVE_GOAL_COLOR if is_active else INACTIVE_GOAL_COLOR)
    return marker


def _build_label_marker(
    waypoint: Waypoint,
    marker_id: int,
    stamp,
) -> Marker:
    """
    Build the text marker showing a waypoint's station name.

    Args:
    ----
    waypoint : Waypoint
        The waypoint to label.
    marker_id : int
        Unique marker ID within the waypoint_labels namespace.
    stamp
        Current ROS time to stamp the marker with.

    Returns
    -------
    Marker
        A populated TEXT_VIEW_FACING Marker.

    """
    marker = Marker()
    marker.header.frame_id = MAP_FRAME_ID
    marker.header.stamp = stamp
    marker.ns = 'waypoint_labels'
    marker.id = marker_id
    marker.type = Marker.TEXT_VIEW_FACING
    marker.action = Marker.ADD
    marker.pose.position.x = waypoint.x
    marker.pose.position.y = waypoint.y
    marker.pose.position.z = LABEL_HEIGHT_METERS
    marker.scale.z = LABEL_TEXT_SCALE_METERS
    _set_color(marker, LABEL_COLOR)
    marker.text = waypoint.name
    return marker


def build_marker_array(
    waypoints: Dict[str, Waypoint],
    active_name: Optional[str],
    stamp,
) -> MarkerArray:
    """
    Build the full MarkerArray for all waypoints.

    Pure function: the same inputs always produce the same output,
    which makes this straightforward to unit test without a running
    ROS node.

    Args
    ----
    waypoints : Dict[str, Waypoint]
        Mapping of station name to Waypoint.
    active_name : Optional[str]
        Name of the currently active Nav2 goal, or None if no goal is
        active (every marker renders as inactive/blue).
    stamp
        Current ROS time to stamp every marker with.

    Returns
    -------
    MarkerArray
        A MarkerArray with one sphere and one text label per waypoint.

    """
    marker_array = MarkerArray()
    for index, waypoint in enumerate(waypoints.values()):
        is_active = waypoint.name == active_name
        sphere_id = index * 2
        label_id = index * 2 + 1
        marker_array.markers.append(
            _build_sphere_marker(waypoint, sphere_id, stamp, is_active)
        )
        marker_array.markers.append(
            _build_label_marker(waypoint, label_id, stamp)
        )
    return marker_array


class WaypointMarkerPublisher:
    """
    Publishes /waypoint_markers and tracks which goal is currently active.

    Owns the ROS publisher but delegates message construction to
    build_marker_array, keeping ROS plumbing separate from the pure
    marker-building logic.
    """

    def __init__(self, node: Node, waypoints: Dict[str, Waypoint]) -> None:
        """
        Initialize the publisher on the given node.

        Args:
        ----
        node : Node
            The ROS node to create the publisher on and read the clock from.
        waypoints : Dict[str, Waypoint]
            Mapping of station name to Waypoint to publish markers for.

        """
        self._node = node
        self._waypoints = waypoints
        self._publisher = node.create_publisher(MarkerArray, MARKER_TOPIC, 10)
        self._active_name: Optional[str] = None

    def set_active_goal(self, name: Optional[str]) -> None:
        """
        Mark name as the active goal and republish all markers.

        Args:
        ----
        name : Optional[str]
            Station name to highlight in green, or None to clear the
            active goal (all markers become blue).

        """
        self._active_name = name
        self._publish()
        time.sleep(REPUBLISH_DELAY_SEC)
        self._publish()

    def _publish(self) -> None:
        """Build and publish the current MarkerArray."""
        stamp = self._node.get_clock().now().to_msg()
        marker_array = build_marker_array(
            self._waypoints, self._active_name, stamp
        )
        self._publisher.publish(marker_array)
