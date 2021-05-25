from django.db import models

from accounts.models import User

DEPARTMENT_TRAINING_TIERS = [
    ('NONE', 'No special training requirements'),
    ('SOME', 'Some training required'),
    ('PER_TOOL', 'Must demonstrate tool proficiency'),
    ('ORIENTATION_REQUIRED', 'Area Orientation is mandatory'),
]

class Department(models.Model):
    name = models.CharField('Department Name', max_length=50, null=False, blank=False)
    slug = models.SlugField('URL Slug', max_length=50, null=False, blank=False)
    area_manager = models.ForeignKey(User, related_name='department_area_manager', on_delete=models.SET_NULL, blank=True, null=True)
    secondary_area_managers = models.ManyToManyField(User)
    shop_contact_email = models.EmailField(max_length=50, null=True, blank=True)
    stripe_donation_product_identifier = models.CharField('Stripe product identifier for donations', max_length=50, blank=False, null=False)

    # Attractive Visuals
    map = models.FileField(max_length=100, blank=True, null=True, help_text="This should be an SVG file with an approximate 4:3 aspect ratio.")
    photo = models.ImageField(max_length=100, blank=True, null=True, help_text="Any image file with a 4:3 aspect ratio will work.")

    # Temporary, until more elaborate training requirements are developed
    training_tier = models.CharField(
        'Training Tier',
        max_length=50,
        choices=DEPARTMENT_TRAINING_TIERS,
        blank=False,
        null=False,
        default=DEPARTMENT_TRAINING_TIERS[0][0]
    )

    def __str__(self):
        return self.name

    def all_area_managers(self):
        ret = [self.area_manager]
        ret += self.secondary_area_managers.order_by('last_name').all()
        return ret

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('workshop:department_detail', args=[self.slug])

class Area(models.Model):
    name = models.CharField('Area Name', max_length=50, null=False, blank=False)
    covid19_capacity = models.PositiveIntegerField('Maximum Concurrent Users')
    area_manager = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    shop_contact_email = models.EmailField(max_length=50, null=True, blank=True)
    is_exempt_from_member_timeslot_quota = models.BooleanField("Reservations in this area do not count against a member's daily quota.", null=False, default=False)

    def __str__(self):
        return self.name
