__author__ = 'kate'
from YAASProject.models import Auction, Bid
import models
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import PasswordInput


class UserRegisterForm(UserCreationForm):
    #A form that creates a user, with no privileges, from the given username and
    #password, email and optional FirstName and LastName
    email = forms.EmailField()
    firstname = forms.RegexField(max_length=30,required=False,
        regex=r'^[\w.@+-]+$',
        help_text=("Required. 30 characters or fewer. Letters, digits and "
                    "@/./+/-/_ only."),
        error_messages={
            'invalid': ("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    lastname = forms.RegexField(max_length=60, required=False,
        regex=r'^[\w.@+-]+$',
        help_text=("Required. 30 characters or fewer. Letters, digits and "
                    "@/./+/-/_ only."),
        error_messages={
            'invalid': ("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})

    class Meta:
        model = User
        fields = ("username","firstname", "lastname", "email",)

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.first_name = self.cleaned_data["firstname"]
        user.last_name = self.cleaned_data["lastname"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class EditUserAccountForm(forms.Form):
    firstname = forms.RegexField(max_length=30, required=False,
        regex=r'^[\w.@+-]+$',
                help_text=("Required. 30 characters or fewer. Letters, digits and "
                           "@/./+/-/_ only."),
                          error_messages={
        'invalid': ("This value may contain only letters, numbers and "
                    "@/./+/-/_ characters.")})
    lastname = forms.RegexField(max_length=60, required=False,
        regex=r'^[\w.@+-]+$',
        help_text=("Required. 30 characters or fewer. Letters, digits and "
                   "@/./+/-/_ only."),
        error_messages={
            'invalid': ("This value may contain only letters, numbers and "
                        "@/./+/-/_ characters.")})
    email = forms.EmailField(max_length=75, required=False)
    newpassword = forms.RegexField(widget=PasswordInput,
        max_length=128, required=False, regex=r'^[\w.@+-]+$',
        help_text=("Required. 30 characters or fewer. Letters, digits and "
                   "@/./+/-/_ only."),
        error_messages={
            'invalid': ("This value may contain only letters, numbers and "
                        "@/./+/-/_ characters.")})
    confirmation = forms.RegexField(widget=PasswordInput,
        max_length=128,required=False, regex=r'^[\w.@+-]+$',
        help_text=("Required. 30 characters or fewer. Letters, digits and "
                   "@/./+/-/_ only."),
        error_messages={
            'invalid': ("This value may contain only letters, numbers and "
                        "@/./+/-/_ characters.")})

class createAuction(forms.Form):
    title = forms.RegexField(min_length=1,max_length=50, required=True,
        regex=r'^[\w.@ +-]+$',
        help_text=("Required. 50 characters or fewer. Letters, digits and "
                   "@/./+/-/_ only."),
        error_messages={
            'invalid': ("This value may contain only letters, numbers and "
                        "@/./+/-/_ characters.")})
    description = forms.RegexField(widget=forms.Textarea(), required=True, min_length=1,
        regex=r'^[\w.,:;!?#$%*()@ +-]+$',
        help_text=("Letters, digits and "
                   "@/.,:;!?#$%*()/+/-/_ only."),
        error_messages={
            'invalid': ("This value may contain only letters, numbers and "
                        "@/.,:;!?#$%*()/+/-/_ characters.")})
    minprice=forms.DecimalField(min_value=0.01, decimal_places=2, required=True)

class confAuction(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)

class bidForm(forms.Form):
    price=forms.DecimalField(min_value=0.01, decimal_places=2)