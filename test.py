import dataclasses
import json

COUNTRY = "cz"
CITY = "Pardubice"
DATA = """{
  "countries": [
    {
      "name": "nextbike Prostejov",
      "cities": [
        {
          "name": "Prostejov",
          "places": [
            {
              "uid": 12705340,
              "name": "Nemocnice Agel",
              "bikes_available_to_rent": 6
            }
          ]
        }
      ]
    },
    {
      "name": "nextbike Pardubice",
      "cities": [
        {
          "name": "Pardubice",
          "places": [
            {
              "uid": 29745906,
              "name": "Aquacentrum Pardubice",
              "bikes_available_to_rent": 2
            },
            {
              "uid": 29746009,
              "name": "Sokolovna - Na Olšinkách",
              "bikes_available_to_rent": 1
            }
          ]
        }
      ]
    }
  ]
}
"""


@dataclasses.dataclass()
class Place:
    uid: int
    name: str
    bikes_available_to_rent: int


def main() -> None:
    print(get_places(json.loads(DATA)))
    print(get_places2(json.loads(DATA)))
    print(get_places3(json.loads(DATA)))


def get_places(data: dict) -> list[Place]:
    countries = data["countries"]

    if not countries:
        print(f"Country '{COUNTRY}' not found.")
        exit(1)

    city_countries = [
        c for c in countries if c["name"].lower() == f"nextbike {CITY}".lower()
    ]

    if not city_countries:
        print(f"Country for city '{CITY}' not found.")
        exit(1)

    cities = city_countries[0]["cities"]

    if not cities:
        print(f"City '{CITY}' not found.")
        exit(1)

    city = cities[0]

    return [
        Place(p["uid"], p["name"], p["bikes_available_to_rent"]) for p in city["places"]
    ]


def get_places2(data: dict) -> list[Place]:
    country = [c for c in data["countries"] if c["name"] == "nextbike Pardubice"][0]
    city = [c for c in country["cities"] if c["name"] == "Pardubice"][0]
    return [
        Place(p["uid"], p["name"], p["bikes_available_to_rent"]) for p in city["places"]
    ]


def get_places3(data: dict) -> list[Place]:
    return [
        Place(p["uid"], p["name"], p["bikes_available_to_rent"])
        for p in [
            c
            for c in [
                c for c in data["countries"] if c["name"] == "nextbike Pardubice"
            ][0]["cities"]
            if c["name"] == "Pardubice"
        ][0]["places"]
    ]


if __name__ == "__main__":
    main()
