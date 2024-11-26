import re
import requests
from bs4 import BeautifulSoup
import json

def extract_phone_numbers(soup):
    # Extract the text content from the HTML
        text = soup.get_text()

        # Regular expression pattern for phone numbers
        phone_pattern = re.compile(r'''
        # Optional +91 or 91 country code
        (\+91[\-\s]?|91[\-\s]?)?      # Country code (optional, with or without +)
        # Indian phone number with various groupings and optional spaces or separators
        (
            \d{3}[\-\s]?\d{3}[\-\s]?\d{4} | # 3-3-4 format
            \d{4}[\-\s]?\d{3}[\-\s]?\d{3} | # 4-3-3 format
            \d{2}[\-\s]?\d{8}               # 2-8 format
        )
        ''', re.VERBOSE)

        # Find all matching phone numbers
        phone_numbers = phone_pattern.findall(text)
        return phone_numbers




def full_phone_numbers_function(url):
    # Function to extract phone numbers from a given URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    phone_numbers = extract_phone_numbers(soup)
    
    inURLS = []

    # Extract contact links
    for link in soup.find_all('a', href=True):
        if 'contact' in link.text.lower():
            inURLS.append(link['href'])

    # Request each contact page and extract phone numbers
    for url in inURLS:
        try:
            # Make the request
            tempResponse = requests.get(url)
            tempResponse.raise_for_status()  # Check for request errors
            tempSoup = BeautifulSoup(tempResponse.text, 'html.parser')
            
            # Extract phone numbers
            temp_phone_numbers = extract_phone_numbers(tempSoup)
            phone_numbers.extend(temp_phone_numbers)
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")



    # Cleaned phone numbers list
    cleaned_phone_numbers = []

    for country_code, number in phone_numbers:
        # Remove hyphens and whitespace
        cleaned_number = number.replace('-', '').replace(' ', '')
        cleaned_phone_numbers.append((country_code.strip('-+'), cleaned_number))

    phone_numbers = cleaned_phone_numbers
    return phone_numbers

  