Plan Your Sprints (pysprints)
-----------------------------

Calculation objects to handle varying sprint/point commitment across various
releases.

Example
=======

    >>> import datetime
    >>>
    >>> from pysprints import ReleasePlan
    >>>
    >>> release_plan = ReleasePlan(start_sprint_number=5,
    ...                            start_date=datetime.date(year=2012,
    ...                                                     month=5,
    ...                                                     day=17),
    ...                            sprint_length_calendar_days=15)
    >>>
    >>> release_plan.add_release(name='Foo', points=20)
    >>> release_plan.add_release(name='Bar', points=50)
    >>> release_plan.next_sprint(points_mix=(('Foo', 10),
    ...                                      ('Bar', 20)))
    Sprint(number=5, start_date=2012-5-17, length_calendar_days=15)
    >>> release_plan.next_sprint(points_mix=(('Foo', 15),
    ...                                      ('Bar', 15)))
    Sprint(number=6, start_date=2012-6-1, length_calendar_days=15)
    >>> release_plan.end('Foo')
    Sprint(number=6, start_date=2012-6-1, length_calendar_days=15)
    >>> release_plan.end('Foo').number
    6
    >>> release_plan.end('Foo').end_date
    datetime.date(2012, 6, 15)
    >>> release_plan.end('Bar')
    >>>
    >>> release_plan.end_dict
    {'Foo': Sprint(number=6, start_date=2012-6-1, length_calendar_days=15), 'Bar': None}
