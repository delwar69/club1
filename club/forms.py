from django import forms
from .models import ClubMember
from PIL import Image
from django.core.exceptions import ValidationError
from django.utils import timezone
from io import BytesIO

class ClubMemberForm(forms.ModelForm):
    same_as_permanent = forms.BooleanField(required=False, label="Same as Permanent Address")

    class Meta:
        model = ClubMember
        fields = '__all__'  # Includes all fields from the model
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter designation'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter department'}),
            'joining_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'spouse_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter spouse name'}),
            'religion': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'permanent_address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter permanent address'}),
            'present_address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter present address'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mobile number'}),
            'phone_office': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter office phone number'}),
            'phone_residence': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter residence phone number'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'signature_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        permanent_address = cleaned_data.get('permanent_address')
        same_as_permanent = cleaned_data.get('same_as_permanent')
        present_address = cleaned_data.get('present_address')

        if same_as_permanent:  # If checkbox is checked, copy permanent address to present address
        # Only update present_address if it's not already filled out
            if not present_address:
                cleaned_data['present_address'] = permanent_address
        return cleaned_data


    # Custom validation for Date of Birth
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        joining_date = self.cleaned_data.get('joining_date')

        if date_of_birth is None:
            raise forms.ValidationError("Date of Birth is required.")

        if joining_date and (joining_date - date_of_birth).days < 18 * 365:
            raise forms.ValidationError("Date of Birth must be at least 18 years before the Joining Date.")

        return date_of_birth

    # Custom validation for Joining Date
    def clean_joining_date(self):
        joining_date = self.cleaned_data.get('joining_date')
        if joining_date is None:
            raise forms.ValidationError("Joining Date is required.")

        if joining_date > timezone.now().date():
            raise forms.ValidationError("Joining Date cannot be in the future.")
        
        return joining_date

    # Validation for profile_picture dimensions
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            try:
                image = Image.open(profile_picture)
                if image.size != (300, 300):
                    raise forms.ValidationError("Profile picture should be 300x300 pixels.")
            except FileNotFoundError:
                raise forms.ValidationError("The uploaded file could not be opened.")
        return profile_picture

    # Validation for signature_image dimensions
    def clean_signature_image(self):
        signature_image = self.cleaned_data.get('signature_image')
        if signature_image:
            try:
            # If signature_image is uploaded, open the image using the file object
                image = Image.open(signature_image)
                if image.size != (300, 80):  # Validate the size
                    raise forms.ValidationError("Signature image should be 300x80 pixels.")
            except Exception as e:
                raise forms.ValidationError(f"Error opening signature image: {e}")
        return signature_image