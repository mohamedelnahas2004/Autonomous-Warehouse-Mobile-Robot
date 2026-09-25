"""
Sequential navigation logic for the warehouse waypoint mission.

This module only decides which goal to send next, waits for Nav2's
result, and handles timed waits. It has no knowledge of how waypoints
are visualized in RViz.
"""

from enum import auto, Enum
import time
from typing import Dict, List, Optional

from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy
from rclpy.node import Node

from warehouse_waypoints.config.waypoints import Waypoint
from warehouse_waypoints.markers.waypoint_marker_publisher import (
    WaypointMarkerPublisher,
)
from warehouse_waypoints.utils.geometry import waypoint_to_pose_stamped


MAP_FRAME_ID: str = 'map'
NAVIGATOR_SPIN_TIMEOUT_SEC: float = 0.1


class MissionOutcome(Enum):
    """Final result of running a full waypoint mission."""

    SUCCEEDED = auto()
    GOAL_FAILED = auto()


class MissionPlanner:
    """
    Drive the robot through an ordered sequence of waypoints.

    Delegates marker visualization to a WaypointMarkerPublisher and
    goal execution to Nav2's BasicNavigator, so this class contains
    only sequencing/state-machine logic.
    """

    def __init__(
        self,
        node: Node,
        navigator: BasicNavigator,
        marker_publisher: WaypointMarkerPublisher,
        waypoints: Dict[str, Waypoint],
        mission_order: List[str],
        wait_durations_sec: Dict[str, float],
    ) -> None:
        """
        Initialize the mission planner.

        Args:
        ----
        node : Node
            ROS node used for spinning and logging.
        navigator : BasicNavigator
            Nav2 BasicNavigator used to send goals.
        marker_publisher : WaypointMarkerPublisher
            Publisher used to reflect the active goal in RViz.
        waypoints : Dict[str, Waypoint]
            Mapping of station name to Waypoint.
        mission_order : List[str]
            Ordered list of station names to visit.
        wait_durations_sec : Dict[str, float]
            Mapping of station name to how long to wait there after arrival,
            in seconds. Stations absent from this mapping are not waited at.

        """
        self._node = node
        self._navigator = navigator
        self._marker_publisher = marker_publisher
        self._waypoints = waypoints
        self._mission_order = mission_order
        self._wait_durations_sec = wait_durations_sec

    def run(self) -> MissionOutcome:
        """
        Execute the full mission sequence.

        Returns
        -------
        MissionOutcome
            MissionOutcome.SUCCEEDED if every goal in mission_order was
            reached, otherwise MissionOutcome.GOAL_FAILED.

        """
        self._marker_publisher.set_active_goal(None)

        for station_name in self._mission_order:
            if not self._navigate_to(station_name):
                self._marker_publisher.set_active_goal(None)
                return MissionOutcome.GOAL_FAILED
            self._wait_if_required(station_name)

        self._marker_publisher.set_active_goal(None)
        self._node.get_logger().info(
            'Mission complete. Robot returned Home.'
        )
        return MissionOutcome.SUCCEEDED

    def _navigate_to(self, station_name: str) -> bool:
        """
        Send one Nav2 goal and block until it finishes.

        Args:
        ----
        station_name : str
            Name of the waypoint to navigate to.

        Returns
        -------
        bool
            True if Nav2 reported success, False otherwise.

        """
        self._node.get_logger().info(
            f"Setting '{station_name}' as active goal."
        )
        self._marker_publisher.set_active_goal(station_name)

        waypoint = self._waypoints[station_name]
        stamp = self._node.get_clock().now().to_msg()
        goal_pose = waypoint_to_pose_stamped(
            waypoint, MAP_FRAME_ID, stamp
        )
        self._navigator.goToPose(goal_pose)

        while not self._navigator.isTaskComplete():
            rclpy.spin_once(
                self._node,
                timeout_sec=NAVIGATOR_SPIN_TIMEOUT_SEC,
            )

        result = self._navigator.getResult()
        if result != TaskResult.SUCCEEDED:
            self._node.get_logger().error(
                f"Failed to reach '{station_name}' "
                f'(Nav2 result: {result}). Aborting mission.'
            )
            return False

        self._node.get_logger().info(
            f"Reached '{station_name}'."
        )
        return True

    def _wait_if_required(self, station_name: str) -> None:
        """
        Block for the configured wait duration at station_name, if any.

        Args:
        ----
        station_name : str
            Name of the station just reached.

        """
        wait_seconds: Optional[float] = (
            self._wait_durations_sec.get(station_name)
        )
        if wait_seconds is None:
            return

        self._node.get_logger().info(
            f"Waiting {wait_seconds:.0f}s at '{station_name}'..."
        )
        start_time = time.time()
        while time.time() - start_time < wait_seconds:
            rclpy.spin_once(
                self._node,
                timeout_sec=NAVIGATOR_SPIN_TIMEOUT_SEC,
            )
