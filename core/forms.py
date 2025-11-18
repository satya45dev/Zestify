from django import forms
from django.contrib.auth.models import User # <-- NEW IMPORT: Required for AccountSettingsForm
from .models import Address, SavedCard, SavedUPI 

# --- 1. CONSTANT: List of Indian States ---
INDIAN_STATES_AND_UTS = (
    ('', '--Select State--'),
    ('AP', 'Andhra Pradesh'),
    ('AR', 'Arunachal Pradesh'),
    ('AS', 'Assam'),
    ('BR', 'Bihar'),
    ('CT', 'Chhattisgarh'),
    ('GA', 'Goa'),
    ('GJ', 'Gujarat'),
    ('HR', 'Haryana'),
    ('HP', 'Himachal Pradesh'),
    ('JH', 'Jharkhand'),
    ('KA', 'Karnataka'),
    ('KL', 'Kerala'),
    ('MP', 'Madhya Pradesh'),
    ('MH', 'Maharashtra'),
    ('MN', 'Manipur'),
    ('ML', 'Meghalaya'),
    ('MZ', 'Mizoram'),
    ('NL', 'Nagaland'),
    ('OR', 'Odisha'),
    ('PB', 'Punjab'),
    ('RJ', 'Rajasthan'),
    ('SK', 'Sikkim'),
    ('TN', 'Tamil Nadu'),
    ('TS', 'Telangana'),
    ('TR', 'Tripura'),
    ('UP', 'Uttar Pradesh'),
    ('UK', 'Uttarakhand'),
    ('WB', 'West Bengal'),
    ('AN', 'Andaman and Nicobar Islands'),
    ('CH', 'Chandigarh'),
    ('DD', 'Dadra and Nagar Haveli and Daman and Diu'),
    ('DL', 'Delhi'),
    ('JK', 'Jammu and Kashmir'),
    ('LA', 'Ladakh'),
    ('LD', 'Lakshadweep'),
    ('PY', 'Puducherry'),
)


# --- 2. MODEL FORM: AddressForm ---
class AddressForm(forms.ModelForm):
    state = forms.ChoiceField(
        choices=INDIAN_STATES_AND_UTS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    address_type = forms.ChoiceField(
        choices=[('Home', 'Home'), ('Work', 'Work')],
        widget=forms.RadioSelect,
        initial='Home'
    )
    
    phone_number = forms.CharField(label='10-digit mobile number', max_length=15)
    
    class Meta:
        model = Address
        fields = [
            'full_name', 'phone_number', 'zip_code', 'address_line_2', 
            'address_line_1', 'city', 'state', 'country', 'address_type',
        ]
        
        labels = {
            'full_name': 'Name',
            'zip_code': 'Pincode',
            'address_line_2': 'Locality',
            'address_line_1': 'Address (Area and Street)',
            'city': 'City/District/Town',
            'country': 'Country',
        }
        
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_1': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.HiddenInput(),
        }


# --- 3. MODEL FORM: AddCardForm ---
class AddCardForm(forms.ModelForm):
    full_card_number = forms.CharField(label='Card Number', max_length=16, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 16-digit card number', 'minlength': '16', 'maxlength': '16'})
    )
    cvv = forms.CharField(label='CVV', max_length=4, 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'CVV', 'minlength': '3', 'maxlength': '4'})
    )

    class Meta:
        model = SavedCard
        fields = ['card_holder_name', 'expiry_month', 'expiry_year', 'card_type'] 
        widgets = {
            'card_holder_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name on Card'}),
            'card_type': forms.HiddenInput(),
            'expiry_month': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM', 'maxlength': '2'}),
            'expiry_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'YYYY', 'maxlength': '4'}),
        }


# --- 4. MODEL FORM: AddUPIForm ---
class AddUPIForm(forms.ModelForm):
    class Meta:
        model = SavedUPI
        fields = ['upi_id']
        widgets = {
            'upi_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., user@bankname'}),
        }
        
# --- 5. MODEL FORM: AccountSettingsForm ---
class AccountSettingsForm(forms.ModelForm):
    """Form to allow users to update their core profile details."""

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': 'Username (Cannot be easily changed)',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }