from django import forms
from .models import SupportRecord


class SupportRecordForm(forms.ModelForm):
    """Form for creating and updating support records"""
    
    class Meta:
        model = SupportRecord
        fields = ['staff_name', 'staff_id', 'issue_reported', 'phone_number', 'status', 'notes']
        widgets = {
            'staff_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter staff name'
            }),
            'staff_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter staff ID'
            }),
            'issue_reported': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Describe the issue'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter phone number'
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
        help_texts = {
            'staff_name': 'Full name of the staff member',
            'staff_id': 'Staff identification number',
            'issue_reported': 'Detailed description of the problem',
            'phone_number': 'Contact number for follow-up',
            'status': 'Current status of the issue',
            'notes': 'Any additional information or resolution details',
        }
    
    def clean_phone_number(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone_number')
        if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise forms.ValidationError('Please enter a valid phone number')
        return phone
    
    def clean_staff_id(self):
        """Validate staff ID"""
        staff_id = self.cleaned_data.get('staff_id')
        if staff_id and len(staff_id) < 3:
            raise forms.ValidationError('Staff ID must be at least 3 characters')
        return staff_id
