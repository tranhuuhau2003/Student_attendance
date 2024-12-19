import os
import unicodedata
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
from PIL import Image, ImageTk

from functions import capture_image, train_images, track_images

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HỆ THỐNG ĐIỂM DANH SINH VIÊN BẰNG NHẬN DIỆN KHUÔN MẶT")
        self.root.geometry("1000x500+250+100")
        self.root.configure(background='#CCFFFF')
        self.root.option_add('*Font', 'Arial 10')

        # Biến lưu file Excel, DataFrame, và ánh xạ MSSV <-> ID
        self.excel_file = None
        self.df = None
        self.mssv_to_id = {}
        self.id_to_mssv = {}

        self.registered_students = {}

        # Treeview Data
        self.tree_data = None

        self.title_label = tk.Label(root, text="HỆ THỐNG ĐIỂM DANH SINH VIÊN BẰNG NHẬN DIỆN KHUÔN MẶT",
                                    font=("Arial", 16, "bold"), bg="#CCFFFF", fg="#000080")
        self.title_label.place(x=100, y=100, width=800, height=40)

        self.selected_class = tk.StringVar()
        self.selected_class.set("Chọn lớp")
        self.class_dropdown = ttk.Combobox(
            root, textvariable=self.selected_class, state="readonly", font=("Arial", 10))
        self.class_dropdown.bind("<<ComboboxSelected>>", self.on_class_selected)  # Gắn sự kiện khi chọn lớp

        self.add_face_button = tk.Button(root, text="CẬP NHẬT KHUÔN MẶT", command=self.open_add_face_window,
                                         background="#3399FF", fg="white", font=("Arial", 8))

        self.track_button = tk.Button(root, text="ĐIỂM DANH", command=self.track_students,
                                      background="#3399FF", fg="white", font=("Arial", 8))

        self.history_button = tk.Button(root, text="LỊCH SỬ ĐIỂM DANH", command=self.open_recognized_images_folder,
                                        background="#3399FF", fg="white", font=("Arial", 8))

        self.class_dropdown.place(x=120, y=200, width=200, height=35)
        self.add_face_button.place(x=350, y=200, width=150, height=35)
        self.track_button.place(x=550, y=200, width=150, height=35)
        self.history_button.place(x=730, y=200, width=180, height=35)

        self.update_class_dropdown()
        self.load_registered_students()

    def open_recognized_images_folder(self):
        recognized_images_dir = "RecognizedImages"

        def search_images():
            keyword = remove_accents(search_entry.get().strip().lower())
            for widget in frame.winfo_children():
                widget.destroy()

            filtered_images = [
                img for img in images if keyword in remove_accents(os.path.basename(img).lower())
            ]
            if not filtered_images:
                messagebox.showinfo("Thông báo", "Không tìm thấy kết quả nào khớp với từ khóa.")
                return

            display_images(filtered_images)

        def display_images(image_list):
            row, col = 0, 0
            for img_path in image_list:
                try:
                    img = Image.open(img_path)
                    img = img.resize((100, 100))
                    photo = ImageTk.PhotoImage(img)
                    self.img_objects.append(photo)

                    lbl_img = tk.Label(frame, image=photo, bg='#CCFFFF')
                    lbl_img.grid(row=row * 2, column=col, padx=10, pady=5)

                    img_name = os.path.basename(img_path)  # Lấy tên ảnh từ đường dẫn
                    lbl_name = tk.Label(frame, text=img_name, bg='#CCFFFF', fg='#003366', font=("Arial", 8))
                    lbl_name.grid(row=row * 2 + 1, column=col, padx=10, pady=5)

                    col += 1
                    if col >= max_columns:
                        col = 0
                        row += 1
                except Exception as e:
                    print(f"Lỗi khi mở ảnh {img_path}: {e}")

        try:
            if not os.path.exists(recognized_images_dir):
                messagebox.showinfo("Thông báo", "Chưa có ảnh nào trong thư mục lịch sử điểm danh.")
                return

            history_window = tk.Toplevel(self.root)
            history_window.title("Lịch sử điểm danh")
            history_window.geometry("1000x500+250+100")
            history_window.configure(background='#CCFFFF')

            search_frame = tk.Frame(history_window, bg='#CCFFFF')
            search_frame.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(search_frame, text="Tìm kiếm:", bg='#CCFFFF', fg='#003366', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
            search_entry = tk.Entry(search_frame, font=("Arial", 10), width=40)
            search_entry.pack(side=tk.LEFT, padx=5)
            search_button = tk.Button(search_frame, text="Tìm", command=search_images, bg="#007BFF", fg="white",
                                      font=("Arial", 10))
            search_button.pack(side=tk.LEFT, padx=5)

            canvas = tk.Canvas(history_window, bg='#CCFFFF', scrollregion=(0, 0, 1200, 2000))
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar = ttk.Scrollbar(history_window, orient=tk.VERTICAL, command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.configure(yscrollcommand=scrollbar.set)

            frame = tk.Frame(canvas, bg='#CCFFFF')
            canvas.create_window((0, 0), window=frame, anchor='nw')

            images = [os.path.join(recognized_images_dir, f) for f in os.listdir(recognized_images_dir) if
                      f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            print("Danh sách ảnh:", images)

            if not images:
                messagebox.showinfo("Thông báo", "Không có ảnh nào trong thư mục lịch sử điểm danh.")
                history_window.destroy()
                return

            self.img_objects = []
            max_columns = 4
            display_images(images)

            frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị ảnh: {e}")

    def update_class_dropdown(self):
        data_dir = "Data"
        if os.path.exists(data_dir):
            class_files = [f for f in os.listdir(data_dir) if f.endswith(".xlsx")]
            class_names = [os.path.splitext(f)[0] for f in class_files]
            self.class_dropdown["values"] = class_names
        else:
            messagebox.showerror("Lỗi", "Thư mục Data không tồn tại.")

    def load_registered_students(self):
        try:
            file_path = "Excels/studentDetailss.csv"
            if not os.path.exists(file_path):
                return

            df_registered = pd.read_csv(file_path)
            for _, row in df_registered.iterrows():
                student_id = str(row["ID"])
                student_name = remove_accents(row["NAME"].strip().lower())
                self.registered_students[student_id] = student_name

            print(self.registered_students)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách sinh viên đã đăng ký: {e}")

    def on_class_selected(self, event):
        selected_class = self.selected_class.get()
        if selected_class == "Chọn lớp":
            self.df = None
            self.mssv_to_id = {}
            self.id_to_mssv = {}
            return

        try:
            file_path = os.path.join("Data", f"{selected_class}.xlsx")
            if not os.path.exists(file_path):
                raise FileNotFoundError("File Excel của lớp không tồn tại.")

            self.df = pd.read_excel(file_path, engine='openpyxl')
            self.df = self.df.fillna("")
            self.df = self.df.astype(str)

            self.map_mssv_to_id()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải file Excel của lớp đã chọn: {e}")
            self.df = None
            self.mssv_to_id = {}
            self.id_to_mssv = {}

    def map_mssv_to_id(self):
        try:
            if self.df is None or "MSSV" not in self.df.columns:
                raise ValueError("Không tìm thấy cột MSSV trong dữ liệu lớp học.")
            self.mssv_to_id = {mssv: idx for idx, mssv in enumerate(self.df["MSSV"], start=1)}
            self.id_to_mssv = {v: k for k, v in self.mssv_to_id.items()}
            print("Ánh xạ MSSV -> ID đã được cập nhật:", self.mssv_to_id)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể ánh xạ MSSV -> ID: {e}")

    def update_treeview_with_registered_faces(self, treeview, dataframe, registered_students):
        treeview.delete(*treeview.get_children())  # Xóa các hàng cũ
        treeview["columns"] = list(dataframe.columns)
        treeview["show"] = "headings"

        # Cấu hình cột
        for column in dataframe.columns:
            treeview.heading(column, text=column)
            treeview.column(column, width=120, anchor='center')

        for idx, row in dataframe.iterrows():
            mssv = row["MSSV"].strip()
            name = row["Họ và Tên"].strip()
            name_no_accents = remove_accents(name.lower())

            student_id = self.mssv_to_id.get(mssv)
            if student_id is not None:
                registered_name = registered_students.get(str(student_id))
                matched = registered_name == name_no_accents
            else:
                matched = False

            tag = "registered" if matched else ("even" if idx % 2 == 0 else "odd")
            values = list(row)
            treeview.insert("", "end", values=values, tags=(tag,))

            print(
                f"MSSV: {mssv}, ID: {student_id}, Tên không dấu: {name_no_accents}, Tên đã đăng ký: {registered_name}, Trạng thái: {matched}")

        # Định nghĩa style cho các tag
        treeview.tag_configure("registered", background="#90EE90")
        treeview.tag_configure("even", background="#F5F5F5")
        treeview.tag_configure("odd", background="#FFFFFF")

    def open_add_face_window(self):
        selected_class = self.selected_class.get()
        if selected_class == "Chọn lớp":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một lớp trước khi thêm khuôn mặt.")
            return

        self.root.withdraw()

        add_face_window = tk.Toplevel(self.root)
        add_face_window.title("CẬP NHẬT KHUÔN MẶT")
        add_face_window.geometry("1400x750+70+15")
        add_face_window.configure(background='#CCFFFF')

        def on_close():
            add_face_window.destroy()
            self.root.deiconify()

        add_face_window.protocol("WM_DELETE_WINDOW", on_close)

        tree = ttk.Treeview(add_face_window)
        tree_width = 1300
        tree_height = 600
        tree_x = (1400 - tree_width) // 2
        tree_y = 50
        tree.place(x=tree_x, y=tree_y, width=tree_width, height=tree_height)

        label_title = tk.Label(
            add_face_window,
            text=f"Danh sách sinh viên của lớp {selected_class}",
            font=("Arial", 16, "bold"),
            background="#CCFFFF",
            foreground="#003366"
        )
        label_title.place(x=tree_x, y=tree_y - 40)

        self.update_treeview_with_registered_faces(tree, self.df, self.registered_students)

        tk.Button(add_face_window, text="CẬP NHẬT KHUÔN MẶT", command=lambda: self.update_face(tree),
                  background="#3399FF", width=25).place(x=600, y=680)

    def update_face(self, tree):
        selected_item = tree.selection()
        if selected_item:
            for item in selected_item:
                row_values = tree.item(item, 'values')
                mssv = row_values[0]
                name = row_values[1]
                try:
                    student_id = self.mssv_to_id[mssv]
                    name_no_accents = remove_accents(name)

                    capture_image(name_no_accents, student_id)
                    train_images()

                    # Cập nhật lại danh sách sinh viên đã đăng ký
                    self.load_registered_students()

                    # Làm mới Treeview
                    self.update_treeview_with_registered_faces(tree, self.df, self.registered_students)

                    messagebox.showinfo("Thành công", f"Khuôn mặt của {name} đã được cập nhật và huấn luyện.",
                                        icon='info')
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể cập nhật khuôn mặt: {e}", icon='error')
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một sinh viên!", icon='warning')

    def track_students(self):
        selected_class = self.selected_class.get()
        if selected_class == "Chọn lớp":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một lớp trước khi điểm danh.")
            return

        try:
            track_images(selected_class, self.id_to_mssv)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi điểm danh: {e}", icon='error')



if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
