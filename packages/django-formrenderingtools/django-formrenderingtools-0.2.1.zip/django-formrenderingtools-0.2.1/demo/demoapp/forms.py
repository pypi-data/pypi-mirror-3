from django import forms
from django.utils.translation import ugettext_lazy as _


class FakeContactForm(forms.Form):
    """A sample contact form which never validates."""
    subject = forms.CharField(
        label=_('Subject'),
        max_length=100,
    )
    message = forms.CharField(
        label=_('Message'),
        widget=forms.Textarea()
    )
    sender_email = forms.EmailField(label=_('Sender email'))
    sender_nickname = forms.CharField(
        label=_('Sender nickname'),
        required=False,
    )
    cc_myself = forms.BooleanField(
        label=_('Copy to the sender'),
        required=False,
        help_text='Send a copy of the message to the sender.',
    )
    
    def clean(self):
        """This sample form never validates!"""
        raise forms.ValidationError('Sorry, this sample form never validates!')
