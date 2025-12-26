from datetime import datetime
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Court
from .availability import get_daily_booking_blocks


class AvailabilityBlocksView(APIView):
    """
    GET /api/v1/availability/blocks/?court_id=1&date=YYYY-MM-DD
    """
    def get(self, request):
        court_id = request.query_params.get("court_id")
        date_str = request.query_params.get("date")

        if not court_id or not date_str:
            return Response(
                {"detail": "court_id and date are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        day = parse_date(date_str)
        if not day:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            court = Court.objects.get(id=court_id, is_active=True)
        except Court.DoesNotExist:
            return Response({"detail": "Court not found"}, status=status.HTTP_404_NOT_FOUND)

        blocks = get_daily_booking_blocks(court, day)

        # Serialize datetimes to ISO strings
        data = [
            {
                "start": b["start"].isoformat(),
                "end": b["end"].isoformat(),
            }
            for b in blocks
        ]

        return Response(data)
