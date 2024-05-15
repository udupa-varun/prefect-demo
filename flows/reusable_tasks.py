from prefect import task, get_run_logger

import requests


@task
def get_api_friendly_address(address: str) -> str:
    logger = get_run_logger()
    out_address = address.replace(",", "%2C")
    out_address = out_address.replace(" ", "+")

    logger.info(f"Input address: {address}")
    logger.info(f"Formatted address: {out_address}")

    return out_address


@task
def get_geocode_coords(address: str, dummy: int = 1) -> dict[str, float]:
    logger = get_run_logger()
    res = {}
    url = f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address={address}&benchmark=2020&format=json"

    logger.info(f"Requesting data from: {url} ...")
    response = requests.get(url).json()
    res["long"] = response["result"]["addressMatches"][0]["coordinates"]["x"]
    res["lat"] = response["result"]["addressMatches"][0]["coordinates"]["y"]

    return res


@task
def get_office_and_gridpoint(lat: float, long: float) -> str:
    logger = get_run_logger()
    url = f"https://api.weather.gov/points/{lat},{long}"

    logger.info(f"Requesting data from: {url} ...")
    response = requests.get(url)
    office = response.json()["properties"]["gridId"]
    grid_x = response.json()["properties"]["gridX"]
    grid_y = response.json()["properties"]["gridY"]

    return (office, (grid_x, grid_y))
