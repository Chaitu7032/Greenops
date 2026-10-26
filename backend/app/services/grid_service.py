import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional
import httpx
import redis
import structlog

from app.core.config import settings
from app.models.carbon_reading import CarbonReading

logger = structlog.get_logger()

# Regional fallbacks based on realistic national grid carbon averages (gCO2eq/kWh)
# Used ONLY when external Electricity Maps API is unreachable and Redis cache is cold
REGIONAL_BASELINE_INTENSITY: Dict[str, Decimal] = {
    "US-EAST": Decimal("380.00"),
    "US-WEST": Decimal("240.00"),
    "EU-WEST": Decimal("210.00"),
    "EU-NORTH": Decimal("45.00"),   # Nordic hydro/wind
    "AP-SOUTH": Decimal("650.00"),  # Coal heavy
    "AP-SOUTHEAST": Decimal("420.00"),
    "DEFAULT": Decimal("350.00"),
}

# Mapping cloud runner region names to Electricity Maps zone codes
ELECTRICITY_MAPS_ZONE_MAPPING: Dict[str, str] = {
    "US-EAST": "US-MIDA-PJM",
    "US-WEST": "US-CAL-CISO",
    "EU-WEST": "DE",
    "EU-NORTH": "SE",
    "AP-SOUTH": "IN-NO",
    "AP-SOUTHEAST": "SG",
}


class GridReadingResult:
    def __init__(
        self,
        region: str,
        intensity_gco2_kwh: Decimal,
        timestamp: datetime,
        source: str = "electricity_maps",
        forecast: bool = False,
        stale: bool = False,
        note: Optional[str] = None,
    ):
        self.region = region
        self.intensity_gco2_kwh = intensity_gco2_kwh
        self.timestamp = timestamp
        self.source = source
        self.forecast = forecast
        self.stale = stale
        self.note = note

    def to_dict(self) -> Dict:
        return {
            "region": self.region,
            "intensity_gco2_kwh": float(self.intensity_gco2_kwh),
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "forecast": self.forecast,
            "stale": self.stale,
            "note": self.note,
        }


def _get_redis_client() -> Optional[redis.Redis]:
    try:
        r = redis.from_url(settings.REDIS_URL, socket_timeout=1.0)
        r.ping()
        return r
    except Exception:
        return None


def get_grid_intensity(region: str = "US-EAST") -> GridReadingResult:
    """
    Retrieve grid carbon intensity for runner region.
    Order of precedence:
    1. Fresh Redis cache (TTL 60 mins)
    2. Live Electricity Maps API call (if key is configured)
    3. Stale Redis cache
    4. Documented regional baseline with stale=True flag
    """
    cache_key = f"greenops:grid_intensity:{region}"
    stale_key = f"greenops:grid_intensity_stale:{region}"
    r = _get_redis_client()

    # 1. Check fresh cache
    if r:
        try:
            cached = r.get(cache_key)
            if cached:
                data = json.loads(cached)
                return GridReadingResult(
                    region=region,
                    intensity_gco2_kwh=Decimal(str(data["intensity"])),
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    source="redis_cache",
                    forecast=False,
                    stale=False,
                )
        except Exception as e:
            logger.warning("Redis cache read error", error=str(e))

    # 2. Query Electricity Maps API
    if settings.ELECTRICITY_MAPS_API_KEY and settings.ELECTRICITY_MAPS_API_KEY != "mock_electricity_maps_key":
        try:
            query_zone = ELECTRICITY_MAPS_ZONE_MAPPING.get(region.upper(), region)
            url = f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={query_zone}"
            headers = {"auth-token": settings.ELECTRICITY_MAPS_API_KEY}
            with httpx.Client(timeout=4.0) as client:
                res = client.get(url, headers=headers)
                if res.status_code == 200:
                    payload = res.json()
                    val = Decimal(str(payload.get("carbonIntensity", 350.0)))
                    now = datetime.now(timezone.utc)
                    cache_data = json.dumps({"intensity": str(val), "timestamp": now.isoformat()})
                    if r:
                        r.setex(cache_key, settings.GRID_CACHE_TTL_MINUTES * 60, cache_data)
                        r.set(stale_key, cache_data)  # Permanent stale backup
                    return GridReadingResult(
                        region=region,
                        intensity_gco2_kwh=val,
                        timestamp=now,
                        source="electricity_maps_api",
                        stale=False,
                    )
                else:
                    logger.warning("Electricity Maps API non-200 response", status=res.status_code, body=res.text)
        except Exception as api_err:
            logger.warning("Electricity Maps API failed or timed out", error=str(api_err))

    # 3. Check Stale Cache
    if r:
        try:
            stale_cached = r.get(stale_key)
            if stale_cached:
                data = json.loads(stale_cached)
                return GridReadingResult(
                    region=region,
                    intensity_gco2_kwh=Decimal(str(data["intensity"])),
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    source="stale_redis_cache",
                    forecast=False,
                    stale=True,
                    note="Using expired cached reading due to API unavailability",
                )
        except Exception:
            pass

    # 4. Regional baseline fallback
    baseline = REGIONAL_BASELINE_INTENSITY.get(region.upper(), REGIONAL_BASELINE_INTENSITY["DEFAULT"])
    return GridReadingResult(
        region=region,
        intensity_gco2_kwh=baseline,
        timestamp=datetime.now(timezone.utc),
        source="regional_baseline_fallback",
        forecast=False,
        stale=True,
        note="Using regional baseline fallback data",
    )
