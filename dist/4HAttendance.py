"""Copyright (c) [2023 Jared Vaughn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime
import csv
import re
import os

class Student:
    student_counter = 0

    def __init__(self, student_name, input_time):
        Student.student_counter += 1
        self.student_num = Student.student_counter
        self.student_name = student_name
        self.input_time = input_time
        self.sign_out_name = ""
        self.output_time = ""

    def is_signed_out(self):
        return bool(self.sign_out_name and self.output_time)
    
    
    def formatted_input_time(self):
        return self.input_time.strftime("%I:%M %p")
    
    def formatted_output_time(self):
        return self.output_time.strftime("%I:%M %p") if self.output_time else ""

class StudentManager:
    def __init__(self):
        self.students = []

    def add_student(self, student_name, input_time):
        new_student = Student(student_name, input_time)
        self.students.append(new_student)

    def sign_out_student(self, selected_student, sign_out_name):
        selected_student.sign_out_name = sign_out_name
        selected_student.output_time = datetime.now().strftime("%H:%M:%S")

    def export_list(self):
        if all(student.is_signed_out() for student in self.students):
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = f"4-H Attendance {datetime.now().strftime('%m-%d')}.csv"
            filepath = os.path.join(desktop_path, filename)
            with open(filepath, "w", newline="") as csvfile:
                fieldnames = [" ", "Name", "In", "Pick-Up", "Out"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for student in self.students:
                    writer.writerow({
                        " ": student.student_num,
                        "Name": student.student_name,
                        "In": student.input_time,
                        "Pick-Up": student.sign_out_name,
                        "Out": student.output_time
                    })

class EditStudentDialog:
    def __init__(self, parent, student_manager, on_edit_callback):
        self.parent = parent
        self.student_manager = student_manager
        self.on_edit_callback = on_edit_callback
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Student")

        self.selected_student_var = tk.StringVar()
        self.selected_student_var.set("Select a student")
        student_names = [student.student_name for student in self.student_manager.students]
        self.student_menu = ttk.Combobox(self.dialog, textvariable=self.selected_student_var, values=student_names)
        self.student_menu.pack(padx=10, pady=10)

        self.edit_name_button = tk.Button(self.dialog, text="Edit Name", command=self.edit_name)
        self.edit_name_button.pack(pady=5)
        
        self.edit_signout_button = tk.Button(self.dialog, text="Edit Sign-out", command=self.edit_signout)
        self.edit_signout_button.pack(pady=5)
        
        self.remove_all_button = tk.Button(self.dialog, text="Remove All", command=self.remove_all)
        self.remove_all_button.pack(pady=5)

        self.cancel_button = tk.Button(self.dialog, text="Cancel", command=self.dialog.destroy)
        self.cancel_button.pack(pady=5)
        

    def edit_name(self):
        selected_student_name = self.selected_student_var.get()
        selected_student = next((student for student in self.student_manager.students if student.student_name == selected_student_name), None)
        if selected_student:
            new_name = simpledialog.askstring("Edit Name", f"Enter a new name for {selected_student_name}:")
            if new_name:
                selected_student.student_name = new_name
                messagebox.showinfo("Success", f"Name for {selected_student_name} edited successfully!")
                self.dialog.destroy()
                self.on_edit_callback()

    def edit_signout(self):
        selected_student_name = self.selected_student_var.get()
        selected_student = next((student for student in self.student_manager.students if student.student_name == selected_student_name), None)
        if selected_student and selected_student.is_signed_out():
            reset_signout = messagebox.askyesno("Edit Sign-out", f"Do you want to reset the sign-out for {selected_student_name}?")
            if reset_signout:
                selected_student.sign_out_name = ""
                selected_student.output_time = ""
                messagebox.showinfo("Success", f"Sign-out for {selected_student_name} reset successfully!")
                self.dialog.destroy()
                self.on_edit_callback()

class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("4H Attendance " + datetime.now().strftime("%m-%d"))
        self.root.configure(bg="dark green")  # Set background color of the main window
        
        # Current Date
        self.today_label = tk.Label(self.root, text="", font=("Helvetica", 12))
        self.today_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.today_label["text"] = self.get_today_info()
        
        # Current Time
        self.time_label = tk.Label(self.root, text="", font=("Helvetica", 16))
        self.time_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        self.update_time_label()
        self.root.columnconfigure(1, weight=1)

        self.style = ttk.Style()
        self.style.configure("SignedOut.TLabel", background="dark green")
        self.style.configure("TButton", font=("TkDefaultFont", 14))  # Increase font size by 20%
        self.style.configure("TLabel", font=("TkDefaultFont", 14))  # Increase font size by 20%

        self.student_manager = StudentManager()

        self.menu_var = tk.StringVar()
        self.menu_var.set("Select an option")

        self.menu = ttk.Combobox(self.root, textvariable=self.menu_var, values=["Select an option", "Add students", "Edit student", "Remove All", "Export list"])
        self.menu.grid(row=0, column=0, padx=10, pady=10)

        self.students_listbox = ttk.Treeview(self.root, columns=["student_num", "student_name", "input_time", "signed_out"], show="headings", height = 30)
        self.students_listbox.heading("student_num", text="Student #", anchor=tk.W, command=self.sort_by_student_num)
        self.students_listbox.heading("student_name", text="Student Name", anchor=tk.W, command=self.sort_by_student_name)
        self.students_listbox.heading("input_time", text="Input Time", anchor=tk.W, command=self.sort_by_input_time)
        self.students_listbox.heading("signed_out", text="Signed Out", anchor=tk.W, command=self.sort_by_signed_out)

        self.students_listbox.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W + tk.E)
        self.students_listbox.bind("<ButtonRelease-1>", self.sign_out_clicked)

        # Load and display the image from the /dist folder
        script_directory = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_directory, "Clover-with-transparent-background.png")
        self.img = tk.PhotoImage(file=image_path)
        
        new_width, new_height = 100, 100  # Replace with your desired dimensions
        self.re_img = self.img.subsample(
            int(self.img.width() / new_width),
            int(self.img.height() / new_height))
        
        self.img_label = tk.Label(self.root, image=self.re_img, bg="dark green")
        self.img_label.photo = self.re_img
        self.img_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.menu.bind("<<ComboboxSelected>>", self.handle_menu_selection)
        self.update_students_listbox()

    def handle_menu_selection(self, event):
        selected_option = self.menu_var.get()

        if selected_option == "Add students":
            self.add_students()
        elif selected_option == "Edit student":
            self.edit_student()
        elif selected_option == "Export list":
            self.export_list()
        elif selected_option == "Remove All":
            self.remove_all()

    def update_students_listbox(self):
        self.students_listbox.delete(*self.students_listbox.get_children())
        for student in self.student_manager.students:
            signed_out_text = student.sign_out_name if student.is_signed_out() else "No"
            tag = "SignedOut.TLabel" if student.is_signed_out() else ""
            self.students_listbox.insert("", "end", values=(student.student_num, student.student_name, student.formatted_input_time() , signed_out_text), tags=tag)

    def add_students(self):
        name_var = tk.StringVar()  # Create a StringVar to store the entered name
      ###  self.show_keyboard(name_var)  # Pass the StringVar to the show_keyboard method
        names_input = simpledialog.askstring("Add Students", "Enter student names (separated by commas):", parent=self.root)
        if names_input:
            names_list = [name.strip() for name in re.split(r',|\n', names_input) if name.strip()]
            current_time = datetime.now().strftime("%H:%M:%S")
            current_time_dt = datetime.strptime(current_time, "%H:%M:%S")
            for name in names_list:
                self.student_manager.add_student(name, current_time_dt)
            messagebox.showinfo("Success", "Students added successfully!")
            self.update_students_listbox()

    def sign_out_clicked(self, event):
        selected_item = self.students_listbox.selection()
        if selected_item:
            selected_student_index = int(self.students_listbox.item(selected_item, 'values')[0]) - 1
            selected_student = self.student_manager.students[selected_student_index]
            if not selected_student.is_signed_out():
                sign_out_name = simpledialog.askstring("Sign Out Students", f"Enter the name of the person signing out {selected_student.student_name}:")
                if sign_out_name:
                    self.student_manager.sign_out_student(selected_student, sign_out_name)
                    messagebox.showinfo("Success", f"{selected_student.student_name} signed out successfully!")
                    self.update_students_listbox()

                    # Check if all students are signed out
                    if all(student.is_signed_out() for student in self.student_manager.students):
                        self.export_list()
                  
                        '''
                        
                        
                        Attempting to use this with a touchscreen computer, however I am running into issues with the pop-up keyboard
                        
    def show_keyboard(self, name_var):
        # Create a custom keyboard window
        keyboard_window = tk.Toplevel(self.root)
        keyboard_window.title("Virtual Keyboard")

        # Define the keys of the virtual keyboard
        keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
            ['Space', 'Backspace', 'Enter']
        ]

        # Function to handle key press events
        def key_pressed(key):
            current_name = name_var.get()

            if key == 'Backspace':
                name_var.set(current_name[:-1])
            elif key == 'Space':
                name_var.set(current_name + ' ')
            elif key == 'Enter':
                keyboard_window.destroy()
            else:
                name_var.set(current_name + key)

        # Create buttons for each key
        for row, key_row in enumerate(keys):
            for col, key in enumerate(key_row):
                key_button = tk.Button(keyboard_window, text=key, width=5, height=2,
                                       command=lambda k=key: key_pressed(k))
                key_button.grid(row=row, column=col, padx=2, pady=2)

        # Entry widget to display the entered name
        name_var = tk.StringVar()
        entry = tk.Entry(keyboard_window, textvariable=name_var, font=("Helvetica", 12), justify='center')
        entry.grid(row=len(keys), columnspan=len(keys[0]), padx=10, pady=10)
        
        '''

    def export_list(self):
        self.student_manager.export_list()
        messagebox.showinfo("Success", "Student list exported to the desktop!")

    def edit_student(self):
        edit_dialog = EditStudentDialog(self.root, self.student_manager, self.update_students_listbox)
        
    def remove_all(self): 
        delete_all = messagebox.askyesno("Remove All", "Do you want to remove all youth from the list?")
        if delete_all:
            self.student_manager.students = []
            self.update_students_listbox()
            messagebox.showinfo("Success", "All names have been removed")
            
    def get_today_info(self):
        # Get today's date and day of the week
        today = datetime.now()
        date_string = today.strftime("%A, %B %d, %Y")
        return date_string
    
    def update_time_label(self):
        # Update the label text with the current time in 12-hour format
        current_time = datetime.now().strftime("%I:%M:%S %p")
        self.time_label["text"] = f"{current_time}"
        
        self.root.after(1000, self.update_time_label)
            
    def sort_by_student_num(self):
        # Implement sorting by student number
        pass

    def sort_by_student_name(self):
        # Implement sorting by student name
        pass

    def sort_by_input_time(self):
        # Implement sorting by input time
        pass

    def sort_by_signed_out(self):
        # Implement sorting by signed out status
        pass




if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    app.update_time_label()
    add_students_button = tk.Button(root, text="Add New Students", command=app.add_students)
    add_students_button.grid(row=1, column=1, padx=10, pady=10, sticky=tk.E)

    root.mainloop()

