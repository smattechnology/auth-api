# Device & IP Geolocation API

A production-ready FastAPI service for accurate device identification and enriched IP geolocation. The API combines HTTP User-Agent parsing, Client Hints, IP2Location Lite and MaxMind GeoLite2 databases, and automatic logging to PostgreSQL to provide reliable device and location insights.

---

## Features

- Accurate device detection (desktop, mobile, tablet) including OS and browser names and versions.
- Client Hints support (sec-ch-ua, sec-ch-ua-platform, sec-ch-ua-mobile) for improved detection.
- Robust IP geolocation using both IP2Location-Lite and MaxMind GeoLite2 (Country, City, ASN).
- Merged geolocation results with timezone formatting (e.g. Asia/Dhaka (+06:00)).
- ASN lookup and organization name.
- Automatic persistence of device and IP logs to PostgreSQL.
- Async-ready with FastAPI and Uvicorn for high-performance deployments.


## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy (async)
- PostgreSQL (asyncpg)
- IP2Location-Lite (.BIN)
- MaxMind GeoLite2 (.mmdb)
- pytz
- Uvicorn

---

## Quick Start

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/smattechnology/auth-api.git
cd auth-api
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate     # Windows (PowerShell)

pip install -r requirements.txt
```

### Configuration

1. Download IP2Location Lite BIN:
   - Place `IP2Location-Lite-DB11.BIN` in `app/geo/`

2. Download MaxMind GeoLite2 databases (place in `app/geo/`):
   - `GeoLite2-Country.mmdb`
   - `GeoLite2-City.mmdb`
   - `GeoLite2-ASN.mmdb`

3. Configure the database and environment variables. Example `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
# Optional: additional config keys (LOG_LEVEL, GEO_DB_PATH, ...)
```

### Run locally

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` by default.

---

## API

### GET /device-info

Returns detected device information and enriched geolocation for the incoming request IP.

Sample request headers:

```
GET /device-info HTTP/1.1
Host: localhost:8000
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...
Sec-CH-UA: "Chromium";v="143"
Sec-CH-UA-Platform: "Windows"
```

Sample response:

```json
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
```

---

## Geolocation Output Fields

- `country_short`: Country ISO code (e.g., `BD`)
- `country_long`: Full country name
- `region`: State or subdivision
- `city`: City name
- `latitude`, `longitude`: Coordinates
- `timezone`: Timezone with offset (e.g., `Asia/Dhaka (+06:00)`)
- `asn`: Autonomous System Number
- `asn_org`: Autonomous System Organization


## Database Models

- Device: stores parsed client device details (type, OS, browser, UA, client hints).
- IPLog: stores IP address, resolved geolocation, ASN, timezone, and relationship to Device.

---

## Development

Run migrations:

```bash
alembic upgrade head
```

Run tests:

```bash
pytest
```

Enable debug logging for geolocation/device detection by configuring logging in `app/geo`.

---

## Contributing

Contributions are welcome — please follow the standard workflow:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feat/my-feature`.
3. Commit your changes with meaningful messages.
4. Push to your fork and open a Pull Request with a clear description.

Please add tests and update documentation for any new behavior.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

If you'd like, I can also add badges, API docs examples, or a Dockerfile + docker-compose setup for local development and testing.
