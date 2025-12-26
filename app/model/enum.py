from enum import Enum
from sqlalchemy import Enum as SQLEnum


class DeviceType(str, Enum):
    MOBILE = "MOBILE"
    TABLET = "TABLET"
    DESKTOP = "DESKTOP"
    BOT = "BOT"
    UNKNOWN = "UNKNOWN"


DeviceTypeEnum = SQLEnum(DeviceType, create_type=False, native_enum=False)


class IPLogStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


IPLogStatusEnum = SQLEnum(IPLogStatus, create_type=False, native_enum=False)
