import dataclasses
import datetime
import pathlib
import sqlite3

import jinja2
import pandas

INDEX_TEMPLATE = "index.html"


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

        charts = get_charts(get_records(conn.cursor()))
        highest_value = max([c.highest_value for c in charts])
        title = "Dostupnost za posledních 12 hodin<br><a href='24h.html'>Zobrazit posledních 24 hodin</a>"
        publish_page(charts, highest_value, title)

        charts_24h = get_charts(get_grouped_records(conn.cursor(), 24))
        highest_value_24h = max([c.highest_value for c in charts_24h])
        title_24h = "Dostupnost za posledních 24 hodin<br><a href='index.html'>Zobrazit posledních 12 hodin</a>"
        publish_page(charts_24h, highest_value_24h, title_24h, "24h.html")


def load_places(conn: sqlite3.Connection) -> None:
    path = pathlib.Path("data/places.csv")
    load_csv(conn, path, "places", separator=";")
    print("Places were loaded.")


def load_bikes_states(conn: sqlite3.Connection) -> None:
    paths = list(pathlib.Path("data").glob("*/*/*.csv"))

    for path in paths:
        load_csv(conn, path, "bike_states")

    print("Bike states were loaded.")


def load_csv(
    conn: sqlite3.Connection, path: pathlib.Path, table_name: str, separator: str = ","
) -> None:
    df = pandas.read_csv(path, sep=separator)
    df.to_sql(table_name, conn, if_exists="append")


def get_charts(records: list[Record]) -> list[Chart]:
    charts = []

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


def get_grouped_records(cursor: sqlite3.Cursor, hours: int) -> list[Record]:
    cursor.execute(
        "SELECT p.uid, p.name, STRFTIME('%d %H', dt), ROUND(AVG(bikes_available_to_rent), 0) "
        "FROM bike_states bs "
        "JOIN places p ON bs.uid = p.uid "
        f"WHERE bs.dt >= '{datetime.datetime.now() - datetime.timedelta(hours=hours)}'"
        "GROUP BY p.uid, p.name, STRFTIME('%d %H', dt)"
        "ORDER BY p.name, bs.dt"
    )
    return [Record(int(r[0]), r[1], r[2], int(r[3])) for r in cursor.fetchall()]


def publish_page(
    charts: list[Chart], highest_value: int, title: str, path="index.html"
) -> None:
    page = pathlib.Path(path)
    page.write_text(
        get_template().render(
            charts=charts,
            dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            highest_value=highest_value,
            title=title,
        ),
        "UTF-8",
    )
    print("Page was published.")


def get_template() -> jinja2.Template:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"),
        autoescape=jinja2.select_autoescape(["html", "xml"]),
    )
    return env.get_template(INDEX_TEMPLATE)


if __name__ == "__main__":
    main()
