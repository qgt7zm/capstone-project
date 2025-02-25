"""
Forms for myapp application.
"""

from django import forms


class UploadDataForm(forms.Form):
    # Upload JSON file containing models
    # Source: https://docs.djangoproject.com/en/5.1/topics/http/file-uploads/
    file = forms.FileField(required=True)

    def clean(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise forms.ValidationError("Please upload a file.")
        else:
            file_extension = file.name.split('.')[-1].lower()
            if file_extension != 'json':
                raise forms.ValidationError("Please upload a .json file.")
        return file
