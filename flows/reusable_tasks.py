from prefect import task

import requests


@task
def get_api_friendly_address(address: str) -> str:
    out_address = address.replace(",", "%2C")
    out_address = out_address.replace(" ", "+")

    return out_address


@task
def get_geocode_coords(address: str, dummy: int = 1) -> dict[str, float]:
    res = {}
    url = f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address={address}&benchmark=2020&format=json"

    response = requests.get(url).json()

    res["long"] = response["result"]["addressMatches"][0]["coordinates"]["x"]
    res["lat"] = response["result"]["addressMatches"][0]["coordinates"]["y"]

    return res


@task
def get_office_and_gridpoint(lat: float, long: float) -> str:
    url = f"https://api.weather.gov/points/{lat},{long}"
    response = requests.get(url)

    office = response.json()["properties"]["gridId"]
    grid_x = response.json()["properties"]["gridX"]
    grid_y = response.json()["properties"]["gridY"]

    return (office, (grid_x, grid_y))
