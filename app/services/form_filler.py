import requests
from app.core.config import settings

def fill_form(extracted_data):
    """
    Fill out the form with extracted data.

    Args:
        extracted_data: Dictionary containing extracted data

    Returns:
        bool: True if form was filled successfully, False otherwise
    """
    form_url = settings.FORM_URL
    print(f"Form URL is {form_url}")

    try:
        response = requests.post(
            form_url,
            json=extracted_data,  # Or use `data=extracted_data` if it's a form-urlencoded endpoint
            timeout=10
        )
        response.raise_for_status()  # Raise exception for 4xx/5xx errors

        return True
    except requests.RequestException as e:
        print(f"Error submitting form: {e}")
        return False
