import smtplib
from email.message import EmailMessage
import mimetypes

msg = EmailMessage()
msg['Subject'] = 'IoT project'
msg['From'] = 'matteobergamaschi02@gmail.com'
msg['To'] = 'dcfrenci2@gmail.com'
msg.set_content('Grande DC se ti arriva godo')

filename = 'prediction_model.py' 

try:
    with open(filename, 'rb') as f:
        dati_file = f.read()
        
        tipo_mime, _ = mimetypes.guess_type(filename)
        if tipo_mime is None:
            tipo_mime = 'application/octet-stream'
            
        maintype, subtype = tipo_mime.split('/', 1)

    msg.add_attachment(
        dati_file, 
        maintype=maintype, 
        subtype=subtype, 
        filename=filename
    )
    
except FileNotFoundError:
    print(f"Error: file not found '{filename}'.")
    exit()


try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login('matteobergamaschi02@gmail.com', 'ztjf pdtv isgu yvsb')
        server.send_message(msg=msg)
    print("Email sent!")
except Exception as e:
    print(f"Error: {e}")