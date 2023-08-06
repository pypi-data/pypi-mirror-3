from django import forms

class EmailForm(forms.Form):
    email_address = forms.EmailField(max_length=200)
    
    email_broken_fixed = forms.BooleanField(initial=True, required=False, label="Email this address when the project breaks or is fixed")
    email_every_failure = forms.BooleanField(initial=True, required=False, label="Email this address every time the project fails")
    email_every_success = forms.BooleanField(initial=False, required=False, label="Email this address every time the project passes")

