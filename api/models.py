from datetime import datetime, timedelta
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, \
    MinValueValidator, MaxValueValidator
from django.utils import timezone


class ExtendedUser(models.Model):
    is_verified = models.BooleanField(default=False)
    credit = models.IntegerField(default=0, blank=True, )
    base_user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='extended',
    )
    ban_list = models.ManyToManyField(
        User,
        related_name='banned',
        blank=True,
    )
    phone_number = models.CharField(
        validators=[
            RegexValidator(regex=r'^0\d{8,9}$'),
        ],
        max_length=12,
        blank=True,
    )

    def __str__(self):
        return self.base_user.username

    class Meta:
        unique_together = ('base_user',)


class Court(models.Model):
    is_verified = models.BooleanField(default=False)
    price = models.IntegerField(validators=[MinValueValidator(0), ])
    court_count = models.IntegerField(blank=False)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courts',
    )
    lat = models.FloatField()
    long = models.FloatField()
    name = models.CharField(max_length=30)
    desc = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

    def rating_count(self):
        return len(self.reviews.all())

    def avg_score(self):
        m_sum = 0
        reviews = self.reviews.all()
        if not reviews:
            return 0
        for review in reviews:
            m_sum += review.score
        return m_sum / len(reviews)

    def check_collision(self, day_of_the_week, start, end):
        for schedule in self.schedules.filter(day_of_the_week=day_of_the_week):
            if schedule.check_collision(start, end) == 0:
                return 0
        return 1

    def book(self, day_of_the_week, start, end):
        for schedule in self.schedules.filter(day_of_the_week=day_of_the_week):
            if schedule.book(start, end) == 0:
                return 0, schedule.court_number
        return 1, -1

    def unbooked(self, day_of_the_week, start, end, court_number):
        schedule = self.schedules.get(day_of_the_week=day_of_the_week, court_number=court_number)
        schedule.unbooked(start, end)
        return 0


class Booking(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    court = models.ForeignKey(
        Court,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    booked_date = models.DateTimeField(auto_now=True)
    day_of_the_week = models.IntegerField()
    court_number = models.IntegerField()
    start = models.IntegerField()
    end = models.IntegerField()
    price = models.IntegerField(validators=[MinValueValidator(0), ])


class Racket(models.Model):
    name = models.CharField(max_length=30)
    price = models.IntegerField(validators=[MinValueValidator(0), ])
    court = models.ForeignKey(
        Court,
        related_name='rackets',
        on_delete=models.CASCADE,
    )

    def check_collision(self, day_of_the_week, start, end):
        schedule = self.schedules.get(day_of_the_week=day_of_the_week)
        if schedule.check_collision(start, end) == 0:
            return 0
        return 1

    def book(self, day_of_the_week, start, end):
        schedule = self.schedules.get(day_of_the_week=day_of_the_week)
        if schedule.book(start, end) == 0:
            return 0
        return 1

    def __str__(self):
        return self.name


class Schedule(models.Model):
    court = models.ForeignKey(
        Court,
        on_delete=models.CASCADE,
        related_name='schedules',
        blank=True
    )

    racket = models.ForeignKey(
        Racket,
        on_delete=models.CASCADE,
        related_name='schedules',
        blank=True
    )

    class Day(models.IntegerChoices):
        Monday = 0,
        Tuesday = 1,
        Wednesday = 2,
        Thursday = 3,
        Friday = 4,
        Saturday = 5,
        Sunday = 6

    day_of_the_week = models.IntegerField(choices=Day.choices)
    status = models.BigIntegerField(default=0)
    last_update = models.DateTimeField(auto_now_add=True)
    court_number = models.IntegerField(blank=True)

    def update(self):
        dist = timezone.localtime(timezone.now()).weekday() \
               - self.day_of_the_week
        if dist < 0:
            dist += 7
        cut_off_day = timezone.localtime(timezone.now()) \
                      - timedelta(days=dist)
        cut_off_day.replace(hour=0, minute=0, second=0)
        if self.last_update < cut_off_day:
            self.status = 0
        self.last_update = timezone.localtime(timezone.now())

    def check_collision(self, start, end):
        self.update()
        for i in range(start, end + 1):
            if ((1 << i) & self.status) != 0:
                return 1
        return 0

    def book(self, start, end):
        if self.check_collision(start, end) != 0:
            return 1
        for i in range(start, end + 1):
            self.status |= 1 << i
        self.save()
        return 0

    def unbooked(self, start, end):
        for i in range(start, end + 1):
            self.status &= ~(1 << i)
        self.save()
        return 0

    def __str__(self):
        return "%s of court %s in %s" % \
               (self.day_of_the_week, self.court_number, self.court)

    class Meta:
        unique_together = (('court', 'court_number', 'day_of_the_week'),)


class Review(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    court = models.ForeignKey(
        Court,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(validators=[MinValueValidator(0),
                                            MaxValueValidator(5),
                                            ])
    review = models.CharField(max_length=200)

    class Meta:
        unique_together = ('user', 'court')

    def __str__(self):
        return "%s review %s" % (self.user, self.court,)


class Shuttlecock(models.Model):
    name = models.CharField(max_length=30)
    count_per_unit = models.IntegerField(validators=[MinValueValidator(0), ])
    count = models.IntegerField(validators=[MinValueValidator(0), ])
    price = models.IntegerField(validators=[MinValueValidator(0), ])
    remaining = models.IntegerField()
    court = models.ForeignKey(
        Court,
        related_name='shuttlecocks',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Log(models.Model):
    user = models.ForeignKey(
        User,
        related_name='logs',
        on_delete=models.SET_NULL,
        null=True,
    )
    desc = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, )

    def __str__(self):
        try:
            return '%s: %s' % (self.user.username, self.desc,)
        except:
            return '<Deleted>: %s' % (self.desc,)


class Document(models.Model):
    url = models.URLField()
    user = models.ForeignKey(
        User,
        related_name='documents',
        on_delete=models.CASCADE,
    )
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, )

    def __str__(self):
        return '%s %s' % (self.user.username, self.url,)


class Image(models.Model):
    url = models.URLField()
    court = models.ForeignKey(
        Court,
        related_name='images',
        on_delete=models.CASCADE,
    )
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, )

    def __str__(self):
        return '%s %s' % (self.court.name, self.url,)


class RacketBooking(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='racket_bookings'
    )
    racket = models.ForeignKey(
        Racket,
        on_delete=models.CASCADE,
        related_name='racket_bookings'
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='racket_bookings'
    )
    reserve_date = models.DateTimeField(auto_now=True)
    price = models.IntegerField(validators=[MinValueValidator(0), ])
    day_of_the_week = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(6), ])
    start = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(47), ])
    end = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(47), ])
    
    
class ShuttlecockBooking(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shuttlecock_bookings'
    )
    shuttlecock = models.ForeignKey(
        Shuttlecock,
        on_delete=models.CASCADE,
        related_name='shuttlecock_bookings'
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='shuttlecock_bookings'
    )
    price = models.IntegerField(validators=[MinValueValidator(0), ])
    count = models.IntegerField(validators=[MinValueValidator(0), ])

