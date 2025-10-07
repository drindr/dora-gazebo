from sqlite3.dbapi2 import Time
from this import s
import dora
from gz.msgs10.stringmsg_pb2 import StringMsg
import gz.transport13
import time
from google.protobuf.json_format import MessageToJson, Parse
import pyarrow

import pkgutil
import importlib
from typing import TypeVar
import threading

MsgType = TypeVar("MsgType")
dora_mutex = threading.Lock()

found_types = {}


def find_proto_message_class(target_type, pkg_name="gz.msgs10"):
    if found_types.get(target_type):
        return found_types[target_type]

    target_class = target_type.removeprefix("gz.msgs.")
    # Iterate over all modules in the gz.msgs10 package
    package = importlib.import_module(pkg_name)
    for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        # Only look at modules that might be proto message definitions
        if not is_pkg and ("pb2" in module_name or "proto" in module_name):
            full_module_name = f"{pkg_name}.{module_name}"
            try:
                mod = importlib.import_module(full_module_name)
                if hasattr(mod, target_class):
                    cls = getattr(mod, target_class)
                    found_types[target_type] = cls
                    return cls
            except Exception as e:
                # Ignore import errors for modules that can't be loaded
                return None
    return None


def register_topic(dora_node: dora.Node, gz_node: gz.transport13.Node, topic: str):
    (pubs, _subs) = gz_node.topic_info(topic)
    if len(pubs) == 0:
        print(f"Topic {topic} has no publishers")
        return
    registered_type = []
    for pub in pubs:
        type_name = pub.msg_type_name
        # For each topic, register each type once is enough
        if type_name in registered_type:
            continue
        registered_type.append(type_name)
        msg_type = find_proto_message_class(type_name)
        if msg_type is None:
            print(f"Failed to handle message with type: {type_name}")
            continue

        def gz_callback(proto_msg, msg_info):
            msg = msg_type()
            msg.ParseFromString(proto_msg)
            json_str = MessageToJson(msg)
            with dora_mutex:
                dora_node.send_output(topic, pyarrow.array([json_str]))
            # print(f"received msg: [{json_str}], {msg_info}\n")

        if gz_node.subscribe_raw(
            topic,
            gz_callback,
            type_name,
            gz.transport13.SubscribeOptions(),
        ):
            print(f"subscribed {pub.msg_type_name} from {topic}")


def main():
    dora_node = dora.Node()
    node_config = dora_node.node_config()

    gz_node = gz.transport13.Node()
    for topic in node_config["outputs"]:
        register_topic(dora_node, gz_node, topic)

    advertised_topics = {}

    while True:
        with dora_mutex:
            event = dora_node.__next__()
        if event is None:
            break
        if event["type"] == "INPUT":
            if event["id"] == "tick":
                continue

            topic = event["id"]
            if event["metadata"].get("msg_type") is None or not event["metadata"][
                "msg_type"
            ].startswith("gz.msgs"):
                print(
                    f"Failed to handle message with topic: {topic}. Unknown message type"
                )
                continue
            msg_type = find_proto_message_class(event["metadata"]["msg_type"])
            if msg_type is None:
                print(
                    f"Failed to handle message with topic: {topic}. Cannot find message type"
                )
                continue

            msg = msg_type()
            print(event["value"].to_pylist()[0])
            Parse(event["value"].to_pylist()[0], msg)
            if topic not in advertised_topics:
                advertised_topics[topic] = gz_node.advertise(topic, msg_type)

            advertised_topics[topic].publish(msg)
            time.sleep(0.1)
