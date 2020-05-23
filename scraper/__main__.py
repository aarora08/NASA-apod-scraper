import asyncio
import time
from argparse import ArgumentParser, Namespace

from scraper.controller import run, run_failed


def build_parser(description: str = None) -> ArgumentParser:
    parser = ArgumentParser(description)
    # TODO: implement verbose flag
    parser.add_argument("--verbose", action="count", default=0)
    # TODO: implement dry run flag
    parser.add_argument("--dry-run", action="count", default=0)
    common_parser = ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--data-dir",
        default="local/data",
        required=False,
    )
    common_parser.add_argument(
        "--log-dir",
        default="local/logs",
        required=False,
    )
    common_parser.add_argument(
        "--run-version",
        default="v1",
        required=False,
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True
    fetch_parser = subparsers.add_parser("fetch", parents=[common_parser])
    fetch_parser.add_argument('--start-date', default='2020-05-01')
    fetch_parser.add_argument('--end-date', default='2020-05-05')

    fetch_failed_parser = subparsers.add_parser("fetch-failed", parents=[common_parser])
    fetch_failed_parser.add_argument('--logs-from', default='local/logs/v1/')

    return parser


def main():
    parser: ArgumentParser = build_parser()
    args: Namespace = parser.parse_args()
    commands = {'fetch': run, 'fetch-failed': run_failed}
    if args.command == "fetch":
        run_kwargs = dict(start_date=args.start_date, end_date=args.end_date, data_dir=args.data_dir,
                          log_dir=args.log_dir, prefix=args.run_version)
    else:
        run_kwargs = dict(data_dir=args.data_dir, log_dir=args.log_dir, log_from=args.logs_from)

    run_command = commands[args.command]
    start_async = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        run_command(loop, **run_kwargs)
    )

    end_async = time.time() - start_async
    print(f"async runtime: {end_async}")


if __name__ == "__main__":
    main()
