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

        if not all([name, email, message]):
            return Response(
                {'error': 'All fields are required.'},
                status=400
            )

        try:
            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": "onboarding@resend.dev",
                    "to": ["connectadrijam@gmail.com"],
                    "subject": f"Portfolio Contact from {name}",
                    "html": f"""
                        <p><strong>Name:</strong> {name}</p>
                        <p><strong>Email:</strong> {email}</p>
                        <p>{message}</p>
                    """,
                },
            )

            return Response({"success": True}, status=200)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=500
            )