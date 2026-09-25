"""Unit tests for warehouse_waypoints.markers.waypoint_marker_publisher."""

from rclpy.time import Time

from warehouse_waypoints.config.waypoints import Waypoint
from warehouse_waypoints.markers.waypoint_marker_publisher import (
    ACTIVE_GOAL_COLOR,
    build_marker_array,
    INACTIVE_GOAL_COLOR,
)

TEST_WAYPOINTS = {
    'A': Waypoint(name='A', x=0.0, y=0.0, yaw=0.0),
    'B': Waypoint(name='B', x=1.0, y=1.0, yaw=0.0),
}


def _sphere_colors_by_name(marker_array, waypoints):
    """Map each waypoint name to its sphere marker's RGBA color tuple."""
    names_by_sphere_id = {index * 2: wp.name for index, wp in enumerate(waypoints.values())}
    colors = {}
    for marker in marker_array.markers:
        if marker.ns == 'waypoints' and marker.id in names_by_sphere_id:
            name = names_by_sphere_id[marker.id]
            colors[name] = (marker.color.r, marker.color.g, marker.color.b, marker.color.a)
    return colors


def test_active_goal_is_green_and_others_are_blue():
    stamp = Time().to_msg()
    marker_array = build_marker_array(TEST_WAYPOINTS, active_name='B', stamp=stamp)
    colors = _sphere_colors_by_name(marker_array, TEST_WAYPOINTS)

    assert colors['B'] == ACTIVE_GOAL_COLOR
    assert colors['A'] == INACTIVE_GOAL_COLOR


def test_no_active_goal_makes_everything_blue():
    stamp = Time().to_msg()
    marker_array = build_marker_array(TEST_WAYPOINTS, active_name=None, stamp=stamp)
    colors = _sphere_colors_by_name(marker_array, TEST_WAYPOINTS)

    assert colors['A'] == INACTIVE_GOAL_COLOR
    assert colors['B'] == INACTIVE_GOAL_COLOR


def test_marker_array_contains_sphere_and_label_per_waypoint():
    stamp = Time().to_msg()
    marker_array = build_marker_array(TEST_WAYPOINTS, active_name=None, stamp=stamp)

    assert len(marker_array.markers) == len(TEST_WAYPOINTS) * 2
