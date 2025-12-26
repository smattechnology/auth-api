# app/models/device.py
from sqlalchemy import Column, String, Boolean, Enum, Integer, BigInteger, ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
import uuid

from sqlalchemy.orm import relationship

from app.database.base import Base
from app.model.enum import DeviceTypeEnum, IPLogStatus, IPLogStatusEnum
from app.utils import current_millis


class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hash = Column(String(128), nullable=False, unique=True, index=True)

    type = Column(DeviceTypeEnum, nullable=False)
    os = Column(String(50), nullable=True)
    os_version = Column(String(50), nullable=True)
    browser = Column(String(50), nullable=True)
    browser_version = Column(String(50), nullable=True)
    device_family = Column(String(100), nullable=True)
    is_touch = Column(Boolean, default=False)

    user_agent = Column(String(512), nullable=True)
    client_hints = Column(JSONB, nullable=True)

    created_at = Column(BigInteger, nullable=False, default=current_millis)
    updated_at = Column(BigInteger, nullable=False, default=current_millis, onupdate=current_millis)

    # Relationship
    ip_logs = relationship(
        "IPLog",
        back_populates="device",
        passive_deletes=True
    )

    @property
    def active_ip(self) -> IPLog | None:
        return next(
            (ip for ip in self.ip_logs if ip.status == IPLogStatus.ACTIVE),
            None
        )


class IPLog(Base):
    __tablename__ = "ip_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    device_id = Column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="SET NULL"),
        nullable=True
    )

    ip_address = Column(String(45), nullable=False)
    forwarded_for = Column(String(512), nullable=True)
    real_ip = Column(String(45), nullable=True)

    accept = Column(String(512), nullable=True)
    origin = Column(String(512), nullable=True)

    status = Column(
        IPLogStatusEnum,
        nullable=False,
        default=IPLogStatus.ACTIVE
    )

    # --- Geo data fields ---
    country_short = Column(String(10), nullable=True)
    country_long = Column(String(128), nullable=True)
    region = Column(String(128), nullable=True)
    city = Column(String(128), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timezone = Column(String(64), nullable=True)
    asn = Column(Integer, nullable=True)
    asn_org = Column(String(256), nullable=True)

    created_at = Column(BigInteger, nullable=False, default=current_millis)
    updated_at = Column(BigInteger, nullable=False, default=current_millis, onupdate=current_millis)

    device = relationship("Device", back_populates="ip_logs")
