import IP2Location
import geoip2.database
from pathlib import Path
from geoip2.errors import AddressNotFoundError
from datetime import datetime, timezone as d_timezone, timedelta
import pytz
import re

BASE_DIR = Path(__file__).resolve().parent

COUNTRY_DB = BASE_DIR / "GeoLite2-Country.mmdb"
CITY_DB = BASE_DIR / "GeoLite2-City.mmdb"
ASN_DB = BASE_DIR / "GeoLite2-ASN.mmdb"
IP2LOCATION_DB = BASE_DIR / "IP2Location-Lite-DB11.BIN"  # Must be BIN format

# Load IP2Location DB once
ip2_db = IP2Location.IP2Location(str(IP2LOCATION_DB))

from typing import Optional

class GeoResult:
    def __init__(
        self,
        ip: str,
        country_short: Optional[str] = None,
        country_long: Optional[str] = None,
        region: Optional[str] = None,
        city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        timezone: Optional[str] = None,
        asn: Optional[int] = None,
        asn_org: Optional[str] = None,
    ):
        self.ip = ip
        self.country_short = country_short
        self.country_long = country_long
        self.region = region
        self.city = city
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.asn = asn
        self.asn_org = asn_org

    def dict(self) -> dict:
        """Return as dictionary (for API response)"""
        return {
            "ip": self.ip,
            "country_short": self.country_short,
            "country_long": self.country_long,
            "region": self.region,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "asn": self.asn,
            "asn_org": self.asn_org,
        }

    def __repr__(self):
        return f"<GeoResult {self.ip} {self.country_long}, {self.city}>"


def parse_timezone(tz_identifier: str) -> str:
    if not tz_identifier:
        return None

    if tz_identifier in pytz.all_timezones:
        tz = pytz.timezone(tz_identifier)
        now = datetime.now(tz)
        offset_seconds = now.utcoffset().total_seconds()
        hours = int(offset_seconds // 3600)
        minutes = int((offset_seconds % 3600) // 60)
        sign = "+" if hours >= 0 else "-"
        return f"{tz_identifier} ({sign}{abs(hours):02d}:{abs(minutes):02d})"

    # UTC offset case like +06:00 or -04:30
    match = re.match(r"^([+-])(\d{1,2}):(\d{2})$", tz_identifier)
    if match:
        sign, h, m = match.groups()
        hours = int(h)
        minutes = int(m)
        return f"UTC{sign}{hours:02d}:{minutes:02d}"

    return tz_identifier


class GeoIPReader:
    _country_reader = None
    _city_reader = None
    _asn_reader = None

    @classmethod
    def country(cls):
        if cls._country_reader is None:
            cls._country_reader = geoip2.database.Reader(COUNTRY_DB)
        return cls._country_reader

    @classmethod
    def city(cls):
        if cls._city_reader is None:
            cls._city_reader = geoip2.database.Reader(CITY_DB)
        return cls._city_reader

    @classmethod
    def asn(cls):
        if cls._asn_reader is None:
            cls._asn_reader = geoip2.database.Reader(ASN_DB)
        return cls._asn_reader


def geo(ip: str) -> GeoResult:
    """Merge IP2Location and GeoLite2 data and return a GeoResult object with debug prints"""
    # --- IP2Location base data ---
    try:
        ip2 = ip2_db.get_all(ip)
        # print(f"[DEBUG] IP2Location data for {ip}: {ip2.__dict__}")
        result = GeoResult(
            ip=ip,
            country_short=ip2.country_short,
            country_long=ip2.country_long,
            region=ip2.region,
            city=ip2.city,
            latitude=float(ip2.latitude) if ip2.latitude else None,
            longitude=float(ip2.longitude) if ip2.longitude else None,
            timezone=parse_timezone(ip2.timezone),
        )
    except Exception as e:
        # print(f"[ERROR] Failed to get IP2Location data for {ip}: {e}")
        result = GeoResult(ip=ip)

    # --- Merge GeoLite2 data ---
    try:
        country = GeoIPReader.country().country(ip)
        city = GeoIPReader.city().city(ip)
        asn = GeoIPReader.asn().asn(ip)

        # print(f"[DEBUG] GeoLite2 Country: {country.country.iso_code}, {country.country.name}")
        # print(f"[DEBUG] GeoLite2 City: {city.city.name if city.city else None}")
        # print(f"[DEBUG] GeoLite2 Region: {city.subdivisions.most_specific.name if city.subdivisions else None}")
        # print(f"[DEBUG] GeoLite2 Location: lat={city.location.latitude if city.location else None}, "
        #       f"lon={city.location.longitude if city.location else None}, tz={city.location.time_zone if city.location else None}")
        # print(f"[DEBUG] GeoLite2 ASN: {asn.autonomous_system_number}, {asn.autonomous_system_organization}")

        # Country
        result.country_short = country.country.iso_code or result.country_short
        result.country_long = country.country.name or result.country_long

        # Region
        if city.subdivisions and city.subdivisions.most_specific.name:
            result.region = city.subdivisions.most_specific.name

        # City
        if city.city and city.city.name:
            result.city = city.city.name

        # Latitude / Longitude
        if city.location and city.location.latitude is not None:
            result.latitude = city.location.latitude
        if city.location and city.location.longitude is not None:
            result.longitude = city.location.longitude

        # Timezone
        if city.location and city.location.time_zone:
            result.timezone = parse_timezone(city.location.time_zone)

        # ASN
        result.asn = asn.autonomous_system_number or result.asn
        result.asn_org = asn.autonomous_system_organization or result.asn_org

        # print(f"[DEBUG] Merged Result: {result.dict()}")

    except AddressNotFoundError:
        # print(f"[WARNING] GeoLite2 data not found for IP {ip}")
        pass
    return result
