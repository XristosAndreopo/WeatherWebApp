# File: weather/forms.py

"""
weather/forms.py

Django form definitions:
  - LocationSearchForm: encapsulates city & optional country inputs
    for both “Find by Location” and “Map” pages.
"""

from django import forms

class LocationSearchForm(forms.Form):
    """
    A simple search form for city & optional country code.
    - city: required CharField(max_length=100)
    - country: optional CharField(max_length=10)
    """
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. London'
        })
    )
    country = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. GB'
        })
    )
