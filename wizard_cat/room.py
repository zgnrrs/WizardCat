import json
import random
import string
import time
from typing import Dict, List

import paho.mqtt.client as mqtt
from PySide6.QtCore import QObject, Signal

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883


class RoomManager(QObject):
    """Manages real-time study room presence, member tracking, and room chat."""

    members_updated = Signal(list)
    chat_received = Signal(str, str, str)  # (username, message, msg_type)
    room_joined = Signal(str)
    room_left = Signal()

    def __init__(self):
        super().__init__()
        self.user_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        self.username = "WizardCat"
        self.room_code = None
        self.members: Dict[str, dict] = {}

        self.client = None
        self._is_connected = False

    def generate_room_code(self) -> str:
        """Generate a random 4-digit room code like CAT-4029."""
        num = "".join(random.choices(string.digits, k=4))
        return f"CAT-{num}"

    def connect_and_join(self, room_code: str, username: str) -> bool:
        """Connect to public MQTT relay and join specified room code."""
        self.leave_room()

        self.room_code = room_code.upper().strip()
        self.username = username.strip() or "WizardCat"
        self.members = {}

        client_id = f"wizcat_{self.user_id}_{random.randint(1000, 9999)}"

        # Compatibility with paho-mqtt v1 and v2
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
        except AttributeError:
            self.client = mqtt.Client(client_id)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        try:
            self.client.connect_async(MQTT_BROKER, MQTT_PORT, keepalive=30)
            self.client.loop_start()
            return True
        except Exception as error:
            print("Room connection error:", error)
            return False

    def leave_room(self):
        """Disconnect from MQTT broker and reset room state."""
        if self.client:
            try:
                if self.room_code:
                    bye_payload = json.dumps({
                        "user_id": self.user_id,
                        "username": self.username,
                        "text": "odadan ayrıldı.",
                        "type": "system",
                    })
                    self.client.publish(f"wizardcat/v1/room/{self.room_code}/chat", bye_payload)
                self.client.loop_stop()
                self.client.disconnect()
            except Exception:
                pass
            self.client = None

        self._is_connected = False
        self.room_code = None
        self.members = {}
        self.room_left.emit()

    def send_chat_message(self, text: str, msg_type: str = "chat"):
        """Broadcast chat message to the room."""
        if not self.client or not self.room_code or not text.strip():
            return

        payload = json.dumps({
            "user_id": self.user_id,
            "username": self.username,
            "text": text.strip(),
            "timestamp": time.time(),
            "type": msg_type,
        })
        self.client.publish(f"wizardcat/v1/room/{self.room_code}/chat", payload)

    def broadcast_presence(self, level: int, title: str, status: str, time_str: str):
        """Broadcast local wizard presence heartbeat to room members."""
        if not self.client or not self.room_code:
            return

        payload = json.dumps({
            "user_id": self.user_id,
            "username": self.username,
            "level": level,
            "title": title,
            "status": status,
            "time_str": time_str,
            "last_seen": time.time(),
        })
        self.client.publish(f"wizardcat/v1/room/{self.room_code}/presence", payload)
        self._purge_stale_members()

    def announce_level_up(self, new_level: int, new_title: str):
        """Broadcast level-up announcement to room chat."""
        if not self.room_code:
            return
        msg = f"✨ LEVEL UP! Seviye {new_level} oldu ve '{new_title}' unvanını kazandı! 🪄"
        self.send_chat_message(msg, msg_type="level_up")

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT on_connect callback handler."""
        if rc == 0 and self.room_code:
            self._is_connected = True
            presence_topic = f"wizardcat/v1/room/{self.room_code}/presence"
            chat_topic = f"wizardcat/v1/room/{self.room_code}/chat"

            self.client.subscribe([(presence_topic, 0), (chat_topic, 0)])
            self.room_joined.emit(self.room_code)

            # Send welcome chat notification
            welcome_payload = json.dumps({
                "user_id": self.user_id,
                "username": self.username,
                "text": "odaya katıldı! 🪄",
                "type": "system",
            })
            self.client.publish(chat_topic, welcome_payload)

    def _on_message(self, client, userdata, msg):
        """MQTT on_message callback handler."""
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            topic = msg.topic

            if topic.endswith("/presence"):
                uid = payload.get("user_id")
                if uid:
                    self.members[uid] = payload
                    self._purge_stale_members()

            elif topic.endswith("/chat"):
                user = payload.get("username", "Büyücü")
                text = payload.get("text", "")
                mtype = payload.get("type", "chat")
                self.chat_received.emit(user, text, mtype)

        except Exception as err:
            print("Room message parse error:", err)

    def _purge_stale_members(self):
        """Purge members whose presence heartbeats are older than 12 seconds."""
        now = time.time()
        stale_uids = [
            uid for uid, mdata in self.members.items()
            if now - mdata.get("last_seen", 0) > 12
        ]
        for uid in stale_uids:
            del self.members[uid]

        member_list = list(self.members.values())
        self.members_updated.emit(member_list)
