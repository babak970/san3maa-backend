from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from arenas.models import Court
from arenas.availability import get_daily_booking_blocks
from .models import Booking
from .serializers import BookingCreateSerializer, BookingSerializer


class BookingCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        court_id = serializer.validated_data["court_id"]
        start = serializer.validated_data["start"]
        end = serializer.validated_data["end"]

        try:
            court = Court.objects.get(id=court_id, is_active=True)
        except Court.DoesNotExist:
            return Response({"detail": "Court not found"}, status=status.HTTP_404_NOT_FOUND)

        # 1) Validate requested block is one of the allowed blocks for that day
        allowed_blocks = get_daily_booking_blocks(court, start.date())
        allowed_set = {(b["start"], b["end"]) for b in allowed_blocks}

        if (start, end) not in allowed_set:
            return Response(
                {"detail": "Requested time is not available or not a valid preset block."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2) Prevent double-booking (atomic check)
        conflict = Booking.objects.select_for_update().filter(
            court=court,
            status=Booking.Status.RESERVED,
            start__lt=end,
            end__gt=start,
        ).exists()

        if conflict:
            return Response({"detail": "Time already booked"}, status=status.HTTP_409_CONFLICT)

        # 3) Price: for now, use the price from availability blocks if you want
        # We'll keep it simple for now:
        price = 80

        booking = Booking.objects.create(
            user=request.user,
            court=court,
            start=start,
            end=end,
            price=price,
            status=Booking.Status.RESERVED,
        )

        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

class MyBookingsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by("-created_at")
class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        if booking.status != Booking.Status.RESERVED:
            return Response({"detail": "Cannot cancel this booking"}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status"])

        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)
