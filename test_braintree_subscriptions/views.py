from django.http import JsonResponse
import braintree
from django.conf import settings
from .forms import CustomerForm, SubscriptionForm
import json


braintree.Configuration.configure(
    braintree.Environment.Sandbox,
    merchant_id=settings.BRAINTREE_MERCHANT,
    public_key=settings.BRAINTREE_PUBLIC_KEY,
    private_key=settings.BRAINTREE_PRIVATE_KEY
)


def token(request, plan_id):
    plans = filter(lambda p: p.id == plan_id, braintree.Plan.all())
    plan = plans[0] if len(plans) else None
    if plan:
        return JsonResponse({
            "price": float(plan.price),
            "token": braintree.ClientToken.generate()
        })
    return JsonResponse({"error": "Plan doesn't exist"})


def create_customer(request):
    if request.POST:
        form = CustomerForm(request.POST)
        if form.is_valid():
            result = braintree.Customer.create(form.cleaned_data)
            if result.is_success:
                return JsonResponse({"customer": result.customer.id})
            return JsonResponse({
                "error": "Couldn't create customer",
                "description": map(
                    lambda err: {
                        "attribute": err.attribute,
                        "code": err.code,
                        "message": err.message
                    }, result.errors.deep_errors)})
        return JsonResponse({"error": "Form is invalid.", "form": json.dumps(form.errors)})
    return JsonResponse({"error": "Invalid request method."}, status=405)


def subscribe(request, plan_id):
    if request.POST:
        print request.POST
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            result = braintree.PaymentMethod.create({
                "customer_id": data['customer_id'],
                "payment_method_nonce": data['payment_method_nonce']
            })
            if result.is_success:
                subscription = braintree.Subscription.create({
                    "payment_method_token": result.payment_method.token,
                    "plan_id": plan_id
                })
                if subscription.is_success:
                    return JsonResponse({"message": "success"})
                return JsonResponse({
                    "error": "Couldn't create customer",
                    "description": map(
                        lambda err: {
                            "attribute": err.attribute,
                            "code": err.code,
                            "message": err.message
                        }, subscription.errors.deep_errors)})
            return JsonResponse({
                "error": "Couldn't create customer",
                "description": map(
                    lambda err: {
                        "attribute": err.attribute,
                        "code": err.code,
                        "message": err.message
                    }, result.errors.deep_errors)})
        return JsonResponse({"error": "Form is invalid.", "form": json.dumps(form.errors)})
    return JsonResponse({"error": "Invalid request method."}, status=405)

