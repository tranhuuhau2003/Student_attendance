import tkinter as tk
from functions import clear_field, capture_image, train_images, track_images

window = tk.Tk()
window.title("STUDENT ATTENDANCE USING FACE RECOGNITION SYSTEM")
window.geometry('800x500')
window.configure(background='green')

# Widgets
label1 = tk.Label(window, background="green", fg="black", text="Name :", width=10, height=1, font=('Helvetica', 16))
label1.place(x=83, y=40)
std_name = tk.Entry(window, background="yellow", fg="black", width=25, font=('Helvetica', 14))
std_name.place(x=280, y=41)

label2 = tk.Label(window, background="green", fg="black", text="Matric Number :", width=14, height=1, font=('Helvetica', 16))
label2.place(x=100, y=90)
std_number = tk.Entry(window, background="yellow", fg="black", width=25, font=('Helvetica', 14))
std_number.place(x=280, y=91)

label3 = tk.Label(window, background="green", fg="red", text="Notification", width=10, height=1, font=('Helvetica', 20, 'underline'))
label3.place(x=320, y=155)
label4 = tk.Label(window, background="yellow", fg="black", width=55, height=4, font=('Helvetica', 14, 'italic'))
label4.place(x=95, y=205)

# Buttons
tk.Button(window, text="CLEAR", command=lambda: clear_field(std_name, label4), background="red", fg="white", width=8).place(x=580, y=42)
tk.Button(window, text="CLEAR", command=lambda: clear_field(std_number, label4), background="red", fg="white", width=8).place(x=580, y=92)
tk.Button(window, text="CAPTURE IMAGE", command=lambda: capture_image(std_name, std_number, label4), background="yellow", width=15).place(x=130, y=360)
tk.Button(window, text="TRAIN IMAGE", command=lambda: train_images(label4), background="yellow", width=15).place(x=340, y=360)
tk.Button(window, text="TRACK IMAGE", command=lambda: track_images(label4), background="yellow", width=12).place(x=550, y=360)

window.mainloop()
