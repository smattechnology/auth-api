# app/services/device_service.py
import hashlib

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.requests import Request
from user_agents import parse
from typing import Optional, Dict

from app.geo import GeoIPReader, geo
from app.model import Device, IPLog
from app.model.enum import DeviceType, IPLogStatus
from app.schema import DeviceInfo
from app.utils import current_millis
from geoip2.errors import AddressNotFoundError



class DeviceService:
    """
    Service to parse device info from a request, store it in DB,
    and return a structured DeviceInfo object.
    """

    def __init__(self, db: Session):
        self.db = db

    def generate_identifier(self, device_info: DeviceInfo) -> str:
        """
        Generate a unique identifier for a device to prevent duplicates.
        Combines user-agent, OS, browser, device family, IP.
        """
        raw_string = (
            f"{device_info.user_agent}|"
            f"{device_info.os}|"
            f"{device_info.os_version}|"
            f"{device_info.browser}|"
            f"{device_info.browser_version}|"
            f"{device_info.device_family}|"
            f"{device_info.is_touch}|"
        )
        return hashlib.sha256(raw_string.encode("utf-8")).hexdigest()

    def parse_device(self, request: Request) -> DeviceInfo:
        """
        Parse the request headers to build a DeviceInfo object.
        """
        ua_string = request.headers.get("user-agent", "")

        try:
            ua = parse(ua_string)
        except Exception:
            ua = None

        # Determine device type
        if ua and ua.is_bot:
            device_type = DeviceType.BOT
        elif ua and ua.is_mobile:
            device_type = DeviceType.MOBILE
        elif ua and ua.is_tablet:
            device_type = DeviceType.TABLET
        elif ua and ua.is_pc:
            device_type = DeviceType.DESKTOP
        else:
            device_type = DeviceType.UNKNOWN

        device_info = DeviceInfo(
            type=device_type,
            os=ua.os.family if ua else "Unknown",
            os_version=ua.os.version_string if ua else None,
            browser=ua.browser.family if ua else "Unknown",
            browser_version=ua.browser.version_string if ua else None,
            device_family=ua.device.family if ua else "Unknown",
            is_touch=(ua.is_mobile or ua.is_tablet) if ua else False,
            user_agent=ua_string,
            client_hints={
                "sec-ch-ua": request.headers.get("sec-ch-ua"),
                "sec-ch-ua-platform": request.headers.get("sec-ch-ua-platform"),
                "sec-ch-ua-mobile": request.headers.get("sec-ch-ua-mobile")
            },
        )

        # Apply client hints overrides
        platform = request.headers.get("sec-ch-ua-platform")
        mobile_hint = request.headers.get("sec-ch-ua-mobile")
        if platform:
            device_info.os = platform.strip('"')
        if mobile_hint == "?1":
            device_info.is_touch = True

        return device_info

    def lookup(ip: str) -> Optional[Dict]:
        if not ip:
            return None

        try:
            city = GeoIPReader.city().city(ip)
            asn = GeoIPReader.asn().asn(ip)

            return {
                "country": city.country.iso_code,
                "country_name": city.country.name,
                "city": city.city.name,
                "region": city.subdivisions.most_specific.name,
                "timezone": city.location.time_zone,
                "latitude": city.location.latitude,
                "longitude": city.location.longitude,
                "asn": asn.autonomous_system_number,
                "asn_org": asn.autonomous_system_organization,
            }

        except AddressNotFoundError:
            return None

    def log_device(self, device_info: DeviceInfo) -> Device:
        """
        Persist the device info into the database, preventing duplicates.
        """
        # Generate deterministic hash
        device_hash = self.generate_identifier(device_info)

        # Try to find existing device
        existing = self.db.query(Device).filter_by(hash=device_hash).first()
        if existing:
            return existing  # Already logged

        # Create new device entry
        db_device = Device(
            hash=device_hash,
            type=device_info.type,
            os=device_info.os,
            os_version=device_info.os_version,
            browser=device_info.browser,
            browser_version=device_info.browser_version,
            device_family=device_info.device_family,
            is_touch=device_info.is_touch,
            user_agent=device_info.user_agent,
            client_hints=device_info.client_hints,
            created_at=current_millis(),
            updated_at=current_millis(),
        )

        self.db.add(db_device)
        try:
            self.db.commit()
            self.db.refresh(db_device)
        except IntegrityError:
            # Duplicate detected due to race condition
            self.db.rollback()
            db_device = self.db.query(Device).filter_by(hash=device_hash).first()

        return db_device

    def parse_and_log(self, request: Request) -> DeviceInfo:
        """
        Full workflow: parse device from request and persist in DB.
        Returns the DeviceInfo object.
        """
        device_info = self.parse_device(request)
        device = self.log_device(device_info)
        self.log_ip_for_device(device,request)
        return device_info

    def log_ip_for_device(self, device: Device, request: Request) -> IPLog:
        """
        Auto-deactivate old IPs when a new one appears.
        If the active IP is unchanged, do nothing.
        Also stores geolocation info from IP2Location + GeoLite2.
        """

        ip_address = request.client.host if request.client else None
        forwarded_for = request.headers.get("x-forwarded-for")
        real_ip = request.headers.get("x-real-ip")
        accept = request.headers.get("accept")
        origin = request.headers.get("origin")

        if not ip_address:
            return None

        # --- Check for existing active IP ---
        active_ip: IPLog | None = (
            self.db.query(IPLog)
            .filter(
                IPLog.device_id == device.id,
                IPLog.status == IPLogStatus.ACTIVE
            )
            .one_or_none()
        )

        if active_ip and active_ip.ip_address == ip_address:
            return active_ip

        # --- Deactivate old active IPs ---
        (
            self.db.query(IPLog)
            .filter(
                IPLog.device_id == device.id,
                IPLog.status == IPLogStatus.ACTIVE
            )
            .update(
                {
                    IPLog.status: IPLogStatus.INACTIVE,
                    IPLog.updated_at: current_millis(),
                },
                synchronize_session=False,
            )
        )

        # --- Get geolocation data ---
        geo_data = geo(ip_address)

        # --- Create new IPLog with geo fields ---
        new_ip = IPLog(
            device_id=device.id,
            ip_address=ip_address,
            forwarded_for=forwarded_for,
            real_ip=real_ip,
            accept=accept,
            origin=origin,
            status=IPLogStatus.ACTIVE,
            created_at=current_millis(),
            updated_at=current_millis(),

            # Geo fields
            country_short=geo_data.country_short,
            country_long=geo_data.country_long,
            region=geo_data.region,
            city=geo_data.city,
            latitude=geo_data.latitude,
            longitude=geo_data.longitude,
            timezone=geo_data.timezone,
            asn=geo_data.asn,
            asn_org=geo_data.asn_org,
        )

        self.db.add(new_ip)
        self.db.commit()
        self.db.refresh(new_ip)

        return new_ip
