"""
Entry point for the warehouse waypoint mission.

Wires together the marker publisher and the mission planner, then
runs the mission once. Contains no business logic of its own.
"""

import sys

from nav2_simple_commander.robot_navigator import BasicNavigator
import rclpy

from warehouse_waypoints.config.waypoints import (
    MISSION_ORDER,
    WAIT_DURATIONS_SEC,
    WAYPOINTS,
)
from warehouse_waypoints.markers.waypoint_marker_publisher import (
    WaypointMarkerPublisher,
)
from warehouse_waypoints.navigation.mission_planner import (
    MissionOutcome,
    MissionPlanner,
)

NODE_NAME: str = 'waypoint_mission_node'


def main() -> None:
    """Run the warehouse waypoint mission once, then shut down cleanly."""
    rclpy.init()

    node = rclpy.create_node(NODE_NAME)
    navigator = BasicNavigator()
    marker_publisher = WaypointMarkerPublisher(node, WAYPOINTS)

    # The robot must already be localized at Home before this runs
    # (e.g. via "2D Pose Estimate" in RViz).
    navigator.waitUntilNav2Active()

    planner = MissionPlanner(
        node=node,
        navigator=navigator,
        marker_publisher=marker_publisher,
        waypoints=WAYPOINTS,
        mission_order=MISSION_ORDER,
        wait_durations_sec=WAIT_DURATIONS_SEC,
    )

    outcome = planner.run()

    node.destroy_node()
    rclpy.shutdown()

    if outcome != MissionOutcome.SUCCEEDED:
        sys.exit(1)


if __name__ == '__main__':
    main()
