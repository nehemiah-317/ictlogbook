from django import forms
from .models import VendorAssistance


class VendorAssistanceForm(forms.ModelForm):
    """Form for creating and updating vendor assistance records"""
    
    class Meta:
        model = VendorAssistance
        fields = ['company_name', 'cashier_owner_name', 'problem_reported', 
                  'phone_number', 'status', 'resolution_notes']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter company/vendor name'
            }),
            'cashier_owner_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter contact person name'
            }),
            'problem_reported': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Describe the problem'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter phone number'
            }),
            'status': forms.Select(attrs={
                'class': 'form-input'
            }),
            'resolution_notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Resolution details (optional)'
            }),
        }
    
    def clean_phone_number(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone_number')
        if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise forms.ValidationError('Please enter a valid phone number')
        return phone
