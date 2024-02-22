from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms

admin.site.unregister(User)

class CustomUserCreationForm(UserCreationForm):
    """
    CustomUserCreationForm
    - Creates randomly generated password for user creation
    - Denies usernames with "@" (to avoid confusion with emails)
    """

    email = forms.EmailField(required=True) # Admin required to create new email for users

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = "Required. 150 characters or fewer. Letters, digits and ./+/-/_ only"
        self.fields['password1'].help_text += f"Randomly generated password: {User.objects.make_random_password(length=10)}"
    

    class Meta:
        model = User
        fields = ('username', 'email',)

   
    def clean_username(self):
        """Reject usernames that differ only in case."""
        username = self.cleaned_data.get("username")
        if (username and 
            self._meta.model.objects.filter(username__iexact=username).exists()): # Raise error if user already exists 

            self._update_errors(
                ValidationError(
                    {
                        "username": self.instance.unique_error_message(
                            self._meta.model, ["username"]
                        )
                    }
                )
            )

        elif username and "@" in username:  # Prevent usernames that contain "@"
            self._update_errors(ValidationError({"username": "@ Symbol not allowed"}))
        else:
            return username
        

class CustomUserAdmin(UserAdmin):
    """Custom User Admin uses new Form and requests for email for user creation"""
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
        ),
    )

admin.site.register(User, CustomUserAdmin)