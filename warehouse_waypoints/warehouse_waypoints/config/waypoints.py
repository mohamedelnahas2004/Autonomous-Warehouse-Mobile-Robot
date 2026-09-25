"""
Static waypoint configuration for the warehouse mission.

This module holds ONLY data — no navigation or ROS logic lives here.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Waypoint:
    """
    A single named waypoint pose in the map frame.

    Attributes
    ----------
    name : str
        Human-readable station name, also used as the RViz marker label.
    x : float
        X position in meters, map frame.
    y : float
        Y position in meters, map frame.
    yaw : float
        Heading in radians, map frame.

    """

    name: str
    x: float
    y: float
    yaw: float


# Real poses must be recorded from the robot (e.g. `ros2 topic echo /amcl_pose
# --once` at each station) and substituted here before running the mission.
WAYPOINTS: Dict[str, Waypoint] = {
    'Home': Waypoint(name='Home', x=0.0, y=0.0, yaw=0.0),
    'Loading': Waypoint(name='Loading', x=7.782053842839245, y=7.420772652392393, yaw=0.0),
    'Storage': Waypoint(name='Storage', x=20.000934662165207, y=-2.415622611057596, yaw=-1.5708),
    'Shipping': Waypoint(name='Shipping', x=-5.930928476565102, y=-5.406362903539103, yaw=3.1416),
}

# Order the robot visits waypoints in. Home is both the mission start
# (where the robot must already be localized) and its final destination.
MISSION_ORDER: List[str] = ['Loading', 'Storage', 'Shipping', 'Home']

# Named stop -> seconds to wait there once reached, before the next goal.
WAIT_DURATIONS_SEC: Dict[str, float] = {'Loading': 30.0}
