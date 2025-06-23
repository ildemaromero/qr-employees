import qrcode
import base64
import hashlib
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

password = os.getenv("PASSWORD")
key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
cipher = Fernet(key)

class Qr:
    def __init__(self, base_url: str = None):
        self.base_url = base_url
    
    def encode(self, text: str):
        token = cipher.encrypt(text.encode()).decode()
        print("Encrypted:", token)
        return token
        
    def decode(self, token :str):
        decrypted = cipher.decrypt(token.encode()).decode()
        print("Decrypted:", decrypted)
        return decrypted
        
    def generate(self, document_number: str):
        url_to_encode = self.base_url + self.encode(document_number)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=15,
            border=1,
        )
        
        qr.add_data(url_to_encode)
        qr.make(fit=True)
        
        qr_name = f"{document_number.strip()}.png"
        qr_path = f"codes/{qr_name}"
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(qr_path)
        
        print("QR code generated and saved as my_qrcode.png")
        
        return qr_name, qr_path