from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .models import Booking
from .serializers import BookingSerializer
from Users.models import Ws_User
from django.core.mail import send_mail

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        professor_id = data.get('professor')
        
        if not professor_id:
            raise ValidationError('Professor ID is required')
        
        # Retrieve the professor instance
        try:
            professor = Ws_User.objects.get(id=professor_id)
        except Ws_User.DoesNotExist:
            raise ValidationError('Professor not found')

        data['professor'] = professor.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        booking = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        response_data = {
            "message": "Booking created successfully. Please wait for the professor to approve.",
            "detail": "Booking created successfully.",
            "booking_id": booking.id,
            "professor": {
                "id": professor.id,
                "username": professor.username,
                "email": professor.email
            },
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email
            },
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "additional_email": booking.additional_email,
            "status": booking.status,
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        professor_id = self.request.data.get('professor')
        professor = Ws_User.objects.get(id=professor_id)
        additional_email = self.request.data.get('additional_email')
        return serializer.save(user=self.request.user, professor=professor, additional_email=additional_email)

    def get_queryset(self):
        professor_id = self.request.query_params.get('professor')
        if professor_id:
            return Booking.objects.filter(professor_id=professor_id)
        return Booking.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        try:
            booking = Booking.objects.get(pk=pk)
            if booking.professor != request.user:
                return Response({'detail': 'You do not have permission to approve this booking.'}, status=status.HTTP_403_FORBIDDEN)
            booking.status = 'approved'
            booking.save()

            # Send confirmation email
            email = booking.additional_email or booking.user.email
            send_mail(
                'Booking Confirmation',
                f'Your booking with Professor {booking.professor.username} from {booking.start_time} to {booking.end_time} has been approved.',
                'noreply@wellspace.com',
                [email],
                fail_silently=False,
            )

            return Response({'detail': 'Booking approved and confirmation email sent.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': 'Error approving booking.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='update')
    def update_booking(self, request, pk=None):
        try:
            booking = Booking.objects.get(pk=pk)
            if booking.user != request.user and booking.professor != request.user:
                return Response({'detail': 'You do not have permission to update this booking.'}, status=status.HTTP_403_FORBIDDEN)
            
            data = request.data.copy()
            serializer = BookingSerializer(booking, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response_data = {
                    'detail': 'Booking updated successfully.',
                    'data': serializer.data
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': 'Error updating booking.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='received-bookings', permission_classes=[IsAuthenticated])
    def received_bookings(self, request):
        try:
            professor = request.user
            if not professor:
                return Response({'detail': 'Professor not found.'}, status=status.HTTP_404_NOT_FOUND)
            bookings = Booking.objects.filter(professor=professor)
            serializer = BookingSerializer(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': 'Error fetching received bookings.'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_booking(self, request, pk=None):
        try:
            booking = Booking.objects.get(pk=pk)
            if booking.user != request.user and booking.professor != request.user:
                return Response({'detail': 'You do not have permission to delete this booking.'}, status=status.HTTP_403_FORBIDDEN)
            booking.delete()

            # Send cancellation email
            email = booking.additional_email or booking.user.email
            send_mail(
                'Booking Cancellation',
                f'Your booking with Professor {booking.professor.username} from {booking.start_time} to {booking.end_time} has been canceled.',
                'noreply@wellspace.com',
                [email],
                fail_silently=False,
            )

            return Response({'detail': 'Booking deleted and notification email sent.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': 'Error deleting booking.'}, status=status.HTTP_400_BAD_REQUEST)

class UserBookingsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        bookings = Booking.objects.filter(user=user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
