import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
from tkcalendar import Calendar
import pymysql


def connect_db():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='A02032178a',
            database='clinic'
        )
        return connection
    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error connecting to database: {e}")
        return None

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Doctor Registration App")
        self.root.geometry("1000x800")
        self.root.resizable(False, False)


        self.main_menu_bg = PhotoImage(file="main_menu_bg.png")
        self.specialty_bg = PhotoImage(file="specialty_bg.png")
        self.date_time_bg = PhotoImage(file="date_time_bg.png")
        self.patient_details_bg = PhotoImage(file="patient_details_bg.png")
        self.check_appointment_bg = PhotoImage(file="check_appointment_bg.png")

        self.main_menu()

    def set_background(self, image):
        self.bg_label = tk.Label(self.root, image=image)
        self.bg_label.place(relwidth=1, relheight=1)

    def main_menu(self):
        self.clear_window()
        self.set_background(self.main_menu_bg)


        register_btn = tk.Button(self.root, text="Записаться к врачу", bg="lightblue", font=("Arial", 20),
                                 command=self.choose_specialty)
        register_btn.place(relx=0.5, rely=0.4, anchor="center", width=300, height=50)


        check_btn = tk.Button(self.root, text="Уточнить запись", bg="lightblue", font=("Arial", 20),
                              command=self.check_appointment)
        check_btn.place(relx=0.5, rely=0.5, anchor="center", width=300, height=50)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def choose_specialty(self):
        self.clear_window()
        self.set_background(self.specialty_bg)

        specialties = [
            "Офтальмолог", "Отоларинголог", "Невропатолог",
            "Ортопед", "Терапевт", "Кардиолог",
            "Гастроэнтеролог", "Сомнолог", "Онколог"
        ]

        frame = tk.Frame(self.root, bg="white")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        def select_specialty(specialty):
            self.selected_specialty = specialty
            self.choose_date_time()

        for i, specialty in enumerate(specialties):
            row, col = divmod(i, 3)
            tk.Button(frame, text=specialty, bg="lightblue", font=("Arial", 14),
                      command=lambda s=specialty: select_specialty(s)).grid(
                row=row, column=col, padx=10, pady=10, ipadx=10, ipady=10)

        back_btn = tk.Button(self.root, text="Назад", bg="lightblue", font=("Arial", 14), command=self.main_menu)
        back_btn.place(relx=0.5, rely=0.9, anchor="center", width=150, height=40)

    def choose_date_time(self):
        self.clear_window()
        self.set_background(self.date_time_bg)

        frame = tk.Frame(self.root, bg="white")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        date_label = tk.Label(frame, text="Выберите дату", font=("Arial", 16), bg="white")
        date_label.pack(pady=10)

        calendar = Calendar(frame, date_pattern='yyyy-mm-dd')
        calendar.pack(pady=5)

        time_label = tk.Label(frame, text="Выберите время", font=("Arial", 16), bg="white")
        time_label.pack(pady=10)

        time_frame = tk.Frame(frame, bg="white")
        time_frame.pack()

        available_times = [
            "8:00", "8:30", "9:00", "9:30", "10:00", "10:30",
            "11:00", "11:30", "12:00", "12:30", "13:00", "13:30"
        ]

        def check_availability(selected_time):
            selected_date = calendar.get_date()
            conn = connect_db()
            if conn:
                try:
                    with conn.cursor() as cursor:
                        query = """
                        SELECT COUNT(*) FROM patient
                        WHERE doctor = %s AND date = %s AND time = %s
                        """
                        cursor.execute(query, (self.selected_specialty, selected_date, selected_time))
                        result = cursor.fetchone()
                        if result[0] > 0:
                            messagebox.showwarning("Время занято", "Время забронировано. Выберите другое время.")
                        else:
                            self.selected_date = selected_date
                            self.selected_time = selected_time
                            self.enter_patient_details()
                except pymysql.MySQLError as e:
                    messagebox.showerror("Database Error", f"Error checking availability: {e}")
                finally:
                    conn.close()

        for time in available_times:
            tk.Button(time_frame, text=time, font=("Arial", 12),
                      command=lambda t=time: check_availability(t)).pack(
                side=tk.LEFT, padx=5, pady=5)

        back_btn = tk.Button(self.root, text="Назад", bg="lightblue", font=("Arial", 14), command=self.choose_specialty)
        back_btn.place(relx=0.5, rely=0.9, anchor="center", width=150, height=40)

    def enter_patient_details(self):
        self.clear_window()
        self.set_background(self.patient_details_bg)

        frame = tk.Frame(self.root, bg="white")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        fio_label = tk.Label(frame, text="Введите ФИО", font=("Arial", 16), bg="white")
        fio_label.pack(pady=10)

        fio_entry = tk.Entry(frame, font=("Arial", 14))
        fio_entry.pack(pady=5)

        phone_label = tk.Label(frame, text="Введите номер телефона", font=("Arial", 16), bg="white")
        phone_label.pack(pady=10)

        phone_entry = tk.Entry(frame, font=("Arial", 14))
        phone_entry.pack(pady=5)

        birthday_label = tk.Label(frame, text="Выберите дату рождения", font=("Arial", 16), bg="white")
        birthday_label.pack(pady=10)

        birthday_calendar = Calendar(frame, date_pattern='yyyy-mm-dd')
        birthday_calendar.pack(pady=5)

        def save_details():
            fio = fio_entry.get()
            phone = phone_entry.get()
            birthday = birthday_calendar.get_date()
            self.save_to_db(self.selected_specialty, self.selected_date, self.selected_time, fio, birthday, phone)

        submit_btn = tk.Button(frame, text="Сохранить", bg="lightblue", font=("Arial", 14), command=save_details)
        submit_btn.pack(pady=20)

        back_btn = tk.Button(self.root, text="Назад", bg="lightblue", font=("Arial", 14), command=self.choose_date_time)
        back_btn.place(relx=0.5, rely=0.9, anchor="center", width=150, height=40)

    def save_to_db(self, doctor, date, time, fio, birthday, phone):
        conn = connect_db()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO patient (doctor, date, time, fio, birthday, phone) VALUES (%s, %s, %s, %s, %s, %s)",
                        (doctor, date, time, fio, birthday, phone)
                    )
                    conn.commit()
                    self.show_appointment_summary(doctor, date, time, fio, birthday, phone)
            except pymysql.MySQLError as e:
                messagebox.showerror("Database Error", f"Error saving data: {e}")
            finally:
                conn.close()

    def show_appointment_summary(self, doctor, date, time, fio, birthday, phone):
        self.clear_window()
        self.set_background(self.main_menu_bg)

        frame = tk.Frame(self.root, bg="white")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        summary = f"""Ваш прием:
Врач: {doctor}
Дата: {date}
Время: {time}
ФИО: {fio}
Дата рождения: {birthday}
Телефон: {phone}"""

        tk.Label(frame, text=summary, font=("Arial", 14), justify=tk.LEFT, bg="white").pack(pady=10)

        back_btn = tk.Button(self.root, text="Назад", bg="lightblue", font=("Arial", 14), command=self.main_menu)
        back_btn.place(relx=0.5, rely=0.9, anchor="center", width=150, height=40)

    def check_appointment(self):
        self.clear_window()
        self.set_background(self.check_appointment_bg)

        frame = tk.Frame(self.root, bg="white")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        fio_label = tk.Label(frame, text="Введите ФИО", font=("Arial", 16), bg="white")
        fio_label.pack(pady=10)

        fio_entry = tk.Entry(frame, font=("Arial", 14))
        fio_entry.pack(pady=5)

        def search_appointments():
            fio = fio_entry.get()
            self.fetch_appointments(fio)

        search_btn = tk.Button(frame, text="Найти", bg="lightblue", font=("Arial", 14), command=search_appointments)
        search_btn.pack(pady=20)

        back_btn = tk.Button(self.root, text="Назад", bg="lightblue", font=("Arial", 14), command=self.main_menu)
        back_btn.place(relx=0.5, rely=0.9, anchor="center", width=150, height=40)

    def fetch_appointments(self, fio):
        conn = connect_db()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT doctor, date, time FROM patient WHERE fio = %s", (fio,))
                    appointments = cursor.fetchall()

                    if appointments:
                        self.display_appointments(appointments)
                    else:
                        messagebox.showwarning("Нет пациента", "Пациент не записан")
            except pymysql.MySQLError as e:
                messagebox.showerror("Database Error", f"Error fetching data: {e}")
            finally:
                conn.close()

    def display_appointments(self, appointments):
        self.clear_window()
        self.set_background(self.check_appointment_bg)

        frame = tk.Frame(self.root, bg="white")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        for appointment in appointments:
            tk.Label(frame, text=f"{appointment[0]} - {appointment[1]} - {appointment[2]}", font=("Arial", 14), bg="white").pack(pady=5)

        back_btn = tk.Button(self.root, text="Назад", bg="lightblue", font=("Arial", 14), command=self.main_menu)
        back_btn.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
