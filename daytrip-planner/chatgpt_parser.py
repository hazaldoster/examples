import os
import base64
import time
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from openai import OpenAI


class TravelDestination(BaseModel):
    """Model for travel destination data"""

    location: str = Field(..., description="The name of the destination city/location")
    price: int = Field(
        ...,
        description="The listed price of just the tickets to the destination (without $ sign)",
    )
    start_date: str = Field(
        ...,
        description=f"The start date of the trip in YYYY-MM-DD format (e.g., '2024-06-15'). If the year is not specified, use the current year, i.e., {time.strftime('%Y')}",
    )
    end_date: str = Field(
        ...,
        description=f"The end date of the trip in YYYY-MM-DD format (e.g., '2023-06-17'). If the year is not specified, use the current year, i.e., {time.strftime('%Y')}",
    )
    travel_time: str = Field(
        ...,
        description="The time it takes to travel to the destination (e.g., '2h 30m')",
    )
    stay_cost: int = Field(
        ..., description="The listed price of just the accommodations (without $ sign)"
    )


class TravelResponseData(BaseModel):
    """Container for a list of travel destinations"""

    destinations: List[TravelDestination] = Field(
        ..., description="List of travel destination options"
    )


def extract_travel_data_from_image(image_path):
    """
    Use ChatGPT Vision API to extract structured travel data from a screenshot.
    Returns a list of TravelDestination objects.
    """
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Set the OPENAI_API_KEY environment variable."
        )

    # Initialize the OpenAI client
    client = OpenAI(api_key=api_key)

    # Read the image file and encode it to base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    # Make the API request using the OpenAI SDK with structured output
    try:
        # First approach: Using JSON schema in response_format
        response = client.beta.chat.completions.parse(
            model="gpt-4o",  # Using GPT-4o for better vision capabilities
            messages=[
                {
                    "role": "system",
                    "content": "Extract travel information from screenshots in a structured format following the provided JSON schema.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is a screenshot from Google Travel Explore showing weekend getaway options. Extract the following information for each destination: location name, ticket price, recommended trip duration, travel time, and approximate stay cost. Format your response according to the JSON schema.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            },
                        },
                    ],
                },
            ],
            # Specify the schema in the response_format
            response_format=TravelResponseData,
        )

        # Parse the response
        content = response.choices[0].message.parsed
        if not content:
            raise ValueError("No content in response")
        destinations = content.destinations
        return destinations

    except Exception as e:
        print(f"Error using JSON schema in response_format: {str(e)}")
