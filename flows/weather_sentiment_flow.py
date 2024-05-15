from datetime import timedelta

from prefect import task, flow, get_run_logger
from prefect.blocks.system import Secret
# from prefect.filesystems import LocalFileSystem

import marvin
import requests

from .reusable_tasks import (
    get_api_friendly_address,
    get_geocode_coords,
    get_office_and_gridpoint,
)


@task(cache_result_in_memory=True, cache_expiration=timedelta(hours=6))
def get_detailed_forecast(
    office: str,
    grid_x: int,
    grid_y: int,
    num_forecast_periods: int = 3,
) -> list[dict]:
    logger = get_run_logger()
    forecast_url = f"https://api.weather.gov/gridpoints/{office}/{grid_x},{grid_y}/forecast?units=si"
    logger.info(f"Requesting data from: {forecast_url}...")
    response = requests.get(forecast_url)
    response_properties = response.json()["properties"]
    last_updated = response_properties["updated"]

    detailed_forecasts = []
    for period in response_properties["periods"][:num_forecast_periods]:
        period_forecast = {}
        period_forecast["last_updated"] = last_updated
        period_forecast["period"] = period["name"]
        period_forecast["detailed_forecast"] = period["detailedForecast"]

        detailed_forecasts.append(period_forecast)

    return detailed_forecasts


@task(persist_result=True)
def run_sentiment_analysis(input_data: str, labels: list[str]) -> list[dict[str]]:
    logger = get_run_logger()

    res = []
    logger.info("Sentiment analysis result:")
    for period_forecast in input_data:
        period_res = {}
        period_res["name"] = period_forecast["period"]
        period_res["forecast"] = period_forecast["detailed_forecast"]

        period_res["result"] = marvin.classify(
            data=period_res["forecast"], labels=labels
        )
        logger.info(period_res)
        res.append(period_res)

    return res


@flow(
    retries=0,
    retry_delay_seconds=5,
    log_prints=True,
    # result_storage=LocalFileSystem.load("results"),
)
def analyze_weather_data(address: str, labels: list[str]):
    logger = get_run_logger()

    secret_block = Secret.load("openai-creds")
    marvin.settings.openai.api_key = secret_block.get()

    # format address for API request
    api_friendly_address = get_api_friendly_address(address)

    # get latitude, longitude
    coords = get_geocode_coords(api_friendly_address)

    # get office and gridpoint for lat, long
    (office, (grid_x, grid_y)) = get_office_and_gridpoint(coords["lat"], coords["long"])

    detailed_forecast = get_detailed_forecast(office, grid_x, grid_y)
    logger.info("Detailed forecast:")
    logger.info(detailed_forecast)

    # perform sentiment analysis on detailed forecast and report result
    logger.info("Based on the weather forecast, which of these options is appropriate?")
    logger.info(labels)
    logger.info("Running sentiment analysis to find out...")
    run_sentiment_analysis(input_data=detailed_forecast, labels=labels)
