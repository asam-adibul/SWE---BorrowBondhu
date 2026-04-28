from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from listings.models import Listing
from .models import Booking
from .forms import BookingForm


@login_required
def booking_create(request, listing_pk):
    listing = get_object_or_404(Listing, pk=listing_pk, approved=True)

    if listing.owner == request.user:
        messages.error(request, "You cannot book your own listing.")
        return redirect('listing_detail', pk=listing_pk)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.renter = request.user
            booking.listing = listing
            booking.status = 'pending'
            booking.save()
            messages.success(request, 'Booking request sent! Wait for the owner to respond.')
            return redirect('my_bookings')
    else:
        form = BookingForm()
    return render(request, 'bookings/booking_form.html', {'form': form, 'listing': listing})


@login_required
def my_bookings(request):
    # Bookings I made as a renter
    my_rents = Booking.objects.filter(renter=request.user).select_related('listing').order_by('-created_at')
    # Bookings on my listings (as owner)
    my_requests = Booking.objects.filter(listing__owner=request.user).select_related('listing', 'renter').order_by('-created_at')
    return render(request, 'bookings/my_bookings.html', {
        'my_rents': my_rents,
        'my_requests': my_requests,
    })


@login_required
def booking_action(request, pk, action):
    booking = get_object_or_404(Booking, pk=pk, listing__owner=request.user)
    if action == 'accept' and booking.status == 'pending':
        booking.status = 'accepted'
        messages.success(request, 'Booking accepted!')
    elif action == 'reject' and booking.status == 'pending':
        booking.status = 'rejected'
        messages.info(request, 'Booking rejected.')
    elif action == 'complete' and booking.status == 'accepted':
        booking.status = 'completed'
        messages.success(request, 'Booking marked as completed.')
    booking.save()
    return redirect('my_bookings')