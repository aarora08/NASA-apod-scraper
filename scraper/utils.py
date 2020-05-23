import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterator


def date_range(start_date: date, end_date: date) -> Iterator:
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


async def log_failed_results(failed_urls, log_dir):
    failed_urls_json = dict(parser=[], image=[])
    while not failed_urls.empty():
        url_info = await failed_urls.get()
        url_type, url = url_info.popitem()
        failed_urls_json[url_type].append(url)
    log_dir = Path(f"{log_dir}")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_location = log_dir / f"{int(datetime.now().timestamp())}.json"
    with log_location.open("w") as f:
        f.write(json.dumps(failed_urls_json))
