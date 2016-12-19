from django import forms


class CustomerForm(forms.Form):
    #  Might be ModelForm with User model.
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)


class SubscriptionForm(forms.Form):
    customer_id = forms.CharField(required=True)
    payment_method_nonce = forms.CharField(required=True)

