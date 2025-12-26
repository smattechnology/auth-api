from typing import Optional, Dict

from pydantic import BaseModel

from app.model.enum import DeviceType


class DeviceInfo(BaseModel):
    type: DeviceType
    os: str
    os_version: str | None = None
    browser: str
    browser_version: str | None = None
    device_family: str | None = None
    is_touch: bool = False
    user_agent: Optional[str]
    client_hints: Optional[Dict]
