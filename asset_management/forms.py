from django import forms
from .models import AssetRecord


class AssetRecordForm(forms.ModelForm):
    """Form for creating and updating asset records"""
    
    class Meta:
        model = AssetRecord
        fields = ['staff_name', 'staff_id', 'problem_reported', 'asset_type', 
                  'division', 'phone_number', 'signature', 'status', 'notes']
        widgets = {
            'staff_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter staff name'
            }),
            'staff_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter staff ID'
            }),
            'problem_reported': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Describe the problem'
            }),
            'asset_type': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Laptop, Printer, Desktop'
            }),
            'division': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter department/division'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter phone number'
            }),
            'signature': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Digital signature (optional)'
            }),
            'status': forms.Select(attrs={
                'class': 'form-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Additional notes (optional)'
            }),
        }
    
    def clean_phone_number(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone_number')
        if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise forms.ValidationError('Please enter a valid phone number')
        return phone
