# mport Django path and views: The code starts by importing the path function from django.urls and 
# the views from the ecommerceapp application.

from django.conf import settings
from django.urls import path

from ecommerceapp import views


#  The urlpatterns list contains various URL patterns mapped to their corresponding view functions using the path() function.



urlpatterns = [
   
   path('',views.home,name='home'),
    path('login',views.handlelogin,name='handlelogin'),
    path('signup',views.signup,name='signup'),
    path('logout',views.logouts,name='logouts'),
    path('about', views.about, name="AboutUs"),
    path('contactus',views.contactus,name='contactus'),
    path('tracker', views.tracker, name="TrackingStatus"),
    path('products/<int:myid>', views.productView, name="ProductView"),
    path('checkout/', views.checkout, name="Checkout"),
    path('handlerequest/', views.Handlerequest, name="HandleRequest")
]
# Each path() function maps a URL pattern to a specific view function.
# The first argument is the URL pattern string.
# The second argument is the view function that should be called when the URL pattern is matched.
# The optional name parameter provides a unique identifier for the URL pattern, which can be used to refer to it in templates or code.



# '': Maps to the home view, typically the landing page of the website.
#  'login', 'signup', 'logout': Map to views for user authentication and session management.
# 'about', 'contactus': Map to views providing information about the website or means to contact.
# 'tracker': Maps to a view for tracking order status.
# 'products/<int:myid>': Maps to a view for displaying details of a specific product identified by myid.
# 'checkout/': Maps to the checkout view, which handles the checkout process.
# 'handlerequest/': Maps to the handlerequest view, which is likely used as a callback URL for processing payment responses or other requests.


# <int:myid>: This is a path converter that captures an integer value from
#  the URL and passes it as a parameter to the associated view function. In this case,
#  it captures the myid parameter and passes it to the productView view function.