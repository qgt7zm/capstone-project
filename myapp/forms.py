"""
Forms for myapp application.
"""

from django import forms


class UploadDataForm(forms.Form):
    # Upload JSON file containing models
    # Source: https://docs.djangoproject.com/en/5.1/topics/http/file-uploads/
    confirm_upload = forms.CharField(widget=forms.CheckboxInput())
    file = forms.FileField(required=True)

    def clean(self):
        confirm_upload = self.cleaned_data.get("confirm_upload")
        if not confirm_upload:
            raise forms.ValidationError("Please confirm upload.")

        file = self.cleaned_data.get("file")
        if not file:
            raise forms.ValidationError("Please upload a file.")
        else:
            file_extension = file.name.split('.')[-1].lower()
            if file_extension != 'json':
                raise forms.ValidationError("Please upload a .json file.")
        return file


class DeleteDataForm(forms.Form):
    # Delete models from database
    confirm_delete = forms.CharField(widget=forms.CheckboxInput())

    def clean(self):
        confirm_delete = self.cleaned_data.get("confirm_delete")
        if not confirm_delete:
            raise forms.ValidationError("Please confirm delete.")
        return confirm_delete
