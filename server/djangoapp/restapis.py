import requests
import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions, KeywordsOptions
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger(__name__)

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    logger.info("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        logger.error("Network exception occurred")
    status_code = response.status_code
    logger.info("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    logger.info("POST to {} ".format(url))
    try:
        response = requests.post(url, json_payload, headers={'Content-Type': 'application/json'})
    except Exception as e:
        logger.error("Error", e)
    logger.info("Status Code ", {response.status_code})
    data = json.loads(response.text)
    logger.info('data', data)
    return data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result['body']['data']["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

def get_dealers_from_cf_id(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result['body']['data']["docs"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    logger.info(url)
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        logger.info(json_result)
        reviews = json_result['body']['data']["docs"]
        # For each dealer object
        for review in reviews:
            # Get its content in `doc` object
            if review["purchase"] == True:
                review_obj = DealerReview(dealership=review["dealership"], name=review["name"], purchase=review["purchase"], review=review["review"],
                                    purchase_date=review["purchase_date"], car_make=review["car_make"], car_model=review["car_model"],
                                    car_year=review["car_year"],
                                    sentiment=analyze_review_sentiments(review["review"]), id=review["id"])
            else:
                review_obj = DealerReview(dealership=review["dealership"], name=review["name"], purchase=review["purchase"], review=review["review"],
                                    purchase_date="", car_make="", car_model="",
                                    car_year="",
                                    sentiment=analyze_review_sentiments(review["review"]), id=review["id"])
            results.append(review_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview, **kwargs):
    url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/cb2aefd9-d5a2-47a6-a264-f828a89c948d"
    apikey = "sr-0-z-CoiQ1TxicjNzLsFwoCR6tEbzzuQxktT9BJBDW"

    authenticator = IAMAuthenticator(apikey)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2022-04-07',
    authenticator=authenticator
    )

    natural_language_understanding.set_service_url(url)
    try:
        response = natural_language_understanding.analyze(
            text=dealerreview,
            features=Features(sentiment=SentimentOptions())).get_result()
        sentiment = response["sentiment"]["document"]["label"]
    except:  
        sentiment = "Data too low for analysis"      
    # - Get the returned sentiment label such as Positive or Negative
    logger.info(sentiment)
    #print(json.dumps(response, indent=2))
    return sentiment