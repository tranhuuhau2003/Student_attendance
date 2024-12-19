import os
import unicodedata
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
from functions import capture_image, train_images, track_images

def remove_accents(input_str):
    """
    Chuyển chuỗi có dấu thành không dấu.
    """
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

        # Danh sách sinh viên đã đăng ký khuôn mặt
        self.registered_students = {}

        # Treeview Data
        self.tree_data = None

        # Tiêu đề chính
        self.title_label = tk.Label(root, text="HỆ THỐNG ĐIỂM DANH SINH VIÊN BẰNG NHẬN DIỆN KHUÔN MẶT",
                                    font=("Arial", 16, "bold"), bg="#CCFFFF", fg="#000080")
        self.title_label.place(x=100, y=100, width=800, height=40)

        # Dropdown chọn lớp
        self.selected_class = tk.StringVar()
        self.selected_class.set("Chọn lớp")
        self.class_dropdown = ttk.Combobox(
            root, textvariable=self.selected_class, state="readonly", font=("Arial", 10))
        self.class_dropdown.bind("<<ComboboxSelected>>", self.on_class_selected)  # Gắn sự kiện khi chọn lớp

        # Nút Thêm Khuôn Mặt
        self.add_face_button = tk.Button(root, text="THÊM KHUÔN MẶT", command=self.open_add_face_window,
                                         background="#3399FF", fg="white", font=("Arial", 8))

        # Nút Điểm Danh
        self.track_button = tk.Button(root, text="ĐIỂM DANH", command=self.track_students,
                                      background="#3399FF", fg="white", font=("Arial", 8))

        # Sắp xếp giao diện dropdown và nút chung một hàng
        self.class_dropdown.place(x=150, y=200, width=300, height=35)
        self.add_face_button.place(x=480, y=200, width=150, height=35)
        self.track_button.place(x=680, y=200, width=150, height=35)

        self.update_class_dropdown()
        self.load_registered_students()

    def update_class_dropdown(self):
        """
        Lấy danh sách tên lớp từ các tệp Excel trong thư mục Data và cập nhật vào dropdown.
        """
        data_dir = "Data"
        if os.path.exists(data_dir):
            class_files = [f for f in os.listdir(data_dir) if f.endswith(".xlsx")]
            class_names = [os.path.splitext(f)[0] for f in class_files]
            self.class_dropdown["values"] = class_names
        else:
            messagebox.showerror("Lỗi", "Thư mục Data không tồn tại.")

    def load_registered_students(self):
        """
        Đọc danh sách sinh viên đã đăng ký khuôn mặt từ file studentDetailss.csv.
        """
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
        """
        Hàm xử lý khi người dùng chọn một lớp từ dropdown.
        """
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
            self.df = self.df.fillna("")  # Điền giá trị rỗng cho các ô null
            self.df = self.df.astype(str)  # Chuyển tất cả dữ liệu sang dạng chuỗi

            self.map_mssv_to_id()  # Thực hiện ánh xạ

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải file Excel của lớp đã chọn: {e}")
            self.df = None
            self.mssv_to_id = {}
            self.id_to_mssv = {}

    def map_mssv_to_id(self):
        """
        Ánh xạ MSSV -> ID và ID -> MSSV từ DataFrame hiện tại.
        """
        try:
            if self.df is None or "MSSV" not in self.df.columns:
                raise ValueError("Không tìm thấy cột MSSV trong dữ liệu lớp học.")
            self.mssv_to_id = {mssv: idx for idx, mssv in enumerate(self.df["MSSV"], start=1)}
            self.id_to_mssv = {v: k for k, v in self.mssv_to_id.items()}
            print("Ánh xạ MSSV -> ID đã được cập nhật:", self.mssv_to_id)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể ánh xạ MSSV -> ID: {e}")

    def update_treeview_with_registered_faces(self, treeview, dataframe, registered_students):
        """
        Hiển thị dữ liệu trong Treeview và tô màu cho các sinh viên đã đăng ký khuôn mặt (kiểm tra MSSV sau khi giải mã ID).
        """
        treeview.delete(*treeview.get_children())  # Xóa các hàng cũ
        treeview["columns"] = list(dataframe.columns)
        treeview["show"] = "headings"

        # Cấu hình cột
        for column in dataframe.columns:
            treeview.heading(column, text=column)
            treeview.column(column, width=120, anchor='center')

        # Duyệt từng sinh viên trong DataFrame
        for idx, row in dataframe.iterrows():
            mssv = row["MSSV"].strip()  # MSSV từ file Excel lớp học
            name = row["Họ và Tên"].strip()  # Họ và Tên từ file Excel lớp học
            name_no_accents = remove_accents(name.lower())  # Chuyển tên sang không dấu để so sánh

            # Kiểm tra xem MSSV có trong danh sách đã đăng ký không
            student_id = self.mssv_to_id.get(mssv)  # Lấy ID từ MSSV
            if student_id is not None:
                registered_name = registered_students.get(str(student_id))  # Tìm tên đã đăng ký từ ID
                matched = registered_name == name_no_accents
            else:
                matched = False

            # Áp dụng tag dựa trên trạng thái đã đăng ký
            tag = "registered" if matched else ("even" if idx % 2 == 0 else "odd")
            values = list(row)
            treeview.insert("", "end", values=values, tags=(tag,))

            print(
                f"MSSV: {mssv}, ID: {student_id}, Tên không dấu: {name_no_accents}, Tên đã đăng ký: {registered_name}, Trạng thái: {matched}")

        # Định nghĩa style cho các tag
        treeview.tag_configure("registered", background="#90EE90")  # Màu xanh nhạt cho sinh viên đã đăng ký
        treeview.tag_configure("even", background="#F5F5F5")  # Hàng chẵn có nền xám nhạt
        treeview.tag_configure("odd", background="#FFFFFF")  # Hàng lẻ có nền trắng

    def open_add_face_window(self):
        selected_class = self.selected_class.get()
        if selected_class == "Chọn lớp":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một lớp trước khi thêm khuôn mặt.")
            return

        self.root.withdraw()

        add_face_window = tk.Toplevel(self.root)
        add_face_window.title("THÊM KHUÔN MẶT")
        add_face_window.geometry("1400x750+70+15")
        add_face_window.configure(background='#CCFFFF')

        def on_close():
            add_face_window.destroy()
            self.root.deiconify()

        add_face_window.protocol("WM_DELETE_WINDOW", on_close)

        # Treeview hiển thị danh sách sinh viên
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
                mssv = row_values[0]  # MSSV được giả định là cột đầu tiên
                name = row_values[1]  # Họ và Tên được giả định là cột thứ hai
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

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
