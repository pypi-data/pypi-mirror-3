"""
Forms used for the IX OpenID integration

.. moduleauthor:: Infoxchange Development Team <development@infoxchange.net.au>
"""
from django import forms

from django.contrib.auth.models import User


class IXOpenIDUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username
    and password.
    """
    username = forms.RegexField(label="Username", max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text="Required. 30 characters or fewer. Letters, " +
                    "digits and @/./+/-/_ only.",
        error_messages={'invalid': "This value may contain only letters, " +
                    "numbers and @/./+/-/_ characters."})

    #
    # pylint:disable=W0232,R0903
    # (metadata class does not need __init__ or public methods)
    #
    class Meta:
        """
        Form metadata
        """
        model = User
        fields = ("username",)

    def clean_username(self):
        """
        username validator. check that the username does not already exist
        """
        username = self.cleaned_data["username"]
        #
        # pylint:disable=E1101
        # (User does have DoesNotExist as a member through ModelBase but pylint
        # can't see it through Django magic)
        #
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("A user with that username already " +
            "exists.")

    def save(self, commit=True):
        user = super(IXOpenIDUserCreationForm, self).save(commit=False)
        user.set_password(None)
        if commit:
            user.save()
        return user
