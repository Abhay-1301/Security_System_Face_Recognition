import smtplib
import random
import face_recognition as fr
import cv2
import numpy as np
# import RPi.GPIO as GPIO
import time
import qrcode
import string
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import io
import base64
import configparser

# Load configuration from the ini file
config = configparser.ConfigParser()
config.read('config.ini')


def generate_and_send_qr_code(recipient_email):
    # Generate a random code
    code = ''.join(random.choices(string.digits, k=6))

    # Create a QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(code)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Convert QR code image to bytes
    img_byte_arr = io.BytesIO()
    qr_img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Encode QR code image as base64 string
    img_base64 = base64.b64encode(img_byte_arr).decode('ascii')

    # Compose the email
    email_subject = config.get('EMAIL', 'email_subject')
    email_body = config.get('EMAIL', 'email_body')
    sender_email = config.get('EMAIL', 'sender_email')
    sender_password = config.get('EMAIL', 'sender_password')

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = email_subject

    msg.attach(MIMEText(email_body, "plain"))

    # Attach the QR code image to the email
    qr_code_img = MIMEImage(base64.b64decode(img_base64))
    qr_code_img.add_header("Content-Disposition", "attachment", filename="qr_code.png")
    msg.attach(qr_code_img)

    # Send the email
    smtp_server = config.get('EMAIL', 'smtp_server')
    smtp_port = config.getint('EMAIL', 'smtp_port')

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print("Failed to send email. Error:", str(e))

    # Return the generated code
    return code


def find_email(name):
    # create dictionary of names and emails
    name_email_dict = name_email_dict = dict(config.items('EMAIL_OF_HEADS'))

    # return email of person whose name is given as input
    # If the name is not in the dictionary, get() returns None by default.
    return name_email_dict.get(name)


def get_name(qr):
    # create dictionary of names and emails
    qr_name_dict = dict(config.items('QR_OF_HEADS'))

    # return email of person whose name is given as input
    # If the name is not in the dictionary, get() returns None by default.
    return qr_name_dict.get(qr)


def load_known_face_encodings_and_names():
    # known_face_encodings = []
    # known_face_names = []
    # for images in os.listdir('TL_Coords_Faces'):
    #     file_path = os.path.join('TL_Coords_Faces',images)
    #     face_image = fr.load_image_file(file_path)
    #     face_encoding = fr.face_encodings(face_image)[0]
    #     known_face_encodings.append(face_encoding)
    #     known_face_names.append(images[:images.index(".")])

    # np.save('known_face_encodings.npy', np.array(known_face_encodings))
    # np.save('known_face_names.npy', np.array(known_face_names))
    known_face_encodings = (np.load('known_face_encodings.npy')).tolist()
    known_face_names = (np.load('known_face_names.npy')).tolist()
    return known_face_encodings, known_face_names



def take_input():
    return input("Enter the OTP : ")

# def display_output(message):
#      display output on lcd display

def decode_qr(frame):
    # initialize the cv2 QRCode detector
    detector = cv2.QRCodeDetector()
    # detect and decode
    decoded_qr, vertices_array, binary_qrcode = detector.detectAndDecode(frame)
    if vertices_array is not None:
        return decoded_qr    
    else:
        return None

def check_otp(real_otp, user_input):
    if (user_input == "" or user_input == None):
        return False
    if int(real_otp) == int(user_input):
        return True
    else:
        return False


# def open_lock(pin):
#     GPIO.setmode(GPIO.BOARD)
#     GPIO.setup(pin, GPIO.OUT)
#     GPIO.output(pin, GPIO.HIGH)
#     try:
#         # Keep the lock open for 5 seconds
#         time.sleep(5)
#     except KeyboardInterrupt:
#         # Clean up GPIO on keyboard interrupt
#         GPIO.cleanup()

def open_lock():
    print('LOCK OPENED')


def decode_name_from_qr(frame):
    method = 'qr'
    decoded_qr = decode_qr(frame)
    if decoded_qr is not None:
        decoded_name_from_qr = get_name(decoded_qr)
        if decoded_name_from_qr is not None:
            print(decoded_name_from_qr)
            print('name printed from QR code')
            return decoded_name_from_qr , method
        else:
            return None , method
            
    else:
        return None , method


def recognize_face(frame, known_face_encodings, known_face_names):
    method = 'face'
    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    # Find all the faces and face encodings in the current frame of video
    face_locations = fr.face_locations(small_frame)
    if(len(face_locations)==0):
       return None , method    
    else:
        face_encodings = fr.face_encodings(small_frame, face_locations)
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = fr.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = fr.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index] and face_distances[best_match_index] < 0.5:
                name = known_face_names[best_match_index]
                print(name)
                print('name printed from face recognize')  
                return name , method
            else:
                return None , method


def main(frame,known_face_encodings,known_face_names,cap):

    name = None
    method = None

    name , method = decode_name_from_qr(frame)

    if (name==None):
        name , method = recognize_face(frame, known_face_encodings, known_face_names)

    if (name == None):
        return

    if method == 'qr':
        open_lock()
        return

    if method == 'face':
        matched_email = find_email(name)
        otp = 736235
        # otp = send_otp(matched_email)
        # otp = generate_and_send_qr_code(matched_email)
        start_time = time.time()
        duration = 60  # Duration in seconds
        while (True):
            ret, temp_frame = cap.read()
            if check_otp(real_otp=otp, user_input=decode_qr(frame=temp_frame)): #take_input() for keyboard entering of otp
                open_lock()
                return
            else:
                elapsed_time = time.time() - start_time
                print(elapsed_time)
                if elapsed_time >= duration:
                    return


if __name__ == "__main__":
    known_face_encodings, known_face_names = load_known_face_encodings_and_names()
    cap = cv2.VideoCapture(0)
    try:
        while (True):
            ret, frame = cap.read()
            main(frame,known_face_encodings,known_face_names,cap)
    except:
        cap.release()
        print("An Error Ocurred. Restart Again.")