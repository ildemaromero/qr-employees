import qrcode

class Qr:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def encode(self, text: str):
        pass
        
    def decoded(self, text :str):
        pass
        
    def generate(self, document_number: str):
        # TODO construir url
        # url_to_encode = self.base_url + 
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=15,
            border=1,
        )
        
        qr.add_data(document_number)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"codes/{document_number}.png")
        
        
        print("QR code generated and saved as my_qrcode.png")