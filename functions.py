import re
import cv2
import csv
import os
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import time
from tkinter import messagebox
import unicodedata


def is_valid_name(name):
    return re.fullmatch(r'[A-Za-zÀ-ỹ\s]+', name) is not None


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


def capture_image(name, student_id):
    try:
        if not is_valid_name(name):
            messagebox.showerror("Lỗi", "Tên không hợp lệ, vui lòng chỉ nhập chữ cái!")
            return
        name_no_accents = remove_accents(name)

        folder_path = "TrainingImages"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            messagebox.showerror("Lỗi", "Không thể mở camera. Vui lòng kiểm tra kết nối!")
            return

        harcascade_path = "haarcascade_frontalface_default.xml"
        if not os.path.exists(harcascade_path):
            messagebox.showerror("Lỗi", "File Haarcascade không tồn tại!")
            cam.release()
            return
        detector = cv2.CascadeClassifier(harcascade_path)

        sample_num = 0
        while True:
            ret, img = cam.read()
            if not ret:
                messagebox.showerror("Lỗi", "Không thể đọc dữ liệu từ camera.")
                break

            img = cv2.flip(img, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.1, 3)

            for (x, y, w, h) in faces:
                sample_num += 1
                image_path = os.path.join(folder_path, f"{name_no_accents}.{student_id}.{str(sample_num)}.jpg")
                cv2.imwrite(image_path, gray[y:y + h, x:x + w])
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.imshow('FACE RECOGNIZER', img)

            if cv2.waitKey(100) & 0xFF == ord('q') or sample_num >= 50:
                break

        cam.release()
        cv2.destroyAllWindows()

        if sample_num == 0:
            messagebox.showwarning("Cảnh báo", "Không chụp được khuôn mặt nào. Vui lòng thử lại!")
            return

        csv_file_path = 'Excels/studentDetailss.csv'
        if not os.path.exists('Excels'):
            os.makedirs('Excels')

        with open(csv_file_path, 'a+', newline='', encoding='utf-8-sig') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([student_id, name_no_accents])

    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")


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
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        faces, ids = get_images_and_labels("TrainingImages")
        recognizer.train(faces, np.array(ids))
        recognizer.save("Trainner.yml")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi huấn luyện hình ảnh: {str(e)}")


def track_images(class_name, id_to_mssv):
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("Trainner.yml")
        harcascade_path = "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(harcascade_path)

        student_details_path = "Excels/studentDetailss.csv"
        if not os.path.exists(student_details_path):
            messagebox.showerror("Lỗi", "File danh sách sinh viên không tồn tại!")
            return
        df = pd.read_csv(student_details_path)

        recognized_folder = "RecognizedImages"
        if not os.path.exists(recognized_folder):
            os.makedirs(recognized_folder)

        class_file_path = f"Data/{class_name}.xlsx"
        if not os.path.exists(class_file_path):
            messagebox.showerror("Lỗi", f"File điểm danh của lớp {class_name} không tồn tại!")
            return

        class_df = pd.read_excel(class_file_path)
        class_df['MSSV'] = class_df['MSSV'].astype(str)  # Chuyển toàn bộ MSSV trong DataFrame thành chuỗi

        print(class_df)

        current_date = datetime.datetime.now().strftime('%d-%m-%Y')

        if current_date not in class_df.columns:
            print(f"Ngày {current_date} chưa có trong file, thêm mới cột vào DataFrame.")
            class_df[current_date] = None
        else:
            print(f"Ngày {current_date} đã tồn tại trong file.")

        font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        cam = cv2.VideoCapture(0)

        while True:
            ret, img = cam.read()
            if not ret:
                messagebox.showerror("Lỗi", "Không thể đọc dữ liệu từ camera.")
                break

            img = cv2.flip(img, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 3)

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                student_id, conf = recognizer.predict(gray[y:y + h, x:x + w])

                if conf < 60:
                    ts = time.time()
                    date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                    time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M')

                    student_mssv = id_to_mssv.get(student_id, "Unknown")  # Lấy MSSV từ ID
                    student_name = df.loc[df['ID'] == student_id]['NAME'].values[0]

                    print(f"Đã nhận diện: MSSV: {student_mssv}, Tên: {student_name}")

                    # Đảm bảo cột ngày có kiểu dữ liệu là object trước khi gán
                    if class_df[current_date].dtype != 'object':
                        class_df[current_date] = class_df[current_date].astype('object')

                    class_df.loc[class_df['MSSV'] == student_mssv, current_date] = 'X'

                    # Ghi file Excel ngay sau khi nhận diện
                    class_df.to_excel(class_file_path, index=False)

                    # Lưu ảnh vào thư mục riêng
                    recognized_image_path = os.path.join(
                        recognized_folder, f"{student_id}_{student_name}_{date}_{time_stamp.replace(':', 'h')}.jpg"
                    )
                    cv2.imwrite(recognized_image_path, img)

                    print(f"Đã cập nhật điểm danh cho MSSV: {student_mssv} vào ngày {current_date}.")

                else:  # Nếu không nhận diện được
                    student_name = "Unknown"

                cv2.putText(img, str(student_name), (x, y + h + 20), font, 1, (255, 255, 255), 2)
                cv2.imshow('FACE RECOGNIZER', img)

            if cv2.waitKey(1000) == ord('q'):  # Nhấn 'q' để thoát
                break

        cam.release()
        cv2.destroyAllWindows()

        messagebox.showinfo("Thành công", f"Điểm danh cho lớp {class_name} đã được cập nhật thành công.")

    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi nhận diện: {str(e)}")
