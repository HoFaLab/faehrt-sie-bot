from datetime import datetime, time

Timetable = list[datetime]

timetable_wilhelmsburg: Timetable = [
    datetime(hour=5, minute=50, year=2020, month=1, day=1),
    datetime(hour=6, minute=10, year=2020, month=1, day=1),
    datetime(hour=6, minute=30, year=2020, month=1, day=1),
    datetime(hour=6, minute=50, year=2020, month=1, day=1),
    datetime(hour=7, minute=10, year=2020, month=1, day=1),
    datetime(hour=7, minute=30, year=2020, month=1, day=1),
    datetime(hour=7, minute=50, year=2020, month=1, day=1),
    datetime(hour=8, minute=10, year=2020, month=1, day=1),
    datetime(hour=8, minute=30, year=2020, month=1, day=1),
    datetime(hour=8, minute=50, year=2020, month=1, day=1),
    datetime(hour=9, minute=30, year=2020, month=1, day=1),
    datetime(hour=10, minute=10, year=2020, month=1, day=1),
    datetime(hour=10, minute=50, year=2020, month=1, day=1),
    datetime(hour=11, minute=30, year=2020, month=1, day=1),
    datetime(hour=12, minute=10, year=2020, month=1, day=1),
    datetime(hour=12, minute=50, year=2020, month=1, day=1),
    datetime(hour=13, minute=30, year=2020, month=1, day=1),
    datetime(hour=14, minute=10, year=2020, month=1, day=1),
    datetime(hour=14, minute=50, year=2020, month=1, day=1),
    datetime(hour=15, minute=10, year=2020, month=1, day=1),
    datetime(hour=15, minute=30, year=2020, month=1, day=1),
    datetime(hour=15, minute=50, year=2020, month=1, day=1),
    datetime(hour=16, minute=10, year=2020, month=1, day=1),
    datetime(hour=16, minute=30, year=2020, month=1, day=1),
    datetime(hour=16, minute=50, year=2020, month=1, day=1),
    datetime(hour=17, minute=10, year=2020, month=1, day=1),
    datetime(hour=17, minute=50, year=2020, month=1, day=1),
    datetime(hour=18, minute=30, year=2020, month=1, day=1),
    datetime(hour=19, minute=10, year=2020, month=1, day=1),
    datetime(hour=19, minute=50, year=2020, month=1, day=1),
    datetime(hour=20, minute=30, year=2020, month=1, day=1),
    datetime(hour=21, minute=10, year=2020, month=1, day=1),
    datetime(hour=21, minute=50, year=2020, month=1, day=1)
    ]

timetable_landungsbruecken: Timetable = [
    datetime(hour=5, minute=30, year=2020, month=1, day=1),
    datetime(hour=5, minute=50, year=2020, month=1, day=1),
    datetime(hour=6, minute=10, year=2020, month=1, day=1),
    datetime(hour=6, minute=30, year=2020, month=1, day=1),
    datetime(hour=6, minute=50, year=2020, month=1, day=1),
    datetime(hour=7, minute=10, year=2020, month=1, day=1),
    datetime(hour=7, minute=30, year=2020, month=1, day=1),
    datetime(hour=7, minute=50, year=2020, month=1, day=1),
    datetime(hour=8, minute=10, year=2020, month=1, day=1),
    datetime(hour=8, minute=30, year=2020, month=1, day=1),
    datetime(hour=9, minute=10, year=2020, month=1, day=1),
    datetime(hour=9, minute=50, year=2020, month=1, day=1),
    datetime(hour=10, minute=30, year=2020, month=1, day=1),
    datetime(hour=11, minute=50, year=2020, month=1, day=1),
    datetime(hour=12, minute=30, year=2020, month=1, day=1),
    datetime(hour=13, minute=10, year=2020, month=1, day=1),
    datetime(hour=13, minute=50, year=2020, month=1, day=1),
    datetime(hour=14, minute=30, year=2020, month=1, day=1),
    datetime(hour=14, minute=50, year=2020, month=1, day=1),
    datetime(hour=15, minute=10, year=2020, month=1, day=1),
    datetime(hour=15, minute=30, year=2020, month=1, day=1),
    datetime(hour=15, minute=50, year=2020, month=1, day=1),
    datetime(hour=16, minute=10, year=2020, month=1, day=1),
    datetime(hour=16, minute=30, year=2020, month=1, day=1),
    datetime(hour=16, minute=50, year=2020, month=1, day=1),
    datetime(hour=17, minute=30, year=2020, month=1, day=1),
    datetime(hour=18, minute=10, year=2020, month=1, day=1),
    datetime(hour=18, minute=50, year=2020, month=1, day=1),
    datetime(hour=19, minute=30, year=2020, month=1, day=1),
    datetime(hour=20, minute=10, year=2020, month=1, day=1),
    datetime(hour=20, minute=50, year=2020, month=1, day=1),
    datetime(hour=21, minute=30, year=2020, month=1, day=1)
]

def next_ferry_from_whb() -> time:
    return get_next_departure_in_timetable(timetable_wilhelmsburg)

def next_ferry_from_landungsbruecken() -> time:
    return get_next_departure_in_timetable(timetable_landungsbruecken)

def get_next_departure_in_timetable(timetable: Timetable) -> time:
    time_now = datetime.now().time()

    for departure_time in timetable:
        if departure_time.time() > time_now:
            return departure_time.time()


if __name__ == "__main__":
    print("next_ferry_from_landungsbruecken")
    print(next_ferry_from_landungsbruecken())