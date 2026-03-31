import logging
import os
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

logger = logging.getLogger(__name__)

class SMSService:
    @staticmethod
    def send_otp(phone_number: str, otp_code: str):
        """
        Send OTP to the given phone number using MSG91.
        In production, integrated with MSG91.
        """
        auth_key = os.getenv("MSG91_AUTH_KEY")
        template_id = os.getenv("MSG91_TEMPLATE_ID")

        if not auth_key or not template_id:
            logger.error("MSG91_AUTH_KEY or MSG91_TEMPLATE_ID not found in environment variables")
            # For development, log it as well
            print("\n" + "="*50)
            print(f"  MOCK OTP FOR {phone_number}: {otp_code}")
            print("="*50 + "\n")
            return False

        # Ensure phone number has country code (remove all non-digit characters)
        clean_phone = "".join(filter(str.isdigit, phone_number))
        if len(clean_phone) == 10:
            clean_phone = "91" + clean_phone
        
        # MSG91 Direct OTP API Endpoint (control.msg91.com is standard for v5)
        # We put mandatory params in the URL and custom variables in the body
        url = "https://control.msg91.com/api/v5/otp"
        
        params = {
            "template_id": template_id,
            "mobile": clean_phone,
            "authkey": auth_key
        }
        
        payload = {
            "otp": otp_code
        }
        
        headers = {
            "Content-Type": "application/json",
            "authkey": auth_key
        }

        try:
            logger.info(f"Sending OTP to {clean_phone} via MSG91...")
            # Sending with both params (query string) and json (body)
            response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)
            
            try:
                res_data = response.json()
            except Exception:
                res_data = {"raw_text": response.text}
            
            if response.status_code == 200 and (res_data.get("type") == "success" or res_data.get("request_id")):
                logger.info(f"OTP {otp_code} successfully sent to {clean_phone}")
                print(f"✅ MSG91 SUCCESS: OTP {otp_code} sent to {clean_phone}")
                return True
            else:
                error_msg = f"Failed to send OTP via MSG91. Status: {response.status_code}, Response: {res_data}"
                logger.error(error_msg)
                print(f"❌ MSG91 FAILURE: {error_msg}")
                return False
                
        except Exception as e:
            error_msg = f"Error during MSG91 request: {str(e)}"
            logger.error(error_msg)
            print(f"❌ SMS Service exception: {error_msg}")
            return False

sms_service = SMSService()
