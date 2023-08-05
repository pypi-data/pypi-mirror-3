from unittest import TestCase
from django_authenticator.forms import LoginForm
from django_authenticator.conf import settings

class LoginFormTests(TestCase):

    def test_fail_change_to_short_password(self):
        new_pass = '1'
        data = {
            'login_provider_name': 'local',
            'password_action': 'change_password',
            'new_password': new_pass,
            'new_password_retyped': new_pass
        }
        assert(len(new_pass) < settings.PASSWORD_MIN_LENGTH)
        form = LoginForm(data)
        result = form.is_valid()
        #print form.errors
        self.assertFalse(result)
        self.assertEquals(form.initial['new_password'], None)
        #self.assertFalse('new_password_retyped' in form.cleaned_data)

