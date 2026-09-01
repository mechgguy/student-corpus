import json
import re
from pathlib import Path


POSTCODE_PATTERN = re.compile(
    r"\b\d{4,5}\b"
)


def load_cities():

    config_path = (
        Path(__file__).resolve()
        .parents[2]
        / "configs"
        / "cities.json"
    )

    if not config_path.exists():
        return {}

    with open(
        config_path,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def extract_location(text: str):

    if not text:
        return None

    cities = load_cities()

    # CV location is usually near the beginning.
    header = "\n".join(
        text.splitlines()[:40]
    )

    header_lower = header.lower()

    # --------------------------------------------------
    # 1. City + country from configured city list
    # --------------------------------------------------

    for country, city_list in cities.items():

        for city in city_list:

            pattern = rf"(?<!\w){re.escape(city.lower())}(?!\w)"

            if re.search(
                pattern,
                header_lower,
            ):

                return f"{city}, {country}"

    # --------------------------------------------------
    # 2. Postal code fallback
    # --------------------------------------------------

    postcode = POSTCODE_PATTERN.search(
        header
    )

    if postcode:

        return postcode.group(0)

    return None
