#!/usr/bin/env python

from datetime import (
    datetime,
    timedelta
    )


def week_start(dt=None):
    """
    Calculates the ISO week start datetime for the given time
    @param dt: Datetime to calculate from (defaults to now)
    @returns: datetime of week start
    """
    if dt is None:
        dt = datetime.today()
    week_days = datetime.isoweekday(dt) % 7
    week_start = dt - timedelta(days=week_days)
    return week_start.replace(hour=0, minute=0, second=0, microsecond=0)

def total_seconds(td):
    tsec = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6)/10**6
    return tsec

if __name__ == '__main__':
    print week_start()

    td = timedelta(days=10, seconds=2.999)
    dt = datetime.today() - td
    print week_start(dt)

    print "%d == %d\n" %(total_seconds(td), td.total_seconds())
