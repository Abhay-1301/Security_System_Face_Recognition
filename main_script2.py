import smtplib
import random
import face_recognition as fr
import cv2
import numpy as np
import threading
# import RPi.GPIO as GPIO
import time
from PIL import Image
from io import BytesIO
import qrcode
import email
from email.mime.multipart import MIMEMultipart
# from email.MIMEText import MIMEText
# from email.MIMEImage import MIMEImage
# import os

# OTP = send_mail('********@iith.ac.in')
# print(OTP)


def send_qr_code(recipient_email):
    # Generate random 6-digit number
    code = random.randint(100000, 999999)

    # Create QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(str(code))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert image to bytes
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_bytes = buffer.getvalue()

    # Set up email information
    sender_email_address = '*********@outlook.com'
    sender_email_password = '**************'

    subject = 'TL Security Code'
    instruction = 'Scan this QR code to get the Security Code'
    body = f'{instruction}'

    # Set up the SMTP server
    smtp_server = 'smtp.outlook.com'
    smtp_port = 587
    smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
    smtp_connection.starttls()
    smtp_connection.login(sender_email_address, sender_email_password)

    # Create the email message with attached QR code image
    message = MIMEMultipart()
    message['From'] = sender_email_address
    message['To'] = recipient_email
    message['Subject'] = subject
    message.attach(email.MIMEText.MIMEText(body))
    image = email.MIMEImage.MIMEImage(img_bytes)
    message.attach(image)

    # Send the email
    smtp_connection.sendmail(sender_email_address, recipient_email, message.as_string())

    # Close the SMTP connection
    smtp_connection.quit()

    # Return code
    return code

def send_otp(recipient_email):

    OTP = random.randint(100000, 999999)
    print(f'Your OTP is {OTP}')
    # Set up the email account information
    sender_email_address = '************@outlook.com'
    sender_email_password = '*************'

    # recipient_email = '**********@iith.ac.in'

    subject = 'TL Security Code'
    instruction = 'Enter this Security Code through keypad to unlock Door'
    body = f'Security Code: {OTP}\n{instruction}'

    # Set up the SMTP server
    smtp_server = 'smtp.outlook.com'
    smtp_port = 587
    smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
    smtp_connection.starttls()
    smtp_connection.login(sender_email_address, sender_email_password)

    # Create the email message
    message = f'Subject: {subject}\n\n{body}'

    # Send the email
    smtp_connection.sendmail(sender_email_address, recipient_email, message)

    # Close the SMTP connection
    smtp_connection.quit()

    # Return OTP
    return OTP


def find_email(name):
    # name_email_dict = dict(zip(known_face_names, known_face_mails))
    # name_email_dict
    # create dictionary of names and emails
    name_email_dict = {
        'Abhay': '**********@iith.ac.in'
    }

    # return email of person whose name is given as input
    # If the name is not in the dictionary, get() returns None by default.
    return name_email_dict.get(name)


def get_name(qr):
    # name_email_dict = dict(zip(known_face_names, known_face_mails))
    # name_email_dict
    # create dictionary of names and emails
    qr_name_dict = {
        'jejeje_1':      'Abhay'
    }

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

# def display_output():
#      display output on lcd display


def check_otp(real_otp, user_input):
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

def get_name(qr):
    # name_email_dict = dict(zip(known_face_names, known_face_mails))
    # name_email_dict
    # create dictionary of names and emails
    qr_name_dict = {
        'wjwkwe_1':      'Abhay'
    }

    # return email of person whose name is given as input
    # If the name is not in the dictionary, get() returns None by default.
    return qr_name_dict.get(qr)

def decode_qr(cap):
    method = 'qr'
    # initialize the cv2 QRCode detector
    detector = cv2.QRCodeDetector()
    # Keep scanning until the user quits
    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()

        # detect and decode
        decoded_qr, vertices_array, binary_qrcode = detector.detectAndDecode(frame)

        if vertices_array is not None:
            decoded_name_from_qr = get_name(decoded_qr)
            if decoded_name_from_qr is not None:
                # cap.release()
                print(decoded_name_from_qr)
                print('name printed from QR code')
                return decoded_name_from_qr , method


def recognize_face(cap, known_face_encodings, known_face_names):
    method = 'face'
    while True:
        # Grab a single frame of video
        ret, frame = cap.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        # rgb_small_frame = small_frame[:, :, ::-1]

        # Find all the faces and face encodings in the current frame of video
        face_locations = fr.face_locations(small_frame)
        face_encodings = fr.face_encodings(small_frame, face_locations)

        face_names = []
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

def main(cap,known_face_encodings,known_face_names):
    name , method = recognize_face(cap, known_face_encodings, known_face_names)


    if method == 'qr':
        open_lock()
        main(cap,known_face_encodings,known_face_names)
        return

    if method == 'face':
        matched_email = find_email(name)  # error here what if none?
        # otp = send_otp(matched_email)
        otp = send_qr_code(matched_email)
        wrong_otp_entered = 0
        while (True):
            if check_otp(real_otp=otp, user_input=take_input()):
                open_lock()
                main(cap,known_face_encodings,known_face_names)
                return
            # main(cap,known_face_encodings , known_face_names)
            else:
                if (wrong_otp_entered == 2):
                    main(cap,known_face_encodings,known_face_names)
                    return
                wrong_otp_entered = wrong_otp_entered + 1
                print("Wrong OTP. Try Again")


if __name__ == "__main__":
    known_face_encodings, known_face_names = load_known_face_encodings_and_names()
    cap = cv2.VideoCapture(0)
    main(cap,known_face_encodings,known_face_names)





# name_qr = None
# name_face = None
# name_detected = threading.Event()


# # create two threads for reading QR code and known face
# qr_thread = threading.Thread(target=decode_qr, args=(cap,))
# face_thread = threading.Thread(target=recognize_face, args=(cap,known_face_encodings, known_face_names,))

# # start both threads
# qr_thread.start()
# face_thread.start()

# # wait for either thread to finish or a name is detected
# name_detected.wait()

# # stop the other thread if a name is detected
# if name_detected.is_set():
#     if qr_thread.is_alive():
#         qr_thread._stop()
#     if face_thread.is_alive():
#         face_thread._stop()

# # use the name for your application
# if name_qr is not None:
#     name = name_qr
# else:
#     name = name_face

# print(name)
