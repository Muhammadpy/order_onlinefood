from django.shortcuts import render
from vendor.models import Vendor
from django.shortcuts import get_object_or_404
from menu.models import Category, FoodItem
from django.db.models import Prefetch


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
    print(categories, '111111')
    context = {
        'vendor': vendor,
        'categories': categories,
    
    }
    
    return render(request, 'marketplace/vendor_detail.html', context)
