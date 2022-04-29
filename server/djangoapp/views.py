from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .restapis import get_dealers_from_cf, get_dealers_from_cf_state, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

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
    print("Log out the user `{}`".format(request.user.username))
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
def get_dealerships(request):
    if request.method == "GET":
        state = request.GET.get("state", None)
        if state:
            url = "https://43edf790.eu-gb.apigw.appdomain.cloud/api/dealership?state={}".format(state)
            dealerships = get_dealers_from_cf_state(url)
        else:
            url = "https://43edf790.eu-gb.apigw.appdomain.cloud/api/dealership"
            dealerships = get_dealers_from_cf(url)
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        return HttpResponse(dealer_names)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://43edf790.eu-gb.apigw.appdomain.cloud/api/review?dealerId={}".format(dealer_id)
        reviews = get_dealer_reviews_from_cf(url)
        review_data = ' '.join([review.sentiment for review in reviews])
        return HttpResponse(review_data)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    #print(dealer_id)
    context = {}
    urldealer = "https://43edf790.eu-gb.apigw.appdomain.cloud/api/review?dealerId={}".format(dealer_id)
    detail = get_dealer_reviews_from_cf(urldealer)
    context["detail"] = detail
    context["cars"] = CarModel.objects.all()
    if request.method == 'GET':
        return render(request, 'djangoapp/add_review.html', context)
    
    if request.method == 'POST':
        
        car = get_object_or_404(CarModel, pk=request.POST["car"])
        review = {}
        review["name"] = request.user.username
        review["time"] = datetime.utcnow().isoformat()
        review["dealership"] = int(dealer_id)
        review["review"] = request.POST["content"]
        review["purchase"] = request.POST.get("purchasecheck", False)
        print("check value", review["purchase"])
        if review["purchase"]:
            review["purchase"] = True
            review["car_make"] = car.make_model.make
            review["car_model"] = car.name
            review["car_year"] = car.year.strftime("%Y")
            review["purchase_date"] = request.POST["purchasedate"]

        json_payload = json.dumps(review)
        print(json_payload)
        url = "https://43edf790.eu-gb.apigw.appdomain.cloud/api/add_review"
        post_request(url, json_payload)

        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)