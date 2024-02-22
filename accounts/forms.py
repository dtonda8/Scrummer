from django import forms as djangoforms
from django.contrib.auth import authenticate, forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class UserAuthForm(AuthenticationForm):
	"""Custom Form to log user in by email or username"""
	def clean(self):
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		
		if username and password:
			if '@' in username: # if "username" entered is actually an email:
				users = User.objects.filter(email=username)
				if len(users) == 1:
					self.user_cache = authenticate(username=users[0].username,
												   password=password)
			else: # If a regular username
				self.user_cache = authenticate(username=username,
										   password=password)
			if self.user_cache is None:
				raise forms.ValidationError(
					self.error_messages['invalid_login'],
					code='invalid_login',
					params={'username': self.username_field.verbose_name},
				)
			else:
				self.confirm_login_allowed(self.user_cache)
				
		return self.cleaned_data

# https://ordinarycoders.com/blog/article/django-user-register-login-logout
class UserRegisterForm(UserCreationForm):
	email = djangoforms.EmailField(required=True)

	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2')

	def save(self, commit=True):
		user = super(UserRegisterForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user
	

# class WeekNumberForm(forms.Form):
#     subfield = forms.CharField(label="Subfield")