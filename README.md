# NASA Astronomy Picture of the Day Scraper

I found out about the APOD website and knew that I want to have these jaw dropping images on my machine for wallpapers. To add a nice spin to it, I decided to use Python asyncIO. 

There's nothing special about this scraper, I just like looking at astronomy pictures, and this is a nice way to get 1000s of wallpapers ready for everyday. 

As always, there are dataclasses in this project. And I tried to implement some sort of retry logic. It saves the failed urls in a separate directory and you with a different command you can retry fetching the failed urls.



## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```bash
asdf local python 3.7.5
python -m venv venv
source venv/bin/activate
pip install -U pip setuptools pipenv
pipenv install
```

Running it:

```bash
cd ~/nasa-apod-scraper/
python -m scraper fetch --data-dir local/data --log-dir local/logs --start-date 2020-05-01 --end-date 2020-05-22
```

```bash
# running failed urls

cd ~/nasa-apod-scraper/
python -m scraper fetch-failed --data-dir local/data --logs-from local/logs/v1 --run-version v2
```


Here are a few that I liked:

<img src="https://github.com/aarora08/nasa-apod-scraper/blob/master/static/A_View_Toward_M106.jpg" width="45%"></img> <img src="https://github.com/aarora08/nasa-apod-scraper/blob/master/static/Moon,_Mars,_Saturn,_Jupiter,_Milky_Way__.jpg" width="45%"></img> <img src="https://github.com/aarora08/nasa-apod-scraper/blob/master/static/The_Dark_River_to_Antares.jpg" width="45%"></img> <img src="https://github.com/aarora08/nasa-apod-scraper/blob/master/static/Galaxy_Wars:_M81_and_M82.jpg" width="45%"></img> 

## Contributing

All suggestions are welcome, use a PR! As the sole maintainer of this tiny project, I'll see what I can review and approve!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for detailsContributing
