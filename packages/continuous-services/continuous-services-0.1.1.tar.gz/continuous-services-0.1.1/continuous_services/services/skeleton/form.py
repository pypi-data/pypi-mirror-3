from django import forms

# For documentation on Django forms see:
# https://docs.djangoproject.com/en/1.2/topics/forms/

class SkeletonForm(forms.Form):
    
    # The fields to be collected from the user. Each field will 
    # be available in build_complete() as follows:
    #    self.data["field_name"]
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)
    a_question = forms.BooleanField(initial=True, required=False, label="Send me lots of messages please")
    
    
    def clean_username(self):
        """An example of how to perform custom field validation
        
        Feel free to remove this method, it is just an example.
        """
        
        # Get the username value
        username = self.clean_data.get("username", "")
        
        # Make lower case
        username = username.lower()
        
        # Some additional validation check
        if username in ("admin", "administrator"):
            # Raise a ValidationError if the check failes
            # (this will be shown to the user)
            raise forms.ValidationError("You may not use the admin/administrator usernames. Sorry.")
        
        # Return the new lowercase username
        return username
        
    

