import math
import random
import dora
import pyarrow
import json
import time


def main():
    dora_node = dora.Node()

    random.seed(114514)
    label = ["x", "y", "z"]
    for _ in range(1000):
        linear_velocity = [random.uniform(-2, 2) for _ in range(3)]
        angular_velocity = [random.uniform(-math.pi, math.pi) for _ in range(3)]
        linear = dict(zip(label, linear_velocity))
        angular = dict(zip(label, angular_velocity))
        msg_dict = {"linear": linear, "angular": angular}
        dora_node.send_output(
            "cmd_vel",
            pyarrow.array([json.dumps(msg_dict)]),
            {"msg_type": "gz.msgs.Twist"},
        )
        time.sleep(0.5)
