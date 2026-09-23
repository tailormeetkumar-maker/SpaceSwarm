"""Protocol helpers and validation rules."""

from .messages import Message, MessageType


BEE_TO_BEE = {
    MessageType.DISCOVERY,
    MessageType.SCIENCE,
    MessageType.HAZARD,
    MessageType.TELEMETRY,
    MessageType.HEARTBEAT,
    MessageType.RELAY,
    MessageType.ACK,
}

BEE_TO_MOTHER = BEE_TO_BEE | {
    MessageType.REPLACEMENT_REQUEST,
}

MOTHER_TO_BEE = {
    MessageType.COMMAND,
    MessageType.ROLE_UPDATE,
    MessageType.HIVE_STATE,
}

MOTHER_TO_EARTH = {
    MessageType.EARTH_REPORT,
    MessageType.HIVE_STATE,
}


def allowed(sender_kind: str, receiver_kind: str, message_type: MessageType) -> bool:
    if sender_kind == "bee" and receiver_kind == "bee":
        return message_type in BEE_TO_BEE
    if sender_kind == "bee" and receiver_kind == "mother":
        return message_type in BEE_TO_MOTHER
    if sender_kind == "mother" and receiver_kind == "bee":
        return message_type in MOTHER_TO_BEE
    if sender_kind == "mother" and receiver_kind == "earth":
        return message_type in MOTHER_TO_EARTH
    return False


def validate_message(message: Message) -> None:
    if not message.sender_id or not message.receiver_id:
        raise ValueError("Messages require sender and receiver IDs.")
    if message.ttl < 0:
        raise ValueError("Message TTL cannot be negative.")
    if message.hop_count < 0:
        raise ValueError("Message hop count cannot be negative.")
