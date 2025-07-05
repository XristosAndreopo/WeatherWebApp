# File: weather/forms.py

"""
weather/forms.py

Django form definitions for the WeatherWebApp.

Responsibilities:
  • Encapsulate user input for searching weather by city (and optional country).
  • Provide consistent styling via shared widget attributes.
  • Validate and normalize inputs (e.g. uppercase ISO country codes).
"""

from django import forms

# ───────────────────────────────────────────────────────────────────────────────
# Shared widget attributes
# ───────────────────────────────────────────────────────────────────────────────
COMMON_TEXT_INPUT_ATTRS = {
    'class': 'form-control',
    'autocomplete': 'off',
}

# ───────────────────────────────────────────────────────────────────────────────
# LocationSearchForm
# ───────────────────────────────────────────────────────────────────────────────
class LocationSearchForm(forms.Form):
    """
    A simple search form to look up weather by city name and optional country code.

    Fields:
      - city   (required): Name of the city to search for.
      - country (optional): ISO 2‑letter country code (e.g. "US", "GB").
    """

    city = forms.CharField(
        label="City",
        max_length=100,
        required=True,
        help_text="Enter the name of the city, e.g. 'London'.",
        widget=forms.TextInput(attrs={
            **COMMON_TEXT_INPUT_ATTRS,
            'placeholder': 'e.g. London',
        })
    )
    country = forms.CharField(
        label="Country (optional)",
        max_length=2,
        required=False,
        help_text="Optional ISO 2‑letter country code, e.g. 'GB'.",
        widget=forms.TextInput(attrs={
            **COMMON_TEXT_INPUT_ATTRS,
            'placeholder': 'e.g. GB',
        })
    )

    def clean_country(self) -> str:
        """
        Normalize the country code to uppercase and validate length.
        Raises ValidationError if provided but not exactly 2 letters.
        """
        country = self.cleaned_data.get('country', '').strip().upper()
        if country and len(country) != 2:
            raise forms.ValidationError(
                "Country code must be exactly 2 letters (ISO 2‑letter code)."
            )
        return country
