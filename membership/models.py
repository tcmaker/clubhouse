from django.db import models, DataError
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from localflavor.us.models import USStateField, USZipCodeField
from model_utils import FieldTracker
from django.contrib.auth.models import User

class Member(models.Model):
    # Basic Information
    given_name = models.CharField('Given Name', max_length=100)
    family_name = models.CharField('Family Name', max_length=100)
    email = models.EmailField('Email Address')
    member_since = models.DateField('Date Joined')
    membership = models.ForeignKey('Membership', on_delete=models.SET_NULL, blank=True, null=True)

    # Address
    address_street1 = models.CharField('Street Address', max_length=100)
    address_street2 = models.CharField('Street Address 2', max_length=100, blank=True, null=True)
    address_city = models.CharField('City', max_length=100)
    address_state = USStateField('State')
    address_zip = USZipCodeField('Zip Code')

    # Phone Info
    phone_number = PhoneNumberField()
    phone_can_receive_sms = models.BooleanField(null=False, default=False)

    # Emergency Contact Information
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = PhoneNumberField()

    # User account
    account = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)

    # Advanced

    # This tells use which fields have been modified so our custom save()
    # method can do less work.
    tracker = FieldTracker()

    def __str__(self):
        return ", ".join([self.family_name, self.given_name])


    def address_lines(self):
        ret = [self.address_street1]

        if self.address_street2:
            ret.append(self.address_street2)

        ret.append("%s %s, %s" % (
            self.address_city,
            self.address_state,
            self.address_zip))

        return ret




    # Are we allowed to add more members to the membership referenced by
    # `self.membership_id`? This is used to validate the model before save
    # and to raise an exception if someone attempts to save an invalid record
    def __membership_has_vacancies(self):
        # Newly-created contacts don't have a membership attached
        if self.membership == None:
            return True
        # Only households have a member limit.
        if self.membership.membership_type != 'HOUSEHOLD':
            return True
        # If we save this record, will the linked membership have more members
        # than is allowed?
        if Member.objects.filter(membership_id=self.membership_id).exclude(id=self.id).count() < Membership.MAXIMUM_HOUSEHOLD_MEMBERS:
            return True
        return False

    def clean(self):
        """
            This runs when the model is validated.
        """
        if not self.__membership_has_vacancies():
            raise ValidationError({
                'membership': 'A household cannot have more than two members.'
            })
        super().clean()

    # Split out of .save() for better legibility
    def __raise_error_if_membership_is_full(self):
        if not self.tracker.has_changed('membership_id'):
            return
        if not self.__membership_has_vacancies():
            raise DataError('A household cannot have more than two members.')

    # Override the default .save() to raise exception if membership has no
    # vacancies
    def save(self, *args, **kwargs):
        self.__raise_error_if_membership_is_full()
        super().save(*args, **kwargs)

class PaymentPlan(models.Model):
    stripe_plan_identifier = models.CharField(max_length=100, help_text="Don't change this.")
    name = models.CharField(max_length=30, help_text='This text will appear in member-facing forms, so pick clear and descriptive.')
    requires_setup_fee = models.BooleanField(default=True)
    sort_priority = models.IntegerField(default=100)

    def __str__(self):
        return self.name


class Discount(models.Model):
    stripe_coupon_identifier = models.CharField(max_length=100)
    name = models.CharField(max_length=30)
    description = models.TextField(help_text="Who qualifies for this discount, and what are its terms?")
    allow_family_memberships = models.BooleanField('Allow family memberships?', default=False)

    def __str__(self):
        return self.name

SIGNUP_PAYMENT_METHODS = [
    ('card', 'Credit Card'),
    ('paypal', 'PayPal'),
    ('offline', 'Cold, Hard Cash'),
]

PAYMENT_METHODS = SIGNUP_PAYMENT_METHODS + [
    ('ach', 'Direct Deposit')
]

class Membership(models.Model):
    """
        Represents either a household of one or more members or a special
        team of members, like a high school Robotics team.
    """
    MAXIMUM_HOUSEHOLD_MEMBERS = 2
    MEMBERSHIP_TYPES = [
        ('household', 'Household'),
        ('student_team', 'Student Team'),
    ]

    MEMBERSHIP_STATUSES = [
        ('incomplete', 'Incomplete'),
        ('active', 'Active'),
        ('incomplete_expired', 'Incomplete (Expired)'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('unpaid', 'Unpaid'),
    ]

    stripe_customer_identifier = models.CharField(max_length=100, blank=True, null=True)
    stripe_subscription_identifier = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(max_length=30, choices=MEMBERSHIP_STATUSES)
    membership_contact = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='administered_memberships')

    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.SET_NULL, blank=True, null=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, blank=True, null=True)
    membership_type = models.CharField(max_length=50, choices=MEMBERSHIP_TYPES)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    valid_through = models.DateField()

    # Team Fields
    team_name = models.CharField(max_length=40, blank=True,
        help_text='This value is ignored on Household memberships')
    org_help_text = "The school or organization to which team members belong"
    team_organization = models.CharField(max_length=40, blank=True,
        help_text="The school or organization to which team members belong")

    def __str__(self):
        if self.membership_type == 'household':
            return 'Household: ' + str(self.membership_contact)
        else:
            return self.team_name

    def __has_member_vacancies(self, member_to_ignore=None):
        # Non-Household memberships always have vacancies.
        if self.membership_type != 'HOUSEHOLD':
            return True

        # How many members are currently attached to the membership? If we
        # passed a `member_to_ignore` parameter, exclude them from the count.
        # That allows this function to be used during model validation of
        # `Member` objects.
        members = Member.objects.filter(membership_id=self.id)
        if member_to_ignore:
            members = members.exclude(id=member_to_ignore.id)
        member_count = members.count()

        if member_count >= self.MAXIMUM_HOUSEHOLD_MEMBERS:
            return False

        if self.discount:
            if not self.discount.allow_family_memberships:
                if member_count >= 1:
                    return False

        return True

    def eligible_for_discount(self):
        # This is America: everyone is eligible to pay full price
        if not self.discount:
            return True

        # Only households are eligible for discounts
        if self.membership_type != 'HOUSEHOLD':
            return False

        # Some discounts are incompatible with family memberships. If there
        # are already multiple people attached to your household membership,
        # you can't qualify for those discounts until you punt the extra
        # members.
        max_member_count = self.MAXIMUM_HOUSEHOLD_MEMBERS if self.discount.allow_family_memberships else 1
        return Member.objects.filter(membership_id=self.id).count() <= max_member_count

    def clean(self):
        errors = {}
        if not self.eligible_for_discount():
            errors['discount'] = 'Multiperson memberships are not eligible for this discount.'

        if self.membership_type != 'HOUSEHOLD':
            if not self.team_name:
                errors['team_name'] = 'This field is required on non-household memberships'
            if not self.team_organization:
                errors['team_organization'] = 'This field is required on non-household memberships'

        if errors:
            raise ValidationError(errors)

        super().clean()
