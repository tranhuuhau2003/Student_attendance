
# 📷 Student Attendance System using Face Recognition

A Python-based attendance management system that utilizes **facial recognition** to automate the process of student attendance tracking. This project leverages **OpenCV** and **Haar Cascade** classifiers for face detection, allowing real-time face recognition and attendance logging into Excel sheets.

---

## 🚀 Features

- 📸 **Real-time Face Detection** using webcam
- 🧠 **Face Recognition** using image training
- 📂 **Attendance Logging** in Excel files
- 🧑‍🎓 Student data management
- 🖼️ Image capture and training functionality
- 🖥️ Simple GUI interface using Tkinter

---

## 🧰 Tech Stack

- **Python 3**
- **OpenCV**
- **Tkinter** (for GUI)
- **Pandas** (for Excel handling)
- **Haar Cascade Classifier** (for face detection)

---

## 📁 Project Structure

```
├── Data/                  # Student details or metadata
├── TrainingImages/        # Stored images for training the model
├── RecognizedImages/      # Saved images of recognized faces
├── Excels/                # Attendance Excel files
├── haarcascade_frontalface_default.xml
├── functions.py           # Core logic for face recognition
├── gui.py                 # GUI implementation using Tkinter
├── Trainner.yml           # Face trainer data (LBPH recognizer)
├── requirements.txt       # Required Python libraries
```

---

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tranhuuhau2003/Student_attendance.git
   cd Student_attendance
   ```

2. **Create and activate virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ How to Use

1. **Run the GUI**
   ```bash
   python gui.py
   ```

2. **Main Functionalities:**
   - **Register Student**: Capture images of new students.
   - **Train Model**: Train the face recognition model with captured images.
   - **Take Attendance**: Recognize faces in real time and log attendance.
   - **View Attendance**: Open and review attendance Excel files.

---

## 🧪 Sample Data

Place student training images in the `TrainingImages/` folder. Images should follow the format:
```
<studentID>.<name>.<count>.jpg
```

---

## 📊 Attendance Output

Attendance is saved in the `Excels/` directory with filenames like:
```
Attendance_YYYY-MM-DD_HH-MM-SS.xls
```

Each file includes:
- Student ID
- Name
- Date
- Time

---

## 🤝 Contributing

Contributions are welcome! Please fork this repo and open a pull request with your improvements or bug fixes.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

Developed by [Hau Tran](https://github.com/tranhuuhau2003)

---

## ⭐️ If you like this project, consider giving it a star on GitHub!
