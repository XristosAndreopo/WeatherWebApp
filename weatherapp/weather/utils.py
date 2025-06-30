# weather/utils.py

from dataclasses import dataclass
from datetime import datetime
from .constants import ICON_MAP, DEFAULT_ICON

@dataclass
class ForecastCard:
    date: str = ''
    description: str = ''
    temp: int | None = None
    humidity: int | None = None
    icon: str = ''
    error: str = ''

def get_icon_for_description(desc: str) -> str:
    desc = desc.lower()
    for key, icon in ICON_MAP.items():
        if key in desc:
            return icon
    return DEFAULT_ICON

def parse_daily_forecasts(raw_list: list[dict], days: int = 7) -> list[ForecastCard]:
    now = datetime.utcnow()
    by_date: dict[str, ForecastCard] = {}
    last_for_today: ForecastCard | None = None
    today_str = now.strftime('%Y-%m-%d')

    for item in raw_list:
        dt = datetime.fromtimestamp(item['dt'])
        ds = dt.strftime('%Y-%m-%d')
        card = ForecastCard(
            date=dt.strftime('%Y-%m-%d %H:%M'),
            description=item['weather'][0]['description'],
            temp=round(item['main']['temp']),
            humidity=item['main']['humidity'],
            icon=get_icon_for_description(item['weather'][0]['description'])
        )
        # track last for today
        if ds == today_str:
            last_for_today = card
        # first future‑or‑today sample for each date
        if ds not in by_date and (dt >= now or ds != today_str):
            by_date[ds] = card

    result: list[ForecastCard] = []
    # today first
    if today_str in by_date:
        result.append(by_date.pop(today_str))
    elif last_for_today:
        result.append(last_for_today)
    else:
        result.append(ForecastCard(error='No forecast data for today.'))

    # next days up to total `days`
    for ds in sorted(by_date)[: days - 1]:
        result.append(by_date[ds])

    return result
