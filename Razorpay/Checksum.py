from razorpay import Client as RazorpayClient
from django.conf import settings
def generate_checksum(param_dict, merchant_key):
    # Initialize Razorpay client
    razorpay_client = RazorpayClient(auth=(settings.razor_pay_key_id, settings.key_secret))

    # Generate checksum using Razorpay SDK method
    checksum = razorpay_client.utility.generate_signature(param_dict, merchant_key)

    return checksum

def verify_checksum(param_dict, merchant_key, checksum):
    # Initialize Razorpay client
    razorpay_client = RazorpayClient(auth=(settings.razor_pay_key_id,settings.key_secret ))

    # Verify checksum using Razorpay SDK method
    is_valid_checksum = razorpay_client.utility.verify_payment_signature(param_dict, checksum, merchant_key)

    return is_valid_checksum
