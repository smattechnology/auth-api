Device & IP Geolocation API

A FastAPI-based server that provides:

Accurate device identification from HTTP requests (browser, OS, type, client hints).

Detailed IP geolocation using both IP2Location and GeoLite2 databases.

Automatic logging of devices and IPs in a PostgreSQL database.

Merged geolocation results with timezone formatting and ASN info.

Features

Detects desktop, mobile, and tablet devices with OS and browser versions.

Retrieves client IP and identifies real IP vs forwarded IP.

Provides rich geolocation info:

Field	Description
country_short	Country code (e.g., BD)
country_long	Full country name
region	State or subdivision
city	City name
latitude	Latitude
longitude	Longitude
timezone	Formatted as Asia/Dhaka (+06:00)
asn	Autonomous System Number
asn_org	Autonomous System Organization

Supports IP2Location Lite DB and MaxMind GeoLite2 databases for best accuracy.

Stores IP logs and device information in the database automatically.

Tech Stack

Python 3.11+

FastAPI for API framework

SQLAlchemy for database ORM

PostgreSQL as the database

IP2Location-Lite BIN for geolocation

GeoLite2 MMDBs (Country, City, ASN) for enriched location and ASN data

Pytz for timezone parsing

Uvicorn as ASGI server

Installation
git clone https://github.com/your-username/device-ip-api.git
cd device-ip-api
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt

Setup

Download IP2Location Lite BIN:

Place IP2Location-Lite-DB11.BIN in app/geo/

Download MaxMind GeoLite2 DBs:

GeoLite2-Country.mmdb

GeoLite2-City.mmdb

GeoLite2-ASN.mmdb

Place all .mmdb files in app/geo/

Configure Database:

Update your .env file with PostgreSQL connection string:

DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

Usage

Run the API locally:

uvicorn app.main:app --reload

Sample Request
GET /device-info
Host: localhost:8000
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...

Sample Response
{
  "ip": "223.25.253.142",
  "country_short": "BD",
  "country_long": "Bangladesh",
  "region": "Rangpur",
  "city": "Rangpur",
  "latitude": 23.7018,
  "longitude": 90.3742,
  "timezone": "Asia/Dhaka (+06:00)",
  "asn": 134968,
  "asn_org": "Mizanur Rahman ta Maya Cyber World",
  "device": {
    "type": "DESKTOP",
    "os": "Linux",
    "os_version": "",
    "browser": "Chrome",
    "browser_version": "143.0.0",
    "device_family": "Other",
    "is_touch": false,
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64)...",
    "client_hints": {
      "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
      "sec-ch-ua-platform": "\"Linux\"",
      "sec-ch-ua-mobile": "?0"
    }
  }
}

Database Models

Device: stores client device info.

IPLog: stores IP address, geolocation, ASN, timezone, and device relationship.

Development

Run migrations:

alembic upgrade head


Run tests:

pytest


Enable debug logging in app/geo to verify IP geolocation and device detection.

Contributing

Fork the repo

Create a feature branch

Commit changes with clear messages

Open a Pull Request

License

MIT License – see LICENSE file.
