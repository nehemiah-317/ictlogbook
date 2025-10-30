from django import forms
from .models import ThermalRollRecord


class ThermalRollRecordForm(forms.ModelForm):
    """Form for creating and updating thermal roll records"""
    
    class Meta:
        model = ThermalRollRecord
        fields = ['vendor_name', 'cashier_owner_name', 'quantity', 
                  'phone_number', 'signature', 'notes']
        widgets = {
            'vendor_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter vendor/station name'
            }),
            'cashier_owner_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter contact person name'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter quantity',
                'min': '1'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter phone number'
            }),
            'signature': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Digital signature (optional)'
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
    
    def clean_quantity(self):
        """Validate quantity"""
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity < 1:
            raise forms.ValidationError('Quantity must be at least 1')
        return quantity
