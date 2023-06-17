import requests
import json
# import related models here
from .models import CarDealer, DealerReview

from requests.auth import HTTPBasicAuth

from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    try:
        if "apikey" in kwargs:
            response = requests.get(url, headers={
                                    'Content-Type': 'application/json'}, params=kwargs, auth=HTTPBasicAuth("apikey", kwargs["apikey"]))
        else:
            response = requests.get(
                url, headers={'Content-Type': 'application/json'}, params=kwargs)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
    except Exception as e:
        print("Error ", e)
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(json_payload)
    print("POST from {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        print(json_data)
        return json_data
    except:
        print("Network exception occurred")

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    list_result = get_request(url)
    json_result = json.dumps(list_result)
    
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["body"]
        # For each dealer object
        for dealer in dealers:
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], 
                                    state=dealer_doc["state"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results


def get_dealer_from_cf_by_id(url, dealer_id):
    list_result = get_request(url, id=dealer_id)
    json_result = json.dumps(list_result)

    if json_result:
        dealer = json_result["body"][0]
        dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], 
                                state=dealer["state"], full_name=dealer["full_name"],
                               id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                               short_name=dealer["short_name"],
                               st=dealer["st"], zip=dealer["zip"])
    return dealer_obj

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    list_result = get_request(url, dealerId=dealer_id)
    json_result = json.dumps(list_result)

    if json_result:
        reviews = json_result["body"]
        for review in reviews:
            if review["purchase"]:
                review_obj = DealerReview(
                    dealership=review["dealership"],
                    name=review["name"],
                    purchase=review["purchase"],
                    review=review["review"],
                    purchase_date=review["purchase_date"],
                    car_make=review["car_make"],
                    car_model=review["car_model"],
                    car_year=review["car_year"],
                    sentiment=analyze_review_sentiments(review["review"]),
                    id=review['id']
                )
            else:
                review_obj = DealerReview(
                    dealership=review["dealership"],
                    name=review["name"],
                    purchase=review["purchase"],
                    review=review["review"],
                    purchase_date=None,
                    car_make=None,
                    car_model=None,
                    car_year=None,
                    sentiment=analyze_review_sentiments(review["review"]),
                    id=review['id']
                )
            results.append(review_obj)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealer_review):
    API_KEY = "f97jLxZ2HrYTU5DqXoG_NTAy-NUQn0pqI6CSataqCJBP"
    NLU_URL = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/05796233-06a3-4296-8436-b98c7ecbb0b9"
    authenticator = IAMAuthenticator(API_KEY)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-08-01', authenticator=authenticator)
    natural_language_understanding.set_service_url(NLU_URL)
    response = natural_language_understanding.analyze(text=dealer_review, features=Features(
        sentiment=SentimentOptions(targets=[dealer_review]))).get_result()
    label = json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']
    return(label)
