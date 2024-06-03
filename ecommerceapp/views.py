from http import client
from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Product,Contact,Orders,OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import  csrf_exempt
import razorpay
from Razorpay import Checksum
# from .razorpay_client import razorpay_client
# Create your views here.


# This line defines a function named home 
# which takes a request object as its parameter. In Django, views are Python functions that take a web request and return a web response.
def home(request):


    # This line retrieves the currently logged-in user from the request object. In Django, request.user represents the user associated with the current request.
    current_user = request.user
    # print(current_user)

    # This line initializes an empty list named allProds. This list will be used to store information about products.
    allProds = []


    # This line queries the database to retrieve values of
    #  the 'category' and 'id' fields from the 'Product' model. It seems like 'Product' is a Django model representing products in an e-commerce website.
    catprods = Product.objects.values('category','id')

    # This line creates a set (cats) containing unique category names extracted from the catprods queryset. It uses a set comprehension to iterate over catprods and collect unique category names.
    cats = {item['category'] for item in catprods}

    # This line starts a loop over each unique category retrieved in the previous step.
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)

        #  This line calculates the number of 
        # slides needed to display the products. It divides the total number of products by 4 and rounds up to the nearest integer using the ceil function from the math module.
        nSlides = n // 4 + ceil((n / 4) - (n // 4))

        # This line appends a list containing
        #  information about products, number of slides, and range of slide numbers to the allProds list. Each element appended represents a category and its corresponding products.
        allProds.append([prod, range(1, nSlides), nSlides])
    # This line creates a dictionary named params containing a key-value pair where the key is 'allProds' and the value is the allProds list created earlier.
    params= {'allProds':allProds}

    # This line renders the 'index.html' template with the parameters passed in the params dictionary. The template will use these parameters to display product information on the webpage.
    return render(request,'index.html',params)




def about(request):
    return render(request, 'about.html')


# This line defines a function named contactus which takes a request object as its parameter. This function handles the logic for displaying the contact form and processing form submissions.
def contactus(request):

    # This condition checks if the user is authenticated (logged in). If the user is not authenticated, it displays a warning message using Django's messages framework and redirects the user to the login page.
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/login')
    

    # This condition checks if the form is being submitted via the POST method.
    if request.method=="POST":

        # This line retrieves the value of the 'name' field from the POST data submitted by the form. If the field is not present in the POST data, it defaults to an empty string.
        name = request.POST.get('name', '')

        # This line retrieves the value of the 'email' field from the POST data.
        email = request.POST.get('email', '')

        # This line retrieves the value of the 'phone' field from the POST data.
        phone = request.POST.get('phone', '')


        # This line retrieves the value of the 'desc' (description) field from the POST data.
        desc = request.POST.get('desc', '')

        # This line creates a new Contact object
        # with the provided name, email, phone, and description. It seems like Contact is a model representing contact form submissions.
        contact = Contact(name=name, email=email, phone=phone, desc=desc)

        # This line saves the Contact object to the database.
        contact.save()

        # This line adds a success message to the Django messages framework, indicating that the contact form has been successfully submitted.
        messages.success(request,"Contact Form is Submitted")

    # This line renders the 'contactus.html' template. If the request method is not POST or if the user is not authenticated, this line is reached to display the contact form.
    return render(request, 'contactus.html')


# This line defines the view function tracker which takes a request object as its parameter.
def tracker(request):
    # This condition checks if the user is authenticated 
    # (logged in). If the user is not authenticated, it displays a warning message using Django's messages framework and redirects the user to the login page.
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/login')
    

    # This condition checks if the form is being submitted via the POST method.
    if request.method=="POST":

        # This line retrieves the value of the 'orderId' field from the POST data submitted by the form. If the field is not present in the POST data, it defaults to an empty string.
        orderId = request.POST.get('orderId', '')

        # This line retrieves the value of the 'email' field from the POST data.
        email = request.POST.get('email', '')

        # This block of code encapsulates the database query within a try-except block to handle any potential exceptions that may occur during the database query.
        try:

            # This line queries the database to retrieve an order matching the provided orderId and email. It seems like Orders is a model representing orders in the system.
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:


                # This line queries the database to retrieve all updates related to the order identified by orderId. It seems like OrderUpdate is a model representing updates associated with orders.
                update = OrderUpdate.objects.filter(order_id=orderId)

                # This line initializes an empty list to store update information.
                updates = []

                # This loop iterates over each update related to the order and appends its description and timestamp to the updates list.
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})

                    # This line converts the updates and order items to a JSON format using the json.dumps() function.
                    response = json.dumps([updates, order[0].items_json], default=str)

                    # This line returns an HTTP response containing the JSON-formatted data.
                return HttpResponse(response)
            else:

                # This line returns an empty JSON response if no matching order is found.
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')
    # This line renders the 'tracker.html' template if the request method is not POST or if the user is not authenticated.
    return render(request, 'tracker.html')




def productView(request, myid):
    # Fetch the product using the id
    product = Product.objects.filter(id=myid)


    return render(request, 'index.html', {'product':product[0]})



    
# The function checkout(request) is defined, which presumably is a view function
#  in a Django web application, handling the checkout process.
def checkout(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.warning(request, "Please login and try again")
        return redirect('/login')

    if request.method == "POST":
        # Retrieve form data
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        # Create an Order instance
        order = Orders(items_json=items_json, name=name, amount=amount, email=email, address1=address1,
                       address2=address2, city=city, state=state, zip_code=zip_code, phone=phone)
        order.save()

        # Create an OrderUpdate instance
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()

        # Generate Razorpay order
        order_amount = int(amount) * 100  # Convert to paisa (Razorpay expects amount in paisa)
        order_currency = 'INR'
        razorpay_order = client.order.create({
            'amount': order_amount,
            'currency': order_currency,
            'receipt': str(order.order_id),
            'notes': {
                'address': f"{address1}, {address2}, {city}, {state}, {zip_code}"
            },
        })

        # Callback URL (you should replace this with your actual callback URL)
         # Callback URL (you should replace this with your actual callback URL)
        callback_url = request.build_absolute_uri('/handlerequest/')
        print("Callback URL:", callback_url)

        # Retrieve Razorpay order ID
        razorpay_order_id = razorpay_order['id']

        context = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
            'razorpay_amount': order_amount,
            'currency': order_currency,
            'callback_url': callback_url,
        }

        # Redirect user to Razorpay checkout page
        return render(request, 'paytm.html', context)

    # If request method is not POST, render checkout.html
    return render(request, 'checkout.html')


@csrf_exempt
def Handlerequest(request):
    print("handlerequest view called")
    data = request.POST
   

    RESPONSE_CODE_SUCCESS = '01'
    RESPONSE_CODE_ORDER_NOT_FOUND = '404'
    RESPONSE_CODE_ERROR_PROCESSING_PAYMENT = '500'
    RESPONSE_MESSAGE_SUCCESS = 'Payment successful'
    RESPONSE_MESSAGE_ORDER_NOT_FOUND = 'Order not found'
    RESPONSE_MESSAGE_ERROR_PROCESSING_PAYMENT = 'Error processing payment'

    try:
        required_keys = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
        if not all(key in data for key in required_keys):
            raise ValueError('Missing required POST data')

        razorpay_order_id = data['razorpay_order_id']
        razorpay_payment_id = data['razorpay_payment_id']
        razorpay_signature = data['razorpay_signature']

        order = Orders.objects.get(order_id=razorpay_order_id)

        if not order:
            raise ValueError('Order not found')

        order.payment_id = razorpay_payment_id
        order.payment_status = 'PAID'
        order.save()

        # print(f"Payment successful for Order ID: {razorpay_order_id}. Amount: {order.amount}. Payment ID: {razorpay_payment_id}")

        response_dict = {
            'ORDERID': razorpay_order_id,
            'TXNAMOUNT': order.amount,
            'RESPCODE': RESPONSE_CODE_SUCCESS,
            'RESPMSG': RESPONSE_MESSAGE_SUCCESS,
        }

    except Orders.DoesNotExist:
        # print(f"Order ID {razorpay_order_id} does not exist in the database")
        response_dict = {
            'ORDERID': razorpay_order_id,
            'TXNAMOUNT': 0,
            'RESPCODE': RESPONSE_CODE_ORDER_NOT_FOUND,
            'RESPMSG': RESPONSE_MESSAGE_ORDER_NOT_FOUND,
        }

    except Exception as e:
        # print(f"Error processing payment: {str(e)}")
        response_dict = {
            'ORDERID': razorpay_order_id,
            'TXNAMOUNT': 0,
            'RESPCODE': RESPONSE_CODE_ERROR_PROCESSING_PAYMENT,
            'RESPMSG': RESPONSE_MESSAGE_ERROR_PROCESSING_PAYMENT,
        }

    # print(f"Response dict: {response_dict}")

    try:
        return render(request, 'status.html', {'response': response_dict})
    except Exception as e:
        print(f"Error rendering template: {str(e)}")
        return HttpResponseServerError()






      

# This line defines the view function handlelogin which takes a request object as its parameter.
def handlelogin(request):
      
    #   This condition checks if the request method is POST, indicating that a form has been submitted.
      if request.method == 'POST':
        # get parameters
        # This line retrieves the value of the 'email' field from the POST data submitted by the form.
        loginusername=request.POST['email']

        #  This line retrieves the value of the 'pass1' field (presumably the password) from the POST data.
        loginpassword=request.POST['pass1']


        # This line attempts to authenticate the user using the provided email (as username) and password. Django's authenticate function checks the provided credentials against those stored in the database.
        user=authenticate(username=loginusername,password=loginpassword)
       

    #    This conditional block checks if the
    #  authentication was successful. If a user with the provided email and password exists in the database, authenticate returns a User object. If authentication is successful, it logs in the user using Django's login function, adds an info message indicating successful login using Django's messages framework, and redirects the user to the home page.
        if user is not None:
            login(request,user)
            messages.info(request,"Successfully Logged In")
            return redirect('/')
        
        # If authentication fails (i.e., if authenticate returns None), it means the provided credentials are invalid. In this case, 
        # it adds an error message indicating invalid credentials using Django's messages framework and redirects the user back to the login page.
        else:
            messages.error(request,"Invalid Credentials")
            return redirect('/login')    

         
    #    This line renders the 'login.html' template if the request method is not POST, i.e., when the user visits the login page initially or when there are validation errors in the form submission.
      return render(request,'login.html')         


# This line defines the view function signup which takes a request object as its parameter.
def signup(request):

    # This condition checks if the form is being submitted via the POST method.
    if request.method == 'POST':


        # This line retrieves the value of the 'email' field from the POST data submitted by the form.
        email=request.POST.get('email')

        # This line retrieves the value of the 'pass1' field (presumably the password) from the POST data.
        pass1=request.POST.get('pass1')

        # This line retrieves the value of the 'pass2' field (presumably the password confirmation) from the POST data.
        pass2=request.POST.get('pass2')

        # This condition checks if the two passwords entered by the user match. If they don't match, it adds an error message using Django's messages framework and redirects the user back to the signup page.
        if pass1 != pass2:

            messages.error(request,"Password do not Match,Please Try Again!")
            return redirect('/signup')
        

        # This block of code checks if a user with the 
        # provided email (used as username) already exists in the database. If a user with that email already exists, it adds a warning message and redirects the user back to the signup page. The try-except block is used to catch the exception if the user does not exist, and the pass statement is used to ignore it.
        try:
            if User.objects.get(username=email):
                messages.warning(request,"Email Already Exists")
                return redirect('/signup')
        except Exception as identifier:            
            pass 


        # This block of code checks if a user with the
        #  provided email already exists in the database (in the 'email' field). If a user with that email already exists, it adds a warning message and redirects the user back to the signup page. The try-except block is used to catch the exception if the user does not exist, and the pass statement is used to ignore it.
        try:
            if User.objects.get(email=email):
                messages.warning(request,"Email Already Exists")
                return redirect('/signup')
        except Exception as identifier:
            pass        
       

        # This line creates a new user object with the provided email as both the username and email address, and the provided password.
        user=User.objects.create_user(email,email,pass1)

        # This line saves the newly created user object to the database.
        user.save()

        #  This line adds an info message to the Django messages framework, indicating successful registration.
        messages.info(request,'Thanks For Signing Up')
       
        return redirect('/login') 


    # This line renders the 'signup.html' template 
    # if the request method is not POST, i.e., when the user visits the signup page initially or when there are validation errors in the form submission.   
    return render(request,"signup.html")        




def logouts(request):
    logout(request)
    messages.warning(request,"Logout Success")
    return render(request,'login.html')