from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings

import logging
import requests

logger = logging.getLogger(__name__)

class ContactView(APIView):
    permission_classes = [AllowAny]
        
    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip()
        message = request.data.get('message', '').strip()

        # 🔒 Validate input
        if not all([name, email, message]):
            return Response(
                {'error': 'All fields are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    # ✅ Works without domain
                    "from": "Portfolio <onboarding@resend.dev>",
                    "to": ["connectadrijam@gmail.com"],  # ← YOUR email
                    "subject": f"Portfolio Contact from {name}",
                    "html": f"""
                        <h3>New Contact Form Submission</h3>
                        <p><strong>Name:</strong> {name}</p>
                        <p><strong>Email:</strong> {email}</p>
                        <p><strong>Message:</strong></p>
                        <p>{message}</p>
                    """,
                },
            )

            # 🔍 Check response from Resend
            if response.status_code not in [200, 201]:
                return Response(
                    {'error': f'Email failed: {response.text}'},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            return Response(
                {'success': True, 'message': 'Message sent successfully!'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )