"""Deployment script for all Prefect flows.
Any edits to this file require re-submission of all deployments.

Author: Varun Udupa
Date: 5/12/2024
"""

from flows.weather_sentiment_flow import analyze_weather_data
from flows.wfo_stations import list_observation_stations

from prefect import serve

SP_ADDR = "815 Pete Rose Way Cincinnati, OH 45202"
PA_ADDR = "777 California Ave Suite 150, Palo Alto, CA 94306"

if __name__ == "__main__":
    # ---------------------------------------------------------------------------------------------------------------- #
    #                                             CREATE DEPLOYMENT OBJECTS                                            #
    # ---------------------------------------------------------------------------------------------------------------- #
    weather_sentiment_SP = analyze_weather_data.to_deployment(
        name="weather_sentiment_sawyerpoint",
        parameters={
            "address": SP_ADDR,
            "labels": [
                "Weather suitable for playing outdoor sports",
                "Weather is either rainy, windy or too cold - stay indoors",
            ],
        },
        cron="30 16 * * 1,3,5",
        tags=["level-basic", "weather", "sawyer_point"],
        description="Weather analysis for Sawyer Point",
        version="0.1.0",
    )

    weather_sentiment_PA = analyze_weather_data.to_deployment(
        name="weather_sentiment_paloalto",
        parameters={
            "address": PA_ADDR,
            "labels": [
                "Sunglasses recommended",
                "Sunglasses not required",
            ],
        },
        cron="0 * * * *",
        tags=["level-basic", "weather", "palo_alto"],
        description="Weather analysis for Palo Alto",
        version="0.1.0",
    )

    wfo_stations_both = list_observation_stations.to_deployment(
        name="weather_office_stations",
        parameters={
            "addresses": [SP_ADDR, PA_ADDR],
        },
        cron="0 7 * * *",
        tags=["weather", "stations", "level-advanced"],
        description="Observation stations for given addresses",
        version="0.1.0",
    )

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                             SERVE DEPLOYMENT OBJECTS                                             #
    # ---------------------------------------------------------------------------------------------------------------- #
    # choose deployment objects to serve
    serve(
        weather_sentiment_SP,
        weather_sentiment_PA,
        wfo_stations_both,
    )
