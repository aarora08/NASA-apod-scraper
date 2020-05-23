import asyncio
import re
from dataclasses import InitVar, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Dict

import aiofiles
from aiohttp import ClientSession, client_exceptions, web
from bs4 import BeautifulSoup
from faker import Faker


@dataclass
class Common:
    relative_url: InitVar[str]
    name: str = field(init=False)
    publish_date: date = field(init=False)
    built_url: str = field(init=False)

    @staticmethod
    def parse_date_name(raw_str: str) -> Dict:
        pattern = re.compile(
            r"(?P<date>[\d]{4}\s[\S]*[\s][\d]{1,2})[\s]?-[\s]*(?P<name>[\s\S]*)[\s]?(?P<extra>\n)"
        )
        match = pattern.search(raw_str)
        return match.groupdict()

    @staticmethod
    def get_agent():
        fake = Faker()
        Faker.seed(0)
        return fake.chrome()


@dataclass
class Parser(Common):
    name: str = field(init=False)
    image_url: str = field(init=False)
    html: BeautifulSoup = field(init=False)
    base_url: str = "https://apod.nasa.gov/apod"

    def __post_init__(self, relative_url):
        self.built_url = f"{self.base_url}/{relative_url}"

    async def fetch(self) -> None:
        headers = {"User-Agent": self.get_agent()}
        async with ClientSession(headers=headers) as session:
            async with session.get(self.built_url) as response:
                response.raise_for_status()
                data = await response.read()
                try:
                    self.html = BeautifulSoup(data, "html5lib")
                except UnicodeDecodeError:
                    print("html decoding error")
                    raise UnicodeDecodeError

    def pull_image(self):
        image = self.html.findAll("img")
        if not image:
            raise AttributeError
        image = image[0]
        self.image_url = image.get("src") or None
        matched_result: Dict = self.parse_date_name(self.html.title.string)
        self.name = matched_result["name"]
        self.publish_date = datetime.strptime(
            matched_result.get("date"), "%Y %B %d"
        ).date()

    def asdict(self) -> Dict:
        return dict(
            name=self.name, publish_date=self.publish_date, relative_url=self.image_url
        )

    async def run(self):
        try:
            await self.fetch()
            self.pull_image()
            return True
        except web.HTTPClientError:
            print("url not found")
            return False
        except client_exceptions.ClientConnectorError:
            print("connection denied")
            return False
        except AttributeError:
            print("image not found")
            raise AttributeError
        except UnicodeDecodeError:
            print("why you no work?")
            return False
        except client_exceptions.ClientOSError:
            print("connection denied")
            return False
        except asyncio.TimeoutError:
            print("connection timeout")
            return False


@dataclass
class Image(Common):
    name: str
    data_dir: InitVar[str]
    file_name: str = field(init=False)
    publish_date: date
    storage_location: Path = field(init=False)
    base_url: str = "https://apod.nasa.gov/apod"

    def __post_init__(self, relative_url: str, data_dir: str):
        self.built_url = f"{self.base_url}/{relative_url}"
        self.storage_location = Path(
            f'{data_dir}/{self.publish_date.year}/{self.publish_date.strftime("%B")}'
        )
        self.storage_location.mkdir(parents=True, exist_ok=True)
        file_ext = relative_url.split(".")[-1]
        self.file_name = f'{self.name.replace(" ", "_").replace("/","_")}.{file_ext}'

    async def save(self):
        headers = {"User-Agent": self.get_agent()}
        async with ClientSession(headers=headers) as session:
            async with session.get(self.built_url) as response:
                response.raise_for_status()
                data = await response.read()
            async with aiofiles.open(
                self.storage_location / self.file_name, mode="wb"
            ) as f:
                await f.write(data)
                print(f"saved file for {self.storage_location / self.file_name}")

    async def run(self):
        try:
            await self.save()
            return True
        except web.HTTPClientError:
            print("url not found")
            return False
        except client_exceptions.ClientConnectorError:
            print("connection denied")
            return False
        except client_exceptions.ClientResponseError:
            print("file not found")
            raise AttributeError
        except client_exceptions.ClientOSError:
            print("connection denied")
            return False
        except asyncio.TimeoutError:
            print("connection timeout")
            return False
