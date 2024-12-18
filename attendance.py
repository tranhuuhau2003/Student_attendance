import tkinter as tk
import csv
import cv2
import os
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import time

window = tk.Tk()
window.title("STUDENT ATTENDANCE USING FACE RECOGNITION SYSTEM")
window.geometry('800x500')

dialog_title = 'QUIT'
dialog_text = "are you sure?"
window.configure(background='green')
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)


def clear_name():
    std_name.delete(0, 'end')
    res = ""
    label4.configure(text=res)


def clear_matric_number():
    std_number.delete(0, 'end')
    res = ""
    label4.configure(text=res)


def capture_image():
    name = (std_name.get())
    student_id = (std_number.get())
    if name.isalpha():
        cam = cv2.VideoCapture(0)
        harcascade_path = "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascade_path)
        sample_num = 0

        while True:
            ret, img = cam.read()
            img = cv2.flip(img, 1)  # Lật camera theo trục dọc (ngang)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.1, 3)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                sample_num += 1
                # store each student picture with its name and id
                cv2.imwrite(f"TrainingImages\\{name}.{student_id}.{str(sample_num)}.jpg",
                            gray[y:y + h, x:x + h])
                cv2.imshow('FACE RECOGNIZER', img)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            if sample_num > 50:
                break

        cam.release()
        cv2.destroyAllWindows()
        # print the student name and id after a successful face capturing
        res = f'Student details saved with:\n Matric number: {student_id} and Full Name: {name}'

        row = [student_id, name]

        with open('Excels/studentDetailss.csv', 'a+') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(row)
        csv_file.close()
        label4.configure(text=res)
    else:
        res = "Enter correct Matric Number"
        label4.configure(text=res)


def get_images_and_labels(path):
    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    ids = []
    for image_path in image_paths:
        pil_image = Image.open(image_path).convert('L')
        image_np = np.array(pil_image, 'uint8')
        student_id = int(os.path.split(image_path)[-1].split(".")[1])
        faces.append(image_np)
        ids.append(student_id)
    return faces, ids


def train_images():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    harcascade_path = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascade_path)
    faces, ids = get_images_and_labels("TrainingImages")
    recognizer.train(faces, np.array(ids))
    recognizer.save("Trainner.yml")
    res = "Images Trained"
    label4.configure(text=res)


def track_images():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("Trainner.yml")
    harcascade_path = "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(harcascade_path)
    df = pd.read_csv("Excels/studentDetailss.csv")
    font = cv2.FONT_HERSHEY_COMPLEX_SMALL
    cam = cv2.VideoCapture(0)
    col_names = ['Id', 'Name', 'Date', 'Time']
    attendance = pd.DataFrame(columns=col_names)

    while True:
        ret, img = cam.read()
        img = cv2.flip(img, 1)  # Lật camera theo trục dọc (ngang)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 3)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            student_id, conf = recognizer.predict(gray[y:y + h, x:x + w])
            if conf < 60:
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M')
                student_name = df.loc[df['ID'] == student_id]['NAME'].values
                tt = f"{student_id}-{student_name}"
                attendance.loc[len(attendance)] = [student_id, student_name, date, time_stamp]
                row = [student_id, student_name, date, time_stamp]
                with open('Excels/AttendanceFile.csv', 'a+') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(row)
                csv_file.close()
                res = 'ATTENDANCE UPDATED WITH DETAILS'
                label4.configure(text=res)
            else:
                student_id = 'Unknown'
                tt = str(student_id)
                if conf > 65:
                    no_of_files = len(os.listdir("UnknownImages")) + 1
                    cv2.imwrite(f"UnknownImages\\Image{str(no_of_files)}.jpg", img[y:y + h, x:x + w])
                    res = 'ID UNKNOWN, ATTENDANCE NOT UPDATED'
                    label4.configure(text=res)
            attendance = attendance.drop_duplicates(subset=['Id'], keep='first')
            cv2.putText(img, str(tt), (x, y + h - 10), font, 0.8, (255, 255, 255), 1)
            cv2.imshow('FACE RECOGNIZER', img)
        if cv2.waitKey(1000) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()


label1 = tk.Label(window, background="green", fg="black", text="Name :", width=10, height=1,
                  font=('Helvetica', 16))
label1.place(x=83, y=40)
std_name = tk.Entry(window, background="yellow", fg="black", width=25, font=('Helvetica', 14))
std_name.place(x=280, y=41)
label2 = tk.Label(window, background="green", fg="black", text="Matric Number :", width=14, height=1,
                  font=('Helvetica', 16))
label2.place(x=100, y=90)
std_number = tk.Entry(window, background="yellow", fg="black", width=25, font=('Helvetica', 14))
std_number.place(x=280, y=91)

clearBtn1 = tk.Button(window, background="red", command=clear_name, fg="white", text="CLEAR", width=8, height=1,
                      activebackground="red", font=('Helvetica', 10))
clearBtn1.place(x=580, y=42)
clearBtn2 = tk.Button(window, background="red", command=clear_matric_number, fg="white", text="CLEAR", width=8,
                      activebackground="red", height=1, font=('Helvetica', 10))
clearBtn2.place(x=580, y=92)

label3 = tk.Label(window, background="green", fg="red", text="Notification", width=10, height=1,
                  font=('Helvetica', 20, 'underline'))
label3.place(x=320, y=155)
label4 = tk.Label(window, background="yellow", fg="black", width=55, height=4, font=('Helvetica', 14, 'italic'))
label4.place(x=95, y=205)

takeImageBtn = tk.Button(window, command=capture_image, background="yellow", fg="black", text="CAPTURE IMAGE",
                         activebackground="red", width=15, height=3, font=('Helvetica', 12))
takeImageBtn.place(x=130, y=360)

trainImageBtn = tk.Button(window, command=train_images, background="yellow", fg="black", text="TRAIN IMAGE",
                          activebackground="red", width=15, height=3, font=('Helvetica', 12))
trainImageBtn.place(x=340, y=360)

trackImageBtn = tk.Button(window, command=track_images, background="yellow", fg="black", text="TRACK IMAGE",
                          activebackground="red", width=12, height=3, font=('Helvetica', 12))
trackImageBtn.place(x=550, y=360)

window.mainloop()
