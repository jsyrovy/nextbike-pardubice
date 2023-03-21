import downloader


def test_get_places():
    data = {
        "countries": [
            {
                "name": "nextbike Pardubice",
                "cities": [
                    {
                        "name": "Pardubice",
                        "places": [
                            {"uid": 1, "name": "Name", "bikes_available_to_rent": 2}
                        ],
                    }
                ],
            }
        ]
    }

    places = downloader.get_places(data)

    assert len(places) == 1
    assert places[0].uid == 1
    assert places[0].name == "Name"
    assert places[0].bikes_available_to_rent == 2
