"""Constants for Reading Bus integration."""

DOMAIN = "reading_bus"
CONF_API_KEY = "api_key"
CONF_STOP_ID = "stop_id"
SCAN_INTERVAL = 60  # seconds
API_URL = "https://reading-opendata.r2p.com/api/v1/siri-sm"
TIMEOUT = 10  # seconds

# XML parsing constants
NAMESPACES = {
    "siri": "http://www.siri.org.uk/siri",
    "sm": "http://www.ifopt.org.uk/ifopt",
}
