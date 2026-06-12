from pathlib import Path

from shapely import Point


USER_AGENT = "imatynia/mgr-turist-movement-predition"
WARSAW_POINT = Point(52.232234, 21.008941)
ROOT = Path(__file__).parent.parent.parent
SCRAPER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"