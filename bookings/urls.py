from django.urls import path
from .views import BookingCreateView, MyBookingsView, BookingCancelView
urlpatterns = [
    path("bookings/", BookingCreateView.as_view()),
    path("bookings/mine/", MyBookingsView.as_view()),
    path("bookings/<int:booking_id>/cancel/", BookingCancelView.as_view()),
]
