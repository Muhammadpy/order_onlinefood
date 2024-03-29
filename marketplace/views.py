from django.http import HttpResponse
from django.shortcuts import render, redirect
from.context_processors import get_cart_counter, get_cart_amounts
from vendor.models import Vendor
from django.shortcuts import get_object_or_404
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from django.http import  JsonResponse
from .models import Cart
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D # D is Distancefrom
from django.contrib.gis.db.models.functions import Distance

# Create your views here.


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    print(vendors)
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
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
            #check fooditem exits
            try:
                fooditem = FoodItem.objects.get(id = food_id)
                #check user already added items
                try:
                    chkCart = Cart.objects.get(
                        user=request.user, fooditem=fooditem)
                    
                    # increase quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'success', 'message': 'added fooditem', 'cart_counter' : get_cart_counter(request), 'qty' : chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    chkCart = Cart.objects.create(
                        user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'success', 'message': 'created one fooditem', 'cart_counter' : get_cart_counter(request), 'qty' : chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
            except:       
                return JsonResponse({'status': 'Failed', 'message': 'Fooditem does not exits'})
        
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request11'})
    else:
        return JsonResponse({'status' : 'login_required', 'message' : 'Please login to continue' })
    







def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # check fooditem exits
            try:
                
                
                fooditem = FoodItem.objects.get(id = food_id)                
                #check user already added items
                try:
                    chkCart = Cart.objects.get(
                        user=request.user, fooditem=fooditem)
                    
                    if chkCart.quantity > 1:
                        chkCart.quantity -= 1
                        chkCart.save()
                       
                    # decreace quantity
                    else:
                        chkCart.delete()
                        chkCart.quantity=0
                    return JsonResponse({'status': 'success', 'message': 'decrease fooditem', 'cart_counter' : get_cart_counter(request), 'qty' : chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})
            except:       
                return JsonResponse({'status': 'Failed', 'message': 'Fooditem does not exits'})
        
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request11'})
    else:
        return JsonResponse({'status' : 'login_required', 'message' : 'Please login to continue' })
    
@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # check if cart item exist
                cart_item=Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'success', 'message':'Cart item has been deleted', 'cart_counter':get_cart_counter(request), 'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Fooditem does not exits'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request11'})
            
            

def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace:marketplace')  
    else:
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']
        
        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
        
        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems)  |  Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude , latitude))
            vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems)  |  Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
            user_profile__location__distance_lte=(pnt, D(km=radius))
            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")
            
            for v in vendors:
                v.kms = round(v.distance.km, 1)
            
        vendor_count = vendors.count()
        context = {
            'vendors' : vendors,
            'vendor_count' : vendor_count,
            'source_location': address,
            
        }
        
        return render(request, 'marketplace/listing.html', context)


