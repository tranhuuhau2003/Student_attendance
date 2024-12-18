import cv2
import csv
import os
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import time

def clear_field(entry_widget, label_widget):
    entry_widget.delete(0, 'end')
    label_widget.configure(text="")


def capture_image(std_name, std_number, label_widget):
    name = std_name.get()
    student_id = std_number.get()

    if name.isalpha():
        cam = cv2.VideoCapture(0)
        harcascade_path = "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascade_path)
        sample_num = 0

        while True:
            ret, img = cam.read()
            img = cv2.flip(img, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.1, 3)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                sample_num += 1
                cv2.imwrite(f"TrainingImages/{name}.{student_id}.{str(sample_num)}.jpg",
                            gray[y:y + h, x:x + h])
                cv2.imshow('FACE RECOGNIZER', img)
            if cv2.waitKey(100) & 0xFF == ord('q') or sample_num > 50:
                break

        cam.release()
        cv2.destroyAllWindows()
        res = f'Student details saved with:\nMatric number: {student_id} and Full Name: {name}'

        with open('Excels/studentDetailss.csv', 'a+') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([student_id, name])

        label_widget.configure(text=res)
    else:
        label_widget.configure(text="Enter correct Matric Number")


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


def train_images(label_widget):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, ids = get_images_and_labels("TrainingImages")
    recognizer.train(faces, np.array(ids))
    recognizer.save("Trainner.yml")
    label_widget.configure(text="Images Trained")


def track_images(label_widget):
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
        img = cv2.flip(img, 1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 3)

        for (x, y, w, h) in faces:
            tt = "Unknown"  # Giá trị mặc định cho tt
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            student_id, conf = recognizer.predict(gray[y:y + h, x:x + w])

            if conf < 60:
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M')
                student_name = df.loc[df['ID'] == student_id]['NAME'].values
                tt = f"{student_id}-{student_name}"

                attendance.loc[len(attendance)] = [student_id, student_name, date, time_stamp]
                with open('Excels/AttendanceFile.csv', 'a+') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow([student_id, student_name, date, time_stamp])
                label_widget.configure(text='ATTENDANCE UPDATED')

            else:
                label_widget.configure(text='ID UNKNOWN, ATTENDANCE NOT UPDATED')

            attendance.drop_duplicates(subset=['Id'], keep='first', inplace=True)
            cv2.putText(img, str(tt), (x, y + h - 10), font, 0.8, (255, 255, 255), 1)
            cv2.imshow('FACE RECOGNIZER', img)

        if cv2.waitKey(1000) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()