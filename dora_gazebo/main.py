from sqlite3.dbapi2 import Time
from this import s
import dora
from gz.msgs10.stringmsg_pb2 import StringMsg
import gz.transport13
import time
from google.protobuf.json_format import MessageToJson

import pkgutil
import importlib
from typing import TypeVar

MsgType = TypeVar("MsgType")


def find_proto_message_class(target_class, pkg_name="gz.msgs10") -> list[MsgType]:
    found = []
    # Iterate over all modules in the gz.msgs10 package
    package = importlib.import_module(pkg_name)
    for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        # Only look at modules that might be proto message definitions
        if not is_pkg and ("pb2" in module_name or "proto" in module_name):
            full_module_name = f"{pkg_name}.{module_name}"
            try:
                mod = importlib.import_module(full_module_name)
                if hasattr(mod, target_class):
                    found.append(getattr(mod, target_class))
            except Exception as e:
                # Ignore import errors for modules that can't be loaded
                pass
    return found


def register_topic(gz_node: gz.transport13.Node, topic: str):
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
        class_name = type_name.removeprefix("gz.msgs.")
        found = find_proto_message_class(class_name)
        if len(found) == 0:
            print(f"Failed to handle message with type: {type_name}")
            continue
        msg_type = found[0]

        def gz_callback(proto_msg, msg_info):
            msg = msg_type()
            msg.ParseFromString(proto_msg)
            json_str = MessageToJson(msg)
            print(f"received msg: [{json_str}], {msg_info}\n")

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
        register_topic(gz_node, topic)

    for event in dora_node:
        if event["type"] == "INPUT":
            time.sleep(0.01)
