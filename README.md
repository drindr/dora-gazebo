# Dora-Gazebo
A Dora node provides bidirectional communication between Gazebo and Dora.
This Node can only work with Gazebo Harmonic now.

[screencast.webm](https://github.com/user-attachments/assets/d4bf0195-f543-45be-baf5-338701c8e307)

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
    inputs:
      tick: dora/timer/millis/2
      /model/tugbot/cmd_vel: dora-gz-ctrl/cmd_vel
      <topic name>: <dora node output>
    outputs:
      - /stats
      - /gui/camera/pose
      - <topic name>
```

## Publish Message to Gazebo
```python
dora_node.send_output(
    "cmd_vel",
    pyarrow.array([json.dumps(msg_dict)]),
    {"msg_type": "gz.msgs.Twist"}, # declare the type of the message
)
```
