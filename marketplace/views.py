from django.http import HttpResponse
from django.shortcuts import render
from.context_processors import get_cart_counter
from vendor.models import Vendor
from django.shortcuts import get_object_or_404
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from django.http import  JsonResponse
from .models import Cart



# Create your views here.


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vedor_count = vendors.count()
    print(vendors)
    context = {
        'vendors': vendors,
        'vedor_count': vedor_count,
    }
    
    return render(request, 'marketplace/listing.html', context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    
    if request.user.is_authenticated:
        cart_items= Cart.objects.filter(user=request.user)
    else:
        cart_items=None
        
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
    }
    
    return render(request, 'marketplace/vendor_detail.html', context)


def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # chech fooditem exits
            try:
                fooditem = FoodItem.objects.get(id = food_id)
                #check user already added items
                try:
                    chkCart = Cart.objects.get(
                        user=request.user, fooditem=fooditem)
                    
                    # increase quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'success', 'message': 'added fooditem', 'cart_counter' : get_cart_counter(request), 'qty' : chkCart.quantity,})
                except:
                    chkCart = Cart.objects.create(
                        user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'success', 'message': 'created one fooditem', 'cart_counter' : get_cart_counter(request), 'qty' : chkCart.quantity})
            except:       
                return JsonResponse({'status': 'Failed', 'message': 'Fooditem does not exits'})
        
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request11'})
    else:
        return JsonResponse({'status' : 'login_required', 'message' : 'Please login to continue' })
    







def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # chech fooditem exits
            try:
                
                
                fooditem = FoodItem.objects.get(id = food_id)                
                #check user already added items
                try:
                    chkCart = Cart.objects.get(
                        user=request.user, fooditem=fooditem)
                    print(chkCart.quantity, "salommmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
                    
                    if chkCart.quantity > 1:
                        chkCart.quantity -= 1
                        chkCart.save()
                       
                    # increase quantity
                    else:
                        chkCart.delete()
                        chkCart.quantity=0
                    return JsonResponse({'status': 'success', 'message': 'decrease fooditem', 'cart_counter' : get_cart_counter(request), 'qty' : chkCart.quantity})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})
            except:       
                return JsonResponse({'status': 'Failed', 'message': 'Fooditem does not exits'})
        
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request11'})
    else:
        return JsonResponse({'status' : 'login_required', 'message' : 'Please login to continue' })
    

def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    print(cart_items)
    
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)