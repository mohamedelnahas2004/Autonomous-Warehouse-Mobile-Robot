# Autonomous Warehouse Mobile Robot

Autonomous multi-waypoint navigation for a simulated TurtleBot3 Burger
in a Gazebo warehouse, built on ROS 2 Jazzy, SLAM Toolbox, AMCL, and
Nav2, with a custom waypoint mission system.

## 1. Project Overview

The robot maps a simulated warehouse with SLAM Toolbox, localizes on
the saved map with AMCL, and then autonomously visits a fixed set of
warehouse stations using Nav2 for path planning and control. A custom
ROS 2 package (`warehouse_waypoints`) sequences the mission, sends
goals to Nav2, and visualizes the waypoints in RViz2.

Data flow:

```
Gazebo Warehouse
      ↓
TurtleBot3 Burger
      ↓
Sensors / Odometry / TF
      ↓
SLAM Toolbox
      ↓
Warehouse Map
      ↓
AMCL Localization
      ↓
Nav2
      ↓
Waypoint Mission
      ↓
Autonomous Navigation
```

## 2. Mission

```
Home → Loading → Storage → Shipping → Home
```

The robot starts at **Home**. Home is the initial position and is
**not** sent as a navigation goal itself — the first goal is Loading.

1. Start at Home.
2. Navigate to Loading.
3. Wait 30 seconds at Loading.
4. Navigate to Storage.
5. Navigate to Shipping.
6. Return to Home.
7. Mission complete.

## 3. Technologies

| Component        | Version / Detail                     |
|-------------------|--------------------------------------|
| ROS 2             | Jazzy                                |
| Simulator         | Gazebo Harmonic                      |
| Robot             | TurtleBot3 Burger with camera (`turtlebot3_burger_cam`) |
| Mapping           | SLAM Toolbox                         |
| Localization      | AMCL                                 |
| Navigation        | Nav2                                 |
| Visualization     | RViz2                                |
| Mission logic     | Custom `warehouse_waypoints` package |

## 4. System Architecture

```
AMCL
 ↓
TF map → odom
 ↓
Costmaps (global + local)
 ↓
Planner Server
 ↓
Controller Server
 ↓
Behavior Server
 ↓
BT Navigator
 ↓
/cmd_vel
 ↓
TurtleBot3
```

- **Global Costmap** — a map-frame costmap built from the static
  warehouse map plus currently sensed obstacles; used for global
  planning.
- **Local Costmap** — a small rolling window around the robot in the
  odom frame, used for short-horizon obstacle avoidance.
- **Global Planner (Planner Server)** — computes a path from the
  robot's current pose to the goal across the global costmap.
- **Local Controller (Controller Server)** — follows the global path
  while reacting to the local costmap, producing `/cmd_vel` commands.
- **Behavior Server** — runs recovery behaviors (spin, back up, wait,
  drive on heading) when navigation gets stuck.
- **BT Navigator** — a behavior tree that orchestrates planning,
  control, and recovery for each `navigate_to_pose` goal.

## 5. Repository Structure

```
warehouse-waypoint-nav-MohamedAbdElaal/
│
├── robot_navigation/
│   ├── config/
│   │   ├── amcl.yaml
│   │   ├── planner_server.yaml
│   │   ├── controller_server.yaml
│   │   ├── behavior_server.yaml
│   │   └── bt_navigator.yaml
│   ├── launch/
│   │   └── nav2_bringup.launch.py
│   ├── maps/
│   │   ├── warehouse_map.yaml
│   │   └── warehouse_map.pgm            
│   ├── rviz/
│   │   └── navigation.rviz
│   ├── CMakeLists.txt
│   └── package.xml
│
├── warehouse_waypoints/
│   ├── resource/
│   │   └── warehouse_waypoints
│   ├── warehouse_waypoints/
│   │   ├── config/
│   │   │   └── waypoints.py
│   │   ├── markers/
│   │   │   └── waypoint_marker_publisher.py
│   │   ├── navigation/
│   │   │   └── mission_planner.py
│   │   ├── nodes/
│   │   │   └── waypoint_mission_node.py
│   │   └── utils/
│   │       └── geometry.py
│   ├── package.xml
│   └── setup.py
│
├── images/
├── .gitignore
└── README.md
```

This repository assumes an existing localization package,
**`robot_localizition`** (spelling intentional — do not rename), is
also present in the workspace `src/` alongside these two packages.
Its structure and `CMakeLists.txt` are preserved unchanged:

```
robot_localizition/
├── CMakeLists.txt
├── config/
├── include/
├── launch/
├── map/
├── package.xml
├── README.md
├── rviz/
└── src/
```

## 6. Requirements

- ROS 2 Jazzy
- Gazebo Harmonic
- Nav2 (`nav2_bringup`, `nav2_amcl`, `nav2_map_server`, `nav2_planner`,
  `nav2_controller`, `nav2_behaviors`, `nav2_bt_navigator`,
  `nav2_lifecycle_manager`)
- SLAM Toolbox
- TurtleBot3 packages providing the `turtlebot3_burger_cam` model
  `[VERIFY FROM EXISTING PROJECT]`
- `rviz2`
- Python 3 / `rclpy`

## 7. Workspace Setup

The workspace is:

```
~/workspaces/nav_ws
```

Packages:

```
robot_localizition
warehouse_waypoints
robot_navigation
```

Verify with:

```bash
cd ~/workspaces/nav_ws
colcon list
```

Expected:

```
robot_localizition      src/robot_localizition
warehouse_waypoints     src/warehouse_waypoints
robot_navigation        src/robot_navigation
```

## 8. Build Instructions

```bash
source /opt/ros/jazzy/setup.bash
cd ~/workspaces/nav_ws
colcon build --symlink-install
source install/setup.bash
```

Verify:

```bash
ros2 pkg list | grep -E "robot_localizition|warehouse_waypoints|robot_navigation"
```

**Rebuild after:**
- changing `package.xml`
- changing `setup.py`
- changing `CMakeLists.txt`
- adding or installing launch files
- changing installed configuration files
- changing executable entry points

## 9. Launching the Warehouse Simulation

Launch Gazebo Harmonic with the warehouse world and the TurtleBot3
Burger (with camera):

```bash
source /opt/ros/jazzy/setup.bash
source ~/workspaces/nav_ws/install/setup.bash

ros2 launch <warehouse_simulation_package> warehouse_storage_launch.launch.py
```

> `[VERIFY FROM EXISTING PROJECT]` — the exact launch package and file
> name for the Gazebo warehouse world were not confirmed for this
> write-up. If your project already has a launch file named
> `warehouse_storage_launch.launch.py`, use that exact name and
> package; otherwise substitute your actual launch file here.

The robot model used is `turtlebot3_burger_cam`, described by
`turtlebot3_burger.urdf` and published on `/robot_description` via
Robot State Publisher.

Key topics exposed by the simulation:

```
/cmd_vel
/odom
/scan
/scan/points
/tf
/robot_description
```

Gazebo model enable topic (previously used):

```
/model/turtlebot3_burger_cam/enable
```

## 10. SLAM Mapping

The warehouse map is generated with SLAM Toolbox, **not** AMCL. SLAM
Toolbox builds the map while the robot moves; AMCL later localizes the
robot **on** that already-built map. They are not interchangeable:

- **SLAM Toolbox** → creates the map (mapping phase).
- **AMCL** → localizes the robot on a saved, static map (localization
  phase).

Mapping workflow:

1. Launch the Gazebo warehouse world (Section 9).
2. Confirm the robot's TF tree and Robot State Publisher are running.
3. Launch SLAM Toolbox in mapping mode:
   ```bash
   ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
   ```
   `[VERIFY FROM EXISTING PROJECT]` if a custom SLAM Toolbox launch
   file/parameters file is used instead of the stock one.
4. Open RViz2:
   ```bash
   rviz2
   ```
5. Set **Fixed Frame** to `map`.
6. Add/enable displays for: Map, LaserScan, TF, RobotModel.
7. Drive the robot (teleop or manual `/cmd_vel`) through the warehouse
   until the map covers the whole environment.
8. Verify the map is being built by watching the Map display update.
9. Save the map (Section 11).

## 11. Saving the Warehouse Map

Save the map published on `/map` using `map_saver_cli`:

```bash
ros2 run nav2_map_server map_saver_cli -f warehouse_map --ros-args -p save_map_timeout:=10000.0
```

This produces:

```
warehouse_map.yaml
warehouse_map.pgm
```

Move both files into `robot_navigation/maps/`. `warehouse_map.yaml`
references `warehouse_map.pgm` by filename and stores the map's
resolution, origin, and occupancy thresholds — the `.pgm` is the
actual occupancy-grid image, and the `.yaml` is only meaningful next
to it.

> `[VERIFY FROM EXISTING PROJECT]` — the resolution/origin values
> shipped in `robot_navigation/maps/warehouse_map.yaml` in this
> repository are placeholders and must be replaced with the values
> `map_saver_cli` actually prints for your saved warehouse map.

## 12. AMCL Localization

AMCL localizes the robot on the saved warehouse map. Configuration:
`robot_navigation/config/amcl.yaml`.

Key frames:

| Parameter        | Value           | Purpose |
|-------------------|-----------------|---------|
| `base_frame_id`   | `base_footprint` | The robot's body frame. |
| `global_frame_id` | `map`            | The fixed map frame AMCL localizes against. |
| `odom_frame_id`   | `odom`           | The continuous, drifting odometry frame. |

Key topics: `scan_topic: scan`, `map_topic: map`.

Parameter notes:

- **`DifferentialMotionModel`** — the odometry motion model for a
  differential-drive robot (TurtleBot3 Burger), used to predict how
  particles move between updates.
- **`min_particles` / `max_particles`** — bound the particle filter's
  population (500–2000): the pose belief is represented by this many
  weighted particles.
- **`pf_err` / `pf_z`** — control KLD-sampling: with probability
  `pf_z` (0.99), the estimated particle distribution stays within
  `pf_err` (0.05) of the true distribution, letting the filter shrink
  the particle count once it's confident.
- **`likelihood_field`** — the laser sensor model; scores each scan
  point against a precomputed likelihood field derived from the map,
  which is computationally cheaper than full ray-casting.
- **`laser_max_range` (3.5 m)** — the maximum laser range used for
  localization updates.

Initializing the robot's pose in RViz2:

1. Set the RViz2 **Fixed Frame** to `map`.
2. Click **2D Pose Estimate**.
3. Click the robot's approximate real location on the map.
4. Drag to set the robot's orientation.
5. Wait for the AMCL particle cloud (`/particle_cloud`) to converge
   around a single tight cluster.

## 13. Nav2 Navigation

Nav2 configuration files live in `robot_navigation/config/`:

```
amcl.yaml
planner_server.yaml
controller_server.yaml
behavior_server.yaml
bt_navigator.yaml
```

Bring everything up with:

```bash
ros2 launch robot_navigation nav2_bringup.launch.py
```

This launches the map server, AMCL, planner server, controller
server, behavior server, and BT navigator, and brings them to the
`active` lifecycle state via the lifecycle manager.

> `[VERIFY FROM EXISTING PROJECT]` — `planner_server.yaml`,
> `controller_server.yaml`, `behavior_server.yaml`, and
> `bt_navigator.yaml` in this repository use standard Nav2 (Jazzy)
> default parameters as a documented starting point, since project-
> specific tuned values were not provided. Only `amcl.yaml` reflects
> exact values confirmed for this project. Re-tune the other four
> against the real warehouse map/environment before treating them as
> final.

## 14. RViz Configuration

Configuration file: `robot_navigation/rviz/navigation.rviz`.
**Fixed Frame:** `map`.

Displays:

| # | Display | Topic |
|---|---------|-------|
| 1 | Grid | — |
| 2 | Map | `/map` |
| 3 | RobotModel | `/robot_description` |
| 4 | TF | — |
| 5 | LaserScan | `/scan` |
| 6 | Global Costmap | `/global_costmap/costmap` |
| 7 | Local Costmap | `/local_costmap/costmap` |
| 8 | Global Plan | `/plan` |
| 9 | Local Plan | `/local_plan` |
| 10 | ParticleCloud | `/particle_cloud` |
| 11 | Waypoints | `/waypoint_markers` |

Tools enabled: **2D Pose Estimate**, **2D Goal Pose**, **Publish
Point**.

Waypoint visualization uses `rviz_default_plugins/MarkerArray` on
`/waypoint_markers` with Fixed Frame `map`.

## 15. Waypoint System

Waypoint coordinates are stored separately from mission logic, in
`warehouse_waypoints/warehouse_waypoints/config/waypoints.py` — the
mission node never hard-codes coordinates.

Module responsibilities:

| Module | Responsibility |
|--------|-----------------|
| `config/waypoints.py` | Waypoint definitions and mission order. |
| `markers/waypoint_marker_publisher.py` | Publishes the `MarkerArray` visualization. |
| `navigation/mission_planner.py` | Mission sequencing and goal-pose construction. |
| `nodes/waypoint_mission_node.py` | ROS 2 node: talks to Nav2, drives the mission. |
| `utils/geometry.py` | Yaw ↔ quaternion conversion. |

Marker color convention on `/waypoint_markers`:

- **BLUE** — inactive waypoint
- **GREEN** — the waypoint currently being navigated to

## 16. Waypoint Coordinates

| Waypoint | x | y | z |
|----------|---|---|---|
| Home     | 0.0 | 0.0 | 0.0 |
| Loading  | 7.782053842839245 | 7.420772652392393 | 0.0 |
| Storage  | 20.000934662165207 | -2.415622611057596 | 0.0 |
| Shipping | -5.930928476565102 | -5.406362903539103 | 0.0 |

All orientations use `qz = sin(yaw / 2)`, `qw = cos(yaw / 2)`, with
`qx = qy = 0` (planar navigation only).

## 17. Waypoint Orientations

| Waypoint | Starting yaw (rad) |
|----------|---------------------|
| Home     | 0.0 |
| Loading  | 0.0 |
| Storage  | -1.5708 |
| Shipping | 3.1416 |

**These yaw values are provisional.** They have not been verified
against the actual warehouse map layout and should not be described
as confirmed physical orientations until checked in RViz against the
saved map.

## 18. Mission Sequence

```
Home (start) → Loading → wait 30s → Storage → Shipping → Home
```

`Home` is only the start pose and the final return goal — it is not
sent as the first navigation target.

## 19. Running the Complete System

Full localization/navigation conceptual workflow:

1. Start Gazebo.
2. Start Robot State Publisher / robot TF.
3. Start AMCL.
4. Start Nav2.
5. Start RViz2.
6. Set RViz Fixed Frame to `map`.
7. Verify the saved map loaded correctly.
8. Use **2D Pose Estimate** to set the robot's initial pose.
9. Wait for the AMCL particle cloud to converge.
10. Verify TF: `map → odom → base_footprint`.
11. Verify `/scan` data is flowing.
12. Verify global/local costmaps are populated.
13. Verify Nav2's lifecycle nodes are active.
14. Start the waypoint mission.

Multi-terminal launch sequence (source both underlays in every
terminal first):

```bash
source /opt/ros/jazzy/setup.bash
source ~/workspaces/nav_ws/install/setup.bash
```

| Terminal | Command |
|----------|---------|
| 1 | `ros2 launch <warehouse_simulation_package> warehouse_storage_launch.launch.py` — Gazebo + TurtleBot3 `[VERIFY FROM EXISTING PROJECT]` |
| 2 | Robot State Publisher / robot TF (often started by Terminal 1's launch file — verify) |
| 3 | `ros2 launch robot_navigation nav2_bringup.launch.py` — AMCL + Nav2 |
| 4 | `rviz2 -d $(ros2 pkg prefix robot_navigation)/share/robot_navigation/rviz/navigation.rviz` |
| 5 | `ros2 run warehouse_waypoints waypoint_mission` |

> Note: `nav2_bringup.launch.py` in this repository brings up AMCL
> and the core Nav2 servers together (Section 13), so Terminals 3 and
> 4 from the original outline are combined here into one launch.

## 20. Terminal Output

Example mission output:

```
==================================================
WAREHOUSE AUTONOMOUS MISSION
==================================================

Mission: Home -> Loading -> Storage -> Shipping -> Home

[INFO] Waiting for Nav2 'navigate_to_pose' action server...
[INFO] Nav2 action server available. Starting mission.
[INFO] Navigating to Loading...
[INFO] Loading reached.
[INFO] Waiting 30 seconds...
[INFO] Navigating to Storage...
[INFO] Storage reached.
[INFO] Navigating to Shipping...
[INFO] Shipping reached.
[INFO] Navigating to Home...
[INFO] Home reached.
==================================================
MISSION COMPLETE
==================================================
```

## 21. Verification and Debugging

```bash
ros2 topic list
ros2 topic echo /map
ros2 topic echo /scan
ros2 topic echo /particle_cloud
ros2 topic echo /waypoint_markers
ros2 topic echo /cmd_vel

ros2 node list
ros2 action list
ros2 topic info /waypoint_markers
```

TF checks:

```bash
ros2 run tf2_ros tf2_echo map base_footprint
ros2 run tf2_tools view_frames
```

## 22. Problems Encountered and Solutions

**Problem 1 — accidental root-level package files.**
`CMakeLists.txt` and `package.xml` were accidentally placed at the
workspace root, causing colcon/CMake to treat the root as a package
and fail with errors referencing a missing `/root/workspaces/nav_ws/launch`
directory.
*Solution:* remove the stray root-level files, keep package files only
inside the actual packages, then rebuild clean:
```bash
rm -rf build install log
colcon build --symlink-install
```

**Problem 2 — package rename confusion.**
Confusion arose between `slam_toolbox` and a renamed
`my_slam_toolbox`. ROS 2 package names and their installed executable
names must stay consistent, or `ros2 run`/`ros2 launch` will fail to
find the expected package.

**Problem 3 — map files accidentally deleted in VS Code.**
Recovery options, in order of ease:
1. `Ctrl+Z` in the editor.
2. VS Code's Timeline / local history panel, if available.
3. `git` history, if the map was already committed.
4. As a last resort, regenerate the map from scratch with SLAM
   Toolbox (Section 10).

**Problem 4 — incorrect map copy path.**
Copy commands failed with `cp: cannot stat ...` because the source
path did not actually exist. Always verify the source file exists
(`ls <path>`) before copying map files into `robot_navigation/maps/`.

**Problem 5 — RViz waypoint markers not appearing.**
Troubleshooting steps:
```bash
ros2 topic list | grep waypoint
ros2 topic echo /waypoint_markers
```
- Confirm `waypoint_mission` node is actually running.
- Confirm RViz has a `rviz_default_plugins/MarkerArray` display
  subscribed to `/waypoint_markers`.
- Confirm RViz's Fixed Frame is `map`.

## 23. Screenshots

> Screenshots have not yet been captured for this write-up. Placeholders are referenced below — replace `images/*.png` with real captures from your own run before publishing.

### SLAM Toolbox building the warehouse map
<img width="567" height="421" alt="map" src="https://github.com/user-attachments/assets/8f698a3c-0797-41e5-b62c-355d8bbf3e5e" />

### AMCL particle cloud converged
<img width="562" height="418" alt="amcl" src="https://github.com/user-attachments/assets/741f6998-17a2-4e16-aaf3-fe4de5c3363c" />

### Nav2 driving the robot toward a goal
<img width="570" height="421" alt="nav_2" src="https://github.com/user-attachments/assets/362284a7-0926-400d-8085-f3ac9b920721" />

### Blue/green waypoint markers in RViz
<img width="561" height="421" alt="Mission_4" src="https://github.com/user-attachments/assets/f39d01f4-d787-4a4e-8b5f-67200cf6f21f" />
<img width="563" height="425" alt="Mission_3" src="https://github.com/user-attachments/assets/be6c5e47-9b30-4b85-a923-10ec07787336" />
<img width="561" height="421" alt="Mission_2" src="https://github.com/user-attachments/assets/bc7f6ecd-824c-4911-925b-261779929169" />
<img width="547" height="378" alt="Mission_1" src="https://github.com/user-attachments/assets/c1dd61e6-5587-438c-92a6-77921291e62f" />
 

## 24. Demonstration Video

(https://drive.google.com/file/d/16PXEJtR36JUpgdENpoLA09O_U8T13w_F/view?usp=sharing)

The video should walk through: the Gazebo warehouse, robot startup,
localization, RViz, Nav2, waypoint markers, arrival at Loading, the
30-second wait, Storage, Shipping, the return to Home, and mission
completion.

## 25. Future Improvements

- Tune `planner_server.yaml`, `controller_server.yaml`,
  `behavior_server.yaml`, and `bt_navigator.yaml` against the actual
  warehouse map instead of the Nav2 stock defaults currently in this
  repository.
- Confirm and record the exact Gazebo warehouse launch file name and
  package.
- Verify the waypoint yaw values (Section 17) against the real
  warehouse layout.
- Add automated tests for `mission_planner.py` and
  `waypoint_marker_publisher.py`.
- Capture the real screenshots and demonstration video referenced in
  Sections 23–24.

---

## Assumptions / Items Not Verified

The following were not provided in the source material and are marked
`[VERIFY FROM EXISTING PROJECT]` throughout this repository rather than
invented:

- The exact package/launch-file name that brings up the Gazebo
  warehouse world and TurtleBot3 (a name of
  `warehouse_storage_launch.launch.py` is used as a placeholder per
  the given instructions, but the containing package is unknown).
- Whether Robot State Publisher is started by that same launch file or
  separately.
- The real `resolution`/`origin`/threshold values for
  `warehouse_map.yaml`, and the actual `warehouse_map.pgm` image.
- Tuned parameter values for `planner_server.yaml`,
  `controller_server.yaml`, `behavior_server.yaml`, and
  `bt_navigator.yaml` (standard Nav2 Jazzy defaults are used instead).
- Whether the physical/simulated warehouse confirms the provisional
  waypoint yaw values in Section 17.
- Real screenshots and a demonstration video link.
