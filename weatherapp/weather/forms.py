# File: weather/forms.py

"""
weather/forms.py

Django form definitions used across views for searching locations:
  - LocationSearchForm: City + optional country input for search.
"""

from django import forms


class LocationSearchForm(forms.Form):
    """
    A simple form for users to input a city (required) and an optional country code.

    Fields:
        - city (str): Required input. Accepts up to 100 characters.
        - country (str): Optional input. Accepts up to 10 characters.

    Used in:
        - FindLocationView
        - MapView (client-side triggered)
    """
    city = forms.CharField(
        label='City',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. London'
        })
    )

    country = forms.CharField(
        label='Country Code (optional)',
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. GB'
        })
    )
