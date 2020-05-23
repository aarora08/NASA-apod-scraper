import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Tuple

from scraper.models import Image, Parser
from scraper.utils import date_range, log_failed_results


async def fetch(data_dir: str, relative_url: str, failed_urls: asyncio.Queue):
    parser = Parser(relative_url=relative_url)
    try:
        result = await parser.run()
    except AttributeError:
        return
    if not result:
        await failed_urls.put(dict(parser=relative_url))
        return
    image = Image(data_dir=data_dir, **parser.asdict())
    result = await image.run()
    if not result:
        await failed_urls.put(dict(image=image.built_url))


async def run_failed(loop: asyncio, data_dir: str, log_dir: str, log_from: str, prefix: str = "v2"):
    p = Path(f"{log_from}")
    data_dir = f"{data_dir}/{prefix}"
    log_dir = f"{log_dir}/{prefix}"
    failed_urls = asyncio.Queue()
    tasks = []
    for file in p.glob("*.json"):
        with file.open("r") as f:
            data = json.loads(f.read())
        for relative_url in data["parser"]:
            tasks.append(loop.create_task(fetch(relative_url=relative_url, failed_urls=failed_urls, data_dir=data_dir)))
    initial_status = 0
    for count, task in enumerate(tasks):
        await task
        completed_status = int(count / len(tasks) * 100)
        if completed_status > initial_status:
            initial_status = completed_status
            print(f"{count} tasks completed: {'*' * completed_status} ")
    if failed_urls.qsize():
        await log_failed_results(failed_urls=failed_urls, log_dir=log_dir)


async def run(loop: asyncio, start_date: Tuple, end_date: Tuple, data_dir: str, log_dir: str, prefix: str = "v1"):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    data_dir = f"{data_dir}/{prefix}"
    log_dir = f"{log_dir}/{prefix}"
    tasks = []
    initial_status = 0
    failed_urls = asyncio.Queue()
    for count, single_date in enumerate(date_range(start_date, end_date)):
        parsed_date = single_date.strftime("%y%m%d")
        relative_url = f"ap{parsed_date}.html"
        tasks.append(loop.create_task(fetch(data_dir=data_dir, relative_url=relative_url, failed_urls=failed_urls)))
        started_tasks = int(count / 7340 * 100)
        if started_tasks > initial_status:
            initial_status = started_tasks
            print(f"{count} tasks started: {'*' * started_tasks} ")
    initial_status = 0
    for count, task in enumerate(tasks):
        await task
        completed_status = int(count / len(tasks) * 100)
        if completed_status > initial_status:
            initial_status = completed_status
            print(f"{count} tasks completed: {'*' * completed_status} ")
    if failed_urls.qsize():
        await log_failed_results(failed_urls=failed_urls, log_dir=log_dir)
