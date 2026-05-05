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

        # 🔒 Validation
        if not all([name, email, message]):
            return Response(
                {'error': 'All fields are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            headers = {
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            }

            # 📩 1. Email to YOU
            owner_email = requests.post(
                "https://api.resend.com/emails",
                headers=headers,
                json={
                    # ⚠️ Change this after domain verification
                    "from": "Portfolio <onboarding@resend.dev>",
                    "to": ["connectadrijam@gmail.com"],
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

            # 📬 2. Confirmation email to USER
            # ⚠️ Will only work AFTER domain verification
            user_email = requests.post(
                "https://api.resend.com/emails",
                headers=headers,
                json={
                    "from": "Portfolio <onboarding@resend.dev>",
                    "to": [email],
                    "subject": "Thanks for reaching out!",
                    "html": f"""
                        <p>Hi {name},</p>

                        <p>Thanks for contacting me. I’ve received your message and will get back to you soon.</p>

                        <p><strong>Your message:</strong></p>
                        <blockquote>{message}</blockquote>

                        <p>Best regards,<br/>Adrija</p>
                    """,
                },
            )

            # 🔍 Check if API calls succeeded
            if owner_email.status_code not in [200, 201]:
                return Response(
                    {'error': f'Failed to send owner email: {owner_email.text}'},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            # ⚠️ User email might fail in sandbox — don’t block success
            if user_email.status_code not in [200, 201]:
                return Response(
                    {
                        'success': True,
                        'warning': 'Message sent, but confirmation email failed (domain not verified yet).'
                    },
                    status=status.HTTP_200_OK
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