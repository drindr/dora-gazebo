This Node works with Gazebo Harmonic.

## Setup
To use the Python binding of Gazebo, you need to install the package for specific Gazebo version from Gazebo's official repository.
```bash
sudo apt install python3-gz-tansport13
```

If you'd like to use venv of UV, please setup the venv manually to make the system packages available.
```bash
uv venv --system-site-packages
```

## Configuration
This Node will subscribe topic from Gazebo, and publish it in Dora with JSON format according to the outputs' configuration.
```yaml
nodes:
  - id: id-of-the-node
    path: dora-gazebo
    outputs:
      - /stats
      - /gui/camera/pose
      - <topic name>
```
