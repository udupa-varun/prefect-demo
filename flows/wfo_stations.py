import asyncio
import time
import random

from prefect import task, flow, get_run_logger
from prefect.filesystems import LocalFileSystem, S3
from prefect.serializers import JSONSerializer
from prefect.task_runners import ConcurrentTaskRunner
import requests

from .reusable_tasks import (
    get_api_friendly_address,
    get_geocode_coords,
    get_office_and_gridpoint,
)

from prefect.runtime import flow_run


def flow_run_name():
    return f"{flow_run.parameters['address'][:5]}"


@task
def dummy_task():
    time.sleep(0.5)
    return random.randint(1, 10)


@task(persist_result=True, result_storage_key="results-{parameters[wfo]}.json")
def get_wfo_stations(wfo: str, grid_x: int, grid_y: int) -> list[dict[str]]:
    logger = get_run_logger()

    url = (
        f"https://api.weather.gov/gridpoints/{wfo}/{grid_x},{grid_y}/stations?limit=500"
    )
    response = requests.get(url).json()

    stations_under_wfo = []
    for station in response["features"]:
        station_info = {}
        station_info["id"] = station["properties"]["stationIdentifier"]
        station_info["name"] = station["properties"]["name"]

        stations_under_wfo.append(station_info)

    logger.info(stations_under_wfo)
    return stations_under_wfo


@flow(
    name="report_wfo_stations",
    flow_run_name=flow_run_name,
    persist_result=True,
    result_serializer=JSONSerializer(),
)
async def report_wfo_stations(address):
    logger = get_run_logger()

    # format address for API request
    api_friendly_address = get_api_friendly_address.submit(address)

    dummy_result = dummy_task.submit()

    # get latitude, longitude
    coords = get_geocode_coords(api_friendly_address, dummy_result)

    # get office and gridpoint for lat, long
    (office, (grid_x, grid_y)) = get_office_and_gridpoint(coords["lat"], coords["long"])

    stations = get_wfo_stations(office, grid_x, grid_y)
    logger.info(f"# stations under {office}: {len(stations)}")

    return stations


@flow(
    retries=0,
    retry_delay_seconds=5,
    log_prints=True,
    task_runner=ConcurrentTaskRunner,
    # result_storage=LocalFileSystem.load("results"),
    result_storage=S3.load("s3-storage"),
)
async def list_observation_stations(addresses: list[str]):
    parallel_subflows = [report_wfo_stations(address) for address in addresses]
    await asyncio.gather(*parallel_subflows)


if __name__ == "__main__":
    asyncio.run(
        list_observation_stations(
            [
                "815 Pete Rose Way Cincinnati, OH 45202",
                "777 California Ave Suite 150, Palo Alto, CA 94306",
            ]
        )
    )
