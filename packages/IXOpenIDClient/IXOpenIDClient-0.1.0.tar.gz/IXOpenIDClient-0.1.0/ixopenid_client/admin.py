"""
Hooks for the django admin interface for more intuitive IX OpenID
integration

.. moduleauthor:: Infoxchange Development Team <development@infoxchange.net.au>
"""
from ixopenid_client.forms import IXOpenIDUserCreationForm

from django.conf import settings
from django.db.models.signals import post_save

from django.contrib.auth.models import User
from django_openid_auth.models import UserOpenID

from django.contrib.auth.admin import UserAdmin

from django.core.exceptions import ImproperlyConfigured


def test_settings():
    """
    Check that application settings needed for the integration have been set
    """
    if not settings.OPENID_SSO_SERVER_PROFILE_ROOT:
        raise ImproperlyConfigured("No profile root in settings")
    if settings.OPENID_CREATE_USERS:
        raise ImproperlyConfigured("OPENID_SSO_IXLOGIN option can't be " +
                                   "with OPENID_CREATE_USERS option")


#
# pylint:disable=W0613
# (sender and **kwargs are not used but must be declared as arguments for
# signal receivers)
#
def create_profile_server_id(sender, instance, created, **kwargs):
    """
    User hook to create a user open id when a user is created
    """
    if created:
        oid_root = settings.OPENID_SSO_SERVER_PROFILE_ROOT
        username = instance.username
        oid_url = oid_root + username
        print "oid_url: %s" % oid_url
        user_oid = UserOpenID(user=instance, claimed_id=oid_url,
                              display_id=oid_url)
        user_oid.save()


if settings.OPENID_SSO_IXPROFILES:
    # Make sure the app is configured properly
    test_settings()

    #
    # Hook onto the user so we can automatically deal with their ixlogin
    # OpenID profile
    #
    post_save.connect(create_profile_server_id, sender=User)

    #
    # Users logging in with ixlogin OpenID don't need local passwords so
    # override stuff to remove that functionality from user forms. django
    # isn't exactly clean with this stuff so this gets a bit messy
    #
    # 1. This is just layout info for the form. Overriding it to remove the
    # password fields. Not enough as the view will still try to process them
    #
    UserAdmin.add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username',)}
        ),
    )
    UserAdmin.fieldsets = (
        (None, {'fields': ('username',)}),
        ('Personal info from IX OpenID. ' +
           '(Not available until user login)', {'fields': ('first_name',
           'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
           'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Groups', {'fields': ('groups',)}),
    )
    UserAdmin.readonly_fields = ('first_name', 'last_name', 'email')
    #
    # 2. Use our alternate user add_form (template). It would have been nice
    # to manipulate the existing one in admin but that has (now inappropriate)
    # instructions hardcoded in it #@!#@!
    #
    UserAdmin.add_form_template = 'ixopenid_user_add_form.html'
    #
    # 3. Finally the view so it doesn't try to validate password fields and
    # sets user passwords to unusable password
    #
    UserAdmin.add_form = IXOpenIDUserCreationForm
