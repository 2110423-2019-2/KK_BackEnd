from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, \
    MinValueValidator, MaxValueValidator


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
        unique_together = ('base_user', )


class Court(models.Model):
    is_verified = models.BooleanField(default=False)
    price = models.IntegerField(validators=[MinValueValidator(0), ])
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courts',
    )
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
        return m_sum/len(reviews)


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
        return "%s review %s" % (self.user, self.court, )


class Racket(models.Model):
    name = models.CharField(max_length=30)
    count = models.IntegerField(validators=[MinValueValidator(0), ])
    price = models.IntegerField(validators=[MinValueValidator(0), ])
    court = models.ForeignKey(
        Court,
        related_name='rackets',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Shuttlecock(models.Model):
    name = models.CharField(max_length=30)
    count_per_unit = models.IntegerField(validators=[MinValueValidator(0), ])
    count = models.IntegerField(validators=[MinValueValidator(0), ])
    price = models.IntegerField(validators=[MinValueValidator(0), ])
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
        return '%s %s' % (self.user.username, self.desc, )


class Document(models.Model):
    url = models.URLField()
    user = models.ForeignKey(
        User,
        related_name='documents',
        on_delete=models.CASCADE,
    )
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, )

    def __str__(self):
        return '%s %s' % (self.user.username, self.url, )


class Image(models.Model):
    url = models.URLField()
    court = models.ForeignKey(
        Court,
        related_name='images',
        on_delete=models.CASCADE,
    )
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, )

    def __str__(self):
        return '%s %s' % (self.court.name, self.url, )