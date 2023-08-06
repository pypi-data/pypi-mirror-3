from django import forms

class JabberForm(forms.Form):
    jid = forms.EmailField(max_length=100, help_text="The Jabber address to send to (e.g. joesmith@gmail.com)", label="Jabber email/ID")
    errors_only = forms.BooleanField(label="Errors & failures only", required=False)

