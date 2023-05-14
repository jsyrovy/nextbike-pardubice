import dataclasses
import datetime
import json
import pathlib
import time
import urllib.error
import urllib.request

ENCODING = "UTF-8"
COUNTRY = "cz"
CITY = "Pardubice"
URL = f"https://api.nextbike.net/maps/nextbike-official.json?countries={COUNTRY}"
DATA_DIRECTORY = "data"


@dataclasses.dataclass()
class Place:
    uid: int
    name: str
    bikes_available_to_rent: int


def main() -> None:
    data = try_get_data()
    places = get_places(data)
    save_places(places)
    save_bike_states(places)


def get_data() -> dict:
    request = urllib.request.urlopen(URL)
    return json.load(request)


def try_get_data() -> dict:
    for _ in range(3):
        try:
            return get_data()
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            print(e)
            time.sleep(5)

    print(f"Cannot connect to '{URL}'.")
    exit(1)


def get_places(data: dict) -> list[Place]:
    countries = data["countries"]

    if len(countries) == 0:
        print(f"Country '{COUNTRY}' not found.")
        exit(1)

    city_countries = [
        c for c in countries if c["name"].lower() == f"nextbike {CITY}".lower()
    ]

    if len(city_countries) == 0:
        print(f"Country for city '{CITY}' not found.")
        exit(1)

    cities = city_countries[0]["cities"]

    if len(cities) == 0:
        print(f"City '{CITY}' not found.")
        exit(1)

    city = cities[0]

    print("Data were downloaded.")

    return [
        Place(p["uid"], p["name"], p["bikes_available_to_rent"]) for p in city["places"]
    ]


def save_places(places: list[Place]) -> None:
    path = pathlib.Path(DATA_DIRECTORY) / "places.csv"

    if not path.parent.exists():
        path.parent.mkdir(parents=True)

    content = path.read_text(encoding=ENCODING) if path.exists() else ""

    lines = [f"{p.uid};{p.name}\n" for p in places if str(p.uid) not in content]
    count = len(lines)

    if not path.exists():
        lines.insert(0, "uid;name\n")

    with path.open("a", encoding=ENCODING) as f:
        f.writelines(lines)

    print(f"{count} places were saved.")


def save_bike_states(places: list[Place]) -> None:
    dt = datetime.datetime.now()
    path = pathlib.Path(DATA_DIRECTORY) / f"{dt.year}/{dt:%m}/{dt:%Y-%m-%d}.csv"

    if not path.parent.exists():
        path.parent.mkdir(parents=True)

    lines = [
        f"{dt:%Y-%m-%d %H:%M:%S},{p.uid},{p.bikes_available_to_rent}\n" for p in places
    ]
    count = len(lines)

    if not path.exists():
        lines.insert(0, "dt,uid,bikes_available_to_rent\n")

    with path.open("a", encoding=ENCODING) as f:
        f.writelines(lines)

    print(f"{count} bike states were saved.")


def get_last_successful_run_dt() -> datetime.datetime:
    directory = pathlib.Path(DATA_DIRECTORY)
    files = directory.rglob("*.csv")

    if not files:
        return datetime.datetime.min

    last_timestamp = max(file.stat().st_mtime for file in files)
    return datetime.datetime.fromtimestamp(last_timestamp)


if __name__ == "__main__":
    last_successful_run_dt = get_last_successful_run_dt()

    try:
        main()
    except Exception as e:
        if last_successful_run_dt < datetime.datetime.now() - datetime.timedelta(
            hours=4
        ):
            raise

        print(
            "The script failed, but the last successful run was less than 4 hours ago."
        )
        print(f"Error: {e}")
