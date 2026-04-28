from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Listing
from .forms import ListingForm


def listing_list(request):
    listings = Listing.objects.filter(approved=True, is_available=True)

    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    location = request.GET.get('location', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if query:
        listings = listings.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if category:
        listings = listings.filter(category=category)
    if location:
        listings = listings.filter(location__icontains=location)
    if min_price:
        listings = listings.filter(price_per_day__gte=min_price)
    if max_price:
        listings = listings.filter(price_per_day__lte=max_price)

    categories = Listing.CATEGORY_CHOICES
    return render(request, 'listings/listing_list.html', {
        'listings': listings,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'location': location,
        'min_price': min_price,
        'max_price': max_price,
    })


def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk, approved=True)
    reviews = listing.reviews.select_related('reviewer').order_by('-created_at')
    avg_rating = listing.average_rating()
    active_booking = listing.active_booking()  # ← NEW
    return render(request, 'listings/listing_detail.html', {
        'listing': listing,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'active_booking': active_booking,  # ← NEW
    })


@login_required
def listing_create(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.approved = False
            listing.save()
            messages.success(request, 'Listing submitted! It will appear after admin approval.')
            return redirect('my_listings')
    else:
        form = ListingForm()
    return render(request, 'listings/listing_form.html', {'form': form, 'action': 'Create'})


@login_required
def listing_edit(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.approved = False
            listing.save()
            messages.success(request, 'Listing updated! Pending re-approval.')
            return redirect('my_listings')
    else:
        form = ListingForm(instance=listing)
    return render(request, 'listings/listing_form.html', {'form': form, 'action': 'Edit'})


@login_required
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user)
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Listing deleted.')
        return redirect('my_listings')
    return render(request, 'listings/listing_confirm_delete.html', {'listing': listing})


@login_required
def my_listings(request):
    listings = Listing.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'listings/my_listings.html', {'listings': listings})