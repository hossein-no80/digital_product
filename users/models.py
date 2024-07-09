import random
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core import validators
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, send_mail


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, phone_number, email, password, is_staff, is_superuser, **extra_fields):
        """
        creates and saves a user with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('Users must have an username')
        email = self.normalize_email(email)
        user = self.model(
            phone_number=phone_number, username=username, email=email,
            is_active=True, is_staff=is_staff, is_superuser=is_superuser, date_joined=now, **extra_fields)

        if not extra_fields.get('no_password'):
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_user(self, username=None, phone_number=None, email=None, password=None, **extra_fields):
        if username is None:
            if email:
                username = email.split('@', 1)[0]
            if phone_number:
                username = random.choice('abcdefghijklmnopqrstuvwxyz') + str(phone_number)[-7:]
            while User.objects.filter(username=username).exists():
                username += str(random.randint(10, 99))

        return self._create_user(username, phone_number, email, password,
                                 False, False, **extra_fields)

    def create_superuser(self, username, phone_number, email, password, **extra_fields):
        return self._create_user(username, phone_number, email, password, True,
                                 True, **extra_fields)

    def get_by_phone_number(self, phone_number):
        return self.get(**{"phone_number": phone_number})


class User(AbstractBaseUser, PermissionsMixin):

    DoseNotExist = None
    username = models.CharField(_('username'), max_length=30, unique=True,
                                help_text=_(
                                    'required. 30 characters or fewer starting with a letter. Letters, digits and '),

                                validators=[
                                    validators.RegexValidator(r'^[a-zA-Z][a-zA-Z0-9_\.]+$',
                                                             _('enter a valid username starting with a_z',
                                                               'this value my contain only letters, numbers and',
                                                               'and underscore characters'), 'invalid'),
                                ],
                                error_messages={
                                    'unique': _("A user with that username already exists."),
                                }
                                )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)
    phone_number = models.BigIntegerField(_('phone number'), blank=True, null=True,
                                          validators=[
                                              validators.RegexValidator(r'^989[0-3,9]\d{8}$',
                                              _('Enter a valid phone number'), 'invalid'),
                                          ],

                                          error_messages={'unique': _("A user with that phone number already exists."),
                                                          }
                                          )
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '))
    is_active = models.BooleanField(_('active'), default=True,
                                    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_seen = models.DateTimeField(_('last seen date'), default=timezone.now, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number']

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def is_loggedin_user(self):
        """
        Returns True if the has actually in with valid credentials.
        """
        return self.phone_number is not None or self.email is not None

    def save(self, *args, **kwargs):
        if self.email is not None and self.email.strip() == '':
            self.email = None
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nick_name = models.CharField(_('nick name'), max_length=150, blank=True)
    avatar = models.ImageField(_('avatar'), blank=True)
    birthday = models.DateField(_('birthday'), blank=True, null=True)
    gender = models.BooleanField(_('gender'), default=False, help_text=_(
        'female is false, male is true, null is unset'))
    province = models.ForeignKey(verbose_name=_('province'), to='Province', null=True,
                                 on_delete=models.SET_NULL, blank=True)
    # email = models.EmailField(_('email address'),blank = True)
    # phone_number = models.BigIntegerField(_('phone number'), max_length=30, blank=True, null=True,
    #                                       validators=[
    #
    #                                          validators.RegexValidator(r'^989[0-3,9]\d{8}$',
    #                                                                    _('Enter a valid phone number'), 'invalid'),
    #
    #                                      ],
    #                                      error_messages={
    #                                          'unique': _("A user with that phone number already exists."), }
    #                                      )

    class Meta:
        db_table = 'user_profile'
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    @property
    def get_first_name(self):
        return self.user.first_name

    @property
    def get_last_name(self):
        return self.user.last_name

    def get_nick_name(self):
        return self.nick_name if self.nick_name else self.user.username


class Device(models.Model):
    WEB = 1
    IOS = 2
    ANDROID = 3
    DEVICE_TYPES_CHOICES = (
        (WEB, 'Web'),
        (IOS, 'IOS'),
        (ANDROID, 'Android'),
    )

    user = models.ForeignKey(User, related_name='device', on_delete=models.CASCADE)
    device_uuid = models.UUIDField(_('Device UUID'), null=True)
    # notify_token = models.CharField(_('Notification token'), max_length=200, blank=True,
    #                                validators=[validators.RegexValidator(r'[a-z]|[A-z]|[0-9])\w+',
    #                                            _('notify token is not valid'),'invalid')])

    last_login = models.DateTimeField(_('last login date'), null=True)
    device_type = models.PositiveSmallIntegerField(_('device type'), choices=DEVICE_TYPES_CHOICES, default=ANDROID)
    device_os = models.CharField(_('device os'), max_length=20, blank=True)
    device_model = models.CharField(_('device model'), max_length=50, blank=True)
    app_version = models.CharField(_('app version'), max_length=20, blank=True)
    created_time = models.DateTimeField(_('created time'), auto_now_add=True)

    class Meta:
        db_table = 'user_device'
        verbose_name = _('device')
        verbose_name_plural = _('devices')
        unique_together = ('user', 'device_uuid')


class Province(models.Model):
    name = models.CharField(_('province'), max_length=150)
    is_valid = models.BooleanField(_('is valid'), default=True)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    def __str__(self):
        return self.name
