import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import pytesseract
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from urllib.parse import urljoin
import base64
import nltk
from nltk.corpus import words as wrds
import json
import spacy
import numpy as np

extractedTexts = []
# Function to extract text from a normal image URL
def text_extract_normal(img_url):
    session = requests.Session()
    
    # Retry strategy for robust requests
    retry_strategy = Retry(
        total=5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        img_response = session.get(img_url)
        img_response.raise_for_status()
        
        # Open and process the image
        img = Image.open(BytesIO(img_response.content))
        text = pytesseract.image_to_string(img)
        extractedTexts.append(text)
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Error processing image: {e}")

# Function to extract text from base64-encoded images
def text_extract_data(img):
    extracted_text = pytesseract.image_to_string(img)
    extractedTexts.append(extracted_text)

def split_words_by_dict(words, valid_words):
    result = []
    
    for word in words:
        if(word in valid_words):
            result.append(word)
        else:
            found_split = False
            
            # Try to split the word at every possible position
            for i in range(1, len(word)):
                left, right = word[:i], word[i:]
                
                # Check if both parts exist in the dictionary
                if left in valid_words and right in valid_words:
                    result.extend([left, right])
                    found_split = True
                    break
            
            # If no valid split is found, keep the word as it is
            if not found_split:
                result.append(word)
    return result
###############################################################################################################
def full_function(url, fradulent):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url  # Default to https if no scheme is provided

    

    # Step 1: Web scraping to get image URLs
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    image_tags = soup.find_all('img')

    # Step 2: Iterate over each image tag and process
    for i, img_tag in enumerate(image_tags, start=1):
        img_url = img_tag.get('src')
        
        # Handle relative URLs
        img_url = urljoin(url, img_url)
        
        # Check if the image is a base64-encoded data URL
        if img_url.startswith('data:image/'):
            header, encoded = img_url.split(',', 1)
            img_data = base64.b64decode(encoded)
            
            # Open and process the image
            img = Image.open(BytesIO(img_data))
            text_extract_data(img)
            
            # Save the image locally
            # img.save(f'downloaded_image{i}.png')
        
        else:
            # Process and download normal image URLs
            text_extract_normal(img_url)
            
            # Download and save the image
            # img_response = requests.get(img_url)
            # if img_response.status_code == 200:
            #     img = Image.open(BytesIO(img_response.content))
            #     img.save(f'downloaded_image{i}.png')
            # else:
            #     print(f'Failed to download image: {img_url}')

    # Step 3: Tokenize extracted text
    words = []
    for text in extractedTexts:
        words.extend(word.lower().strip('|@#$%^&*()?/.-_') for word in text.split())

    valid_words_dict = set(wrds.words())

    words = split_words_by_dict(words, valid_words_dict)

    # here , words contains all words extracted from images of the website

    # now extracting the website text

    text = soup.get_text()

    # Step 4: Split the text into individual words and store in an array
    words_array = text.split()

    words.extend(words_array)

    helping_words = [
        "a", "about", "above", "after", "again", "against", "all", "am", 
        "an", "and", "any", "are", "as", "at", "be", "because", "been", 
        "before", "being", "below", "between", "both", "but", "by", 
        "can", "could", "did", "do", "does", "either", "for", "from", 
        "further", "had", "has", "have", "he", "her", "here", "him", 
        "his", "if", "in", "into", "is", "it", "its", "just", "like", 
        "may", "me", "might", "more", "most", "must", "my", "no", 
        "not", "of", "off", "on", "once", "one", "only", "or", "other", 
        "our", "out", "over", "re", "same", "she", "should", "so", 
        "some", "such", "that", "the", "their", "them", "then", "there", 
        "these", "they", "this", "those", "through", "to", "too", 
        "under", "until", "up", "very", "was", "we", "were", "what", 
        "when", "where", "which", "while", "who", "whom", "why", 
        "will", "with", "would", "yes", "yet", ""
    ]

    words = split_words_by_dict(words, valid_words_dict)

    preProcessing = []
    for word in words:
        word = word.lower().strip('|@#$%^&*()?/.-_')
        if ( (not word in helping_words) and (word.isalpha()) ):
            preProcessing.append(word.lower().strip('?./'))
    words = preProcessing




    #use of nlp in order to assess if the website is fraud


    # Load the array from the JSON file
    with open('data.json', 'r') as file:
        data = json.load(file)
    data = json.loads(data)
    fradulent_words = data['fradulent_words']

    nlp = spacy.load("en_core_web_md")
    # Join the words into a single string
    text = ' '.join(fradulent_words)
    # Process the text with SpaCy
    doc = nlp(text)

    # Extract tokens
    fradulent_tokens = [token for token in doc]

    text = ' '.join(set(words))
    doc = nlp(text)

    extracted_tokens = [token for token in doc]

    similarity_threshold = 0.35
    fradulent_matches_threshold = 0.20
    sus_word_frequency = 0

    addable_words = []

    no_match_count = [0] * len(fradulent_tokens)
    for exToken in extracted_tokens:
        matches_with_frTokens = 0
        for i in range(len(fradulent_tokens)):
            if(exToken.similarity(fradulent_tokens[i]) > similarity_threshold):
                # print(exToken.text + "-" + frToken.text + "-" + str(exToken.similarity(frToken)))
                matches_with_frTokens+=1
            else:
                no_match_count[i]+=1
                
        # print(str(matches_with_frTokens) + " " + str(exToken.text))
        if(matches_with_frTokens/len(fradulent_tokens) > fradulent_matches_threshold):
            sus_word_frequency+=1
        elif(matches_with_frTokens/len(fradulent_tokens) > fradulent_matches_threshold*0.95):
            addable_words.append(exToken.text)


    # Get the indices of the top three greatest values in no_match_count
    if len(no_match_count) >= 3:
        removable_words = np.argsort(no_match_count)[-3:]
        # removable_words = removable_words[np.argsort(no_match_count[removable_words])[::-1]]
        removable_words = sorted(removable_words, key=lambda x: no_match_count[x], reverse=True)
    else:
        removable_words = np.argsort(no_match_count)



    


    # print(sus_word_frequency)
    # Calculate probability
    total_extracted = len(extracted_tokens)
    probability_of_fraud = sus_word_frequency / total_extracted if total_extracted > 0 else 0
    print(probability_of_fraud)
    
    detected = (probability_of_fraud > 0.5)

    addable_words = sorted(addable_words, key=lambda x: x[1])

    
    

    if(fradulent and not detected):
        fradulent_words.extend(addable_words)
    if(not fradulent and detected):
        for index in removable_words:
            del fradulent_words[index]


    data_to_write = "{\n \"fradulent_words\" : ["
    first = True
    for word in fradulent_words:
        if(first):
            data_to_write+= "\""+word+"\""
            first=False
        else:
            data_to_write+=", \""+word+"\""
    data_to_write+="]\n}\n"

    with open('data.json', 'w') as json_file:
        json.dump(data_to_write, json_file, indent=4)

    return probability_of_fraud