import datetime


class ReleasePlan(object):
    """
    Object with which to map future sprints.

    """
    def __init__(self, start_sprint_number, start_date,
                 sprint_length_calendar_days):
        self.start_sprint_number = start_sprint_number
        self.start_date = start_date
        self.sprint_length_calendar_days = sprint_length_calendar_days
        super(ReleasePlan, self).__init__()

    def add_release(self, name, points):
        if not hasattr(self, 'releases'):
            self.releases = dict()
        else:
            if name in self.releases:
                raise ValueError(
                    'Release "{name}" already in ReleasePlan'.format(
                        name=name))
        self.releases[name] = points

    def next_sprint(self, points_mix):
        if not hasattr(self, 'sprints'):
            self.sprints = list()
            new_sprint_number = self.start_sprint_number
            new_start_date = self.start_date
        else:
            most_recent_sprint = self.sprints[-1]
            new_sprint_number = 1 + most_recent_sprint.number
            new_start_date = (
                most_recent_sprint.start_date +
                datetime.timedelta(days=self.sprint_length_calendar_days))
        new_sprint = \
            Sprint(number=new_sprint_number,
                   start_date=new_start_date,
                   length_calendar_days=self.sprint_length_calendar_days,
                   points_mix=points_mix)
        self.sprints.append(new_sprint)
        return new_sprint

    def end(self, release_name):
        points_left = self.releases[release_name]
        for sprint in self.sprints:
            points_left -= sprint.points_mix(release_name)
            if points_left <= 0:
                return sprint

    @property
    def end_dict(self):
        return dict([(release_name, self.end(release_name))
                    for release_name in self.releases])

    def __repr__(self):
        return (
            '{cls}(start_sprint_number={start_sprint_number}, '
            'start_date={year}-{month}-{day}, '
            'sprint_length_calendar_days='
            '{sprint_length_calendar_days})'.format(
                cls=self.__class__.__name__,
                start_sprint_number=self.start_sprint_number,
                year=self.start_date.year,
                month=self.start_date.month,
                day=self.start_date.day,
                sprint_length_calendar_days=self.sprint_length_calendar_days))


class Sprint(object):
    def __init__(self, number, start_date, length_calendar_days, points_mix):
        self.number = number
        self.start_date = start_date
        self.length_calendar_days = length_calendar_days
        self.points_mix = lambda x: dict(points_mix).get(x, 0)

    @property
    def end_date(self):
        return (self.start_date +
                datetime.timedelta(days=self.length_calendar_days) -
                datetime.timedelta(days=1))

    def __repr__(self):
        return ('{cls}(number={number}, start_date={year}-{month}-{day}, '
                'length_calendar_days={length_calendar_days})'.format(
                    cls=self.__class__.__name__,
                    number=self.number,
                    year=self.start_date.year,
                    month=self.start_date.month,
                    day=self.start_date.day,
                    length_calendar_days=self.length_calendar_days))
