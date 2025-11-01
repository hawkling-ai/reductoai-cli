"""Client wrapper for the Reducto SDK."""

import os

from dotenv import load_dotenv
from reducto import Reducto

# Load environment variables from .env file
load_dotenv()


def get_client(environment: str = "production") -> Reducto:
    """
    Create and return a Reducto client.

    Args:
        environment: The API environment to use (production, eu, or au)

    Returns:
        Reducto client instance

    Raises:
        ValueError: If REDUCTO_API_KEY is not set
    """
    api_key = os.environ.get("REDUCTO_API_KEY")

    if not api_key:
        raise ValueError(
            "REDUCTO_API_KEY environment variable is not set. "
            "Please set it in your environment or .env file."
        )

    return Reducto(api_key=api_key, environment=environment)
