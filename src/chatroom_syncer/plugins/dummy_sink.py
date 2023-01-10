from __future__ import annotations

import hashlib
import math

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient
from wechaty import Message, WechatyPlugin
from wechaty_puppet import MessageType

from ..emoji import emoji_list
from ..utils import format_msg_text, prepare_for_configuration

HASH_BYTES = math.ceil(math.log(len(emoji_list), 2) / 8)


class DummySinkPlugin(WechatyPlugin):
    def __init__(self):
        super().__init__()
        self._config = prepare_for_configuration()

    async def on_message(self, msg: Message) -> None:
        room = msg.room()
        if room:
            topic = await room.topic()
        else:
            topic = msg.to().name
        username = msg.talker().name
        if msg.type() == MessageType.MESSAGE_TYPE_TEXT:
            # again in second plugin
            text = format_msg_text(msg.text())
            print(f">>> {username}->{topic}: {text}")
        elif msg.type() == MessageType.MESSAGE_TYPE_IMAGE:
            # TBD: send image
            image = msg.to_image()
            # BUG: internal error <'remoteUrl'>
            # hd = await image.hd()
            print(f">>> {username}->{topic}: {image.image_id}[image_id]")
        else:
            print(f">>> {username}->{topic}: {msg.type()}[msg_type]")

    @staticmethod
    def get_emoji(username: str) -> str:
        """Get emoji"""
        username_hash = hashlib.sha256(username.encode("utf-8")).digest()
        # Get the first 2 bytes of the sha256 digest, that is max 65535
        # then get the index by mod the length of emoji list
        emoji_index = int.from_bytes(username_hash[:HASH_BYTES], "big")
        return emoji_list[emoji_index % len(emoji_list)]
