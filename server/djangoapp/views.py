from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealers_from_cf_id, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import random

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def get_about_page(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def get_contact_page(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact_us.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    logger.info("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request, dealar_id=None):
    if request.method == "GET":
        context={}
        url = "https://c266971e.eu-gb.apigw.appdomain.cloud/api/dealership"
        dealerships = get_dealers_from_cf(url)
        context["dealers"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context={}
        url = "https://c266971e.eu-gb.apigw.appdomain.cloud/api/review?dealerId={}".format(dealer_id)
        reviews = get_dealer_reviews_from_cf(url)
        dealer_url = "https://c266971e.eu-gb.apigw.appdomain.cloud/api/dealership?dealerId={}".format(dealer_id)
        dealer_detail = get_dealers_from_cf_id(dealer_url)
        context["reviews"] = reviews
        context["detail"] = dealer_detail[0]
        logger.info('delear_reviews', [ele.name for ele in reviews])
        return render(request, 'djangoapp/dealer_details.html', context)
        
# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    #logger.info(dealer_id)
    context = {}
    urldealer = "https://c266971e.eu-gb.apigw.appdomain.cloud/api/dealership?dealerId={}".format(dealer_id)
    logger.info(urldealer)
    detail = get_dealers_from_cf_id(urldealer)
    logger.info(detail[0])
    context["detail"] = detail[0]
    context["cars"] = CarModel.objects.all()
    if request.method == 'GET':
        return render(request, 'djangoapp/add_review.html', context)
    
    if request.method == 'POST':
        
        car = get_object_or_404(CarModel, pk=request.POST["car"])
        logger.info("car",car)
        final_json = {}
        review = {}
        review["id"] = random.randint(1111,9999)
        review["name"] = request.user.username
        review["dealership"] = int(dealer_id)
        review["review"] = request.POST["content"]
        review["purchase"] = request.POST.get("purchasecheck", False)
        logger.info("check value", review["purchase"])
        if review["purchase"]:
            review["purchase"] = True
            review["car_make"] = car.carmake.name
            review["car_model"] = car.name
            review["car_year"] = car.year.strftime("%Y")
            review["another"] = "field"
            review["purchase_date"] = request.POST["purchasedate"]
        else:
            review["purchase"] = False
            review["car_make"] = ""
            review["car_model"] = ""
            review["car_year"] = ""
            review["another"] = "field"
            review["purchase_date"] = ""
        final_json['review'] = review

        json_payload = json.dumps(final_json)
        # logger.info(json_payload)
        url = "https://c266971e.eu-gb.apigw.appdomain.cloud/api/add_review"
        post_request(url, json_payload)

        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)