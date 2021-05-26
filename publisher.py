import dataclasses
import datetime
import pathlib
import sqlite3

import jinja2
import pandas


@dataclasses.dataclass
class Record:
    uid: int
    name: str
    time: str
    bikes_available_to_rent: int


@dataclasses.dataclass
class Chart:
    uid: int
    name: str
    labels: str
    serie: str
    highest_value: int


def main() -> None:
    with sqlite3.connect(":memory:") as conn:
        load_places(conn)
        load_bikes_states(conn)

        charts = get_charts(conn.cursor())
        highest_value = max([c.highest_value for c in charts])
        publish_page(charts, highest_value)


def load_places(conn: sqlite3.Connection) -> None:
    path = pathlib.Path("data/places.csv")
    load_csv(conn, path, "places")
    print(f"Places were loaded.")


def load_bikes_states(conn: sqlite3.Connection) -> None:
    paths = list(pathlib.Path("data").glob("*/*/*.csv"))

    for path in paths:
        load_csv(conn, path, "bike_states")

    print(f"Bike states were loaded.")


def load_csv(conn: sqlite3.Connection, path: pathlib.Path, table_name) -> None:
    df = pandas.read_csv(path, sep=",")
    df.to_sql(table_name, conn, if_exists="append")


def get_charts(cursor: sqlite3.Cursor) -> list[Chart]:
    charts = []
    records = get_records(cursor)

    for record in sorted(set([r.name for r in records])):
        charts.append(
            Chart(
                [r.uid for r in records if r.name == record][0],
                record,
                str([r.time for r in records if r.name == record]),
                str([r.bikes_available_to_rent for r in records if r.name == record]),
                max([r.bikes_available_to_rent for r in records if r.name == record]),
            )
        )

    print("Data were selected.")
    return charts


def get_records(cursor: sqlite3.Cursor) -> list[Record]:
    cursor.execute(
        "SELECT p.uid, p.name, strftime('%H:%M', dt), bikes_available_to_rent "
        "FROM bike_states bs "
        "JOIN places p ON bs.uid = p.uid "
        f"WHERE bs.dt >= '{datetime.datetime.now() - datetime.timedelta(hours=12)}'"
        "ORDER BY p.name, bs.dt"
    )
    return [Record(int(r[0]), r[1], r[2], int(r[3])) for r in cursor.fetchall()]


def publish_page(charts: list[Chart], highest_value: int) -> None:
    page = pathlib.Path("index.html")
    page.write_text(
        get_template().render(
            charts=charts,
            dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            highest_value=highest_value,
        ),
        "UTF-8",
    )
    print("Page was published.")


def get_template() -> jinja2.Template:
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("publisher", "templates"),
        autoescape=jinja2.select_autoescape(["html", "xml"]),
    )
    return env.get_template("index.html")


if __name__ == "__main__":
    main()
