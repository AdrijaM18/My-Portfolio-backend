from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings

from django.conf import settings


from_email=settings.EMAIL_HOST_USER

class ContactView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip()
        message = request.data.get('message', '').strip()

        if not all([name, email, message]):
            return Response(
                {'error': 'All fields are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 1. Email to YOU (site owner)
            send_mail(
                subject=f'Portfolio Contact from {name}',
                message=f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}',
                from_email=from_email, 
                recipient_list=['connectadrijam@gmail.com'],
                fail_silently=False,
            )

            # 2. Confirmation email to USER
            send_mail(
                subject='Thanks for contacting me!',
                message=(
                    f'Hi {name},\n\n'
                    'Thanks for reaching out. I’ve received your message and will get back to you soon.\n\n'
                    'Here’s a copy of your message:\n\n'
                    f'{message}\n\n'
                    'Best regards,\n'
                    'Adrija'
                ),
                from_email=from_email,
                recipient_list=[email],  
                fail_silently=False,
            )

            return Response({'success': True}, status=status.HTTP_200_OK)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"EMAIL ERROR: {str(e)}")
            # Still return 200 so frontend gets CORS headers, but log the error
            return Response(
                {'success': True, 'message': 'Message received (email delivery pending)'},
                status=status.HTTP_200_OK
            )
