import sys
from pathlib import Path

#lock dashboard supaya tidak muncul banyak tab
lock_file = Path("app.lock")

if lock_file.exists():
    print("Application already running.")
    sys.exit()

# Buat file lock untuk memastikan hanya satu instance
lock_file.touch()

import cv2
import os
import sqlite3
import tkinter as tk
from tkinter import Tk, Label, Entry, Button, StringVar, Frame, messagebox, simpledialog
from PIL import Image, ImageTk
from collections import deque
from ultralytics import YOLO, solutions
from ultralytics.solutions import speed_estimation
from time import time
import numpy as np
from collections import defaultdict
#from ocr_library import process_image # ngga jadi dipake, proses dipindah ke webased javascrpt
from datetime import datetime
import math
import threading
import queue

#variable global untuk config
glob_integral = 0.00
glob_span_time = 0.00
glob_width_in_pixel = 900
glob_width_in_meter = 7 #meter
glob_actual_time = 5.00
glob_yolo_time = 15.00 
glob_calibration_factor = 2.0
glob_model = "yolov8x.pt"
#glob_slash = "/" #linux
glob_slash = "\\" #windows
glob_slash_html = "/" 

def get_current_time():
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H-%M-%S")

def recursive_output(current_string, repeat_count):
    # Base case: Jika repeat_count sudah 0, kembalikan current_string
    if repeat_count <= 0:
        return current_string
    else:
        # Rekursi: Tambahkan string baru ke current_string dan ulangi
        new_string = current_string + " " + get_current_time()
        return recursive_output(new_string, repeat_count - 1)

def detect_seatbelt(output_queue, frame, track_id, model_path="seat_belt_5.pt", retries=5):
    # Inisialisasi model YOLOv8
    model = YOLO(model_path)

    # Loop untuk mencoba deteksi dengan batasan retry
    for attempt in range(retries):
        # Melakukan deteksi menggunakan YOLOv8
        results = model.predict(source=frame)
        class_ids = results[0].boxes.cls.numpy().tolist()
        output_folder = 'database'+ glob_slash + 'static'+ glob_slash + 'Seatbelt'
        os.makedirs(output_folder, exist_ok=True)
        
        print(model.model.names)
        # Jika ada objek yang terdeteksi, lanjutkan dengan cropping        
        if len(results[0].boxes) > 0:
            cropped_image_paths = []

            for i, result in enumerate(results[0].boxes):
                # Dapatkan koordinat bounding box
                x1, y1, x2, y2 = map(int, result.xyxy[0])

                # Crop gambar berdasarkan bounding box
                save_frame = frame
                cropped_image = frame[y1:y2, x1:x2]
                print(model.model.names[int(class_ids[i])])
                
                if model.model.names[int(class_ids[i])] == 'NoSeatBelt':
                    text = "no-seatbelt"
                    #print(text)
                    output_queue.put((cropped_image, track_id, text))
                    return
            output_queue.put((None, track_id, ""))  # Indikasi bahwa tidak ada helm terdeteksi
        else:
            print(f"No objects detected on attempt {attempt + 1}. Retrying...")

    # Jika tidak ada objek yang terdeteksi setelah retries selesai
    print("No objects detected after maximum retries.")
    output_queue.put((None, track_id, ""))

def detect_helmet(output_queue, frame, track_id, model_path="helmet_9.pt", retries=5):
    # Inisialisasi model YOLOv8
    model = YOLO(model_path)

    # Loop untuk mencoba deteksi dengan batasan retry
    for attempt in range(retries):
        # Melakukan deteksi menggunakan YOLOv8
        results = model.predict(source=frame)
        class_ids = results[0].boxes.cls.numpy().tolist()
        print(model.model.names)
        output_folder = 'database'+ glob_slash + 'static'+ glob_slash + 'Helmet'
        os.makedirs(output_folder, exist_ok=True)

        # Jika ada objek yang terdeteksi, lanjutkan dengan cropping
        if len(results[0].boxes) > 0:
            cropped_image_paths = []

            for i, result in enumerate(results[0].boxes):
                # Dapatkan koordinat bounding box
                x1, y1, x2, y2 = map(int, result.xyxy[0])

                # Crop gambar berdasarkan bounding box
                save_frame = frame
                cropped_image = frame[y1:y2, x1:x2]
                
                if model.model.names[int(class_ids[i])] == 'no-helm':
                    text = "no-helm"
                    output_queue.put((cropped_image, track_id, text))
                    return
            output_queue.put((None, track_id, ""))  # Indikasi bahwa tidak ada helm terdeteksi
        else:
            print(f"No objects detected on attempt {attempt + 1}. Retrying...")

    # Jika tidak ada objek yang terdeteksi setelah retries selesai
    print("No objects detected after maximum retries.")
    output_queue.put((None, track_id, ""))

def detect_plat_and_crop_with_retries(output_queue, string_dir, frame_, track_id, model_path="plat_license.pt", retries=4):
    # Inisialisasi model YOLOv8
    model_ = YOLO(model_path)
    print(model_.model.names)
    # Loop untuk mencoba deteksi dengan batasan retry
    for attempt in range(retries):
        # Melakukan deteksi menggunakan YOLOv8
        #frame_ = cv2.resize(frame_, (416, 620), interpolation=cv2.INTER_AREA)
        results = model_.predict(source=frame_)
        class_ids = results[0].boxes.cls.numpy().tolist()
        output_folder = 'database'+ glob_slash + 'static'+ glob_slash + "plat_number_" + str(string_dir)
        os.makedirs(output_folder, exist_ok=True)

        print(class_ids)
        # Jika ada objek yang terdeteksi, lanjutkan dengan cropping
        if len(results[0].boxes) > 0:
            cropped_image_paths = []

            for i, result in enumerate(results[0].boxes):
                # Dapatkan koordinat bounding box
                class_ids = results[0].boxes.cls.numpy().tolist()

                # Crop gambar berdasarkan bounding box
                save_frame = results[0].plot()
                #text_result = process_image(save_frame)

                if model_.model.names[int(class_ids[i])] == '.':
                    print("detected")
                    initial_time_final_string = get_current_time()
                    final_string = recursive_output(initial_time_final_string, 0)  # contoh rekursi 0 kali
                    name_file = final_string + "_" + str(track_id) + ".jpg"
                    output_path = os.path.join(output_folder, name_file)
                    x1, y1, x2, y2 = map(int, result.xyxy[0])
                    cropped_image = frame_[y1:y2, x1:x2]
                    cv2.imwrite(output_path, cropped_image) 
                    #cv2.imwrite("test"+output_path, cropped_image)
                    output_queue.put((final_string, track_id))
                    return   
                # Simpan gambar yang sudah di-crop
               
                #print(model.model.names)
            output_queue.put(("", track_id))
        else:
            print(f"No objects detected on attempt {attempt + 1}. Retrying...")

    # Jika tidak ada objek yang terdeteksi setelah retries selesai
    print("No objects detected after maximum retries.")
    return "", track_id

class VideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive AI YOLO Dashboard")
        self.cropped_images = []
        self.ip_input = StringVar()
        self.status = StringVar()
        self.location = ""
        self.model = ""
        self.use_camera = False
        self.use_yolo = False
        self.use_distance_detector = False
        self.speed_obj = None
        self.detected_values = {1, 2, 3, 5, 7}  # 1: 'bicycle', 2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'
        self.detected_values_non_motorcycle = {2, 5, 7}  # 1: 'bicycle', 2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'
        self.max_speed = 80  # Initialize max_speed variable default
        self.width_in_pixel = 900
        self.width_in_meter = 7 #meter
        self.actual_time = 5.00
        self.yolo_time = 15.00
        self.constant = 0.0
        self.max_track_id = 0
        self.save_left_specific_val_id = []
        self.save_right_specific_val_id = []
        self.last_track_id = []
        self.save_id = []
        self.array_time = []
        self.get_point_A_B = []
        self.point_get_category = []
        self.moving_right_dir_id = []
        self.moving_left_dir_id = []
        self.get_violence_helm_id = []
        self.get_violence_seatbelt_id = []
        self.get_first_point_for_speed = []
        self.get_violence_overspeed_id = []
        self.get_violence_overtaking_id = []
        self.get_violence_wrong_dir_id = []
        self.get_violence_helm_date = []
        self.get_violence_seatbelt_date = []
        self.get_violence_overtaking_date = []        
        self.get_violence_wrong_dir_date = []
        self.get_violence_helm_flag = []
        self.get_violence_seatbelt_flag = []
        
        # Array untuk menyimpan track_id, direct_x, direct_y, dan speeds
        self.track_id_array = []
        self.class_ids = []
        self.direct_array = []
        self.sum_array = []
        self.last_speed = []
        Label(root, textvariable=self.status).pack(side="top", fill="x", pady=5)
        self.canvas = tk.Canvas(root, width=1600, height=900)
        self.canvas.pack()
        
        self.coordinates_label = tk.Label(root, text="Mouse Coordinates:")
        self.coordinates_label.pack()
        self.areas = []
        self.lines = []
        self.current_line = None
        self.ip_path = ""

        #config init
        self.conn = sqlite3.connect('database'+ glob_slash + 'configuration.db')
        self.conn_data = sqlite3.connect('database'+ glob_slash + 'datalog.db')
        self.save_ip = sqlite3.connect('save_ip.db')
        self.create_table()
        self.init_config()
        self.load_data() #load data
        self.ip_path = str(self.load_ip_from_db())
        #print("self.ip_path", self.ip_path)


        # Frame for input and buttons
        control_frame = tk.Frame(root)
        control_frame.pack(side="top", fill="x", pady=5)
        # Status Label
        
        
        # Input IP and video path
        Label(control_frame, text="Enter IP :").grid(row=0, column=0, padx=5)
        self.ip_input.set(str(self.ip_path))
        Entry(control_frame, textvariable=self.ip_input, width=40).grid(row=0, column=1, padx=5)
        
        # Connect Button
        Button(control_frame, text="Connect to Camera", command=self.connect_camera, width=15).grid(row=0, column=2, padx=5)
        
        # Toggle YOLO Button
        Button(control_frame, text="Toggle AI (YOLO)", command=self.toggle_yolo, width=15).grid(row=0, column=3, pady=5)
        
        # Save Distance Detector
        Button(control_frame, text="Distance Detector", command=self.toggle_detect_distance, width=15).grid(row=0, column=4, pady=5)
        #Button(control_frame, text="Save Photo", command=self.capture_photo, width=15).grid(row=0, column=4, pady=5)

        Button(control_frame, text="Add Area", command=self.add_area, width=15).grid(row=0, column=5, padx=5)
        Button(control_frame, text="Draw Line", command=self.draw_line, width=15).grid(row=0, column=6, padx=5)
        Button(control_frame, text="Undo Last Area", command=self.undo_last_area, width=15).grid(row=0, column=7, padx=5)
        Button(control_frame, text="Undo Last Line", command=self.undo_last_line, width=15).grid(row=0, column=8, padx=5)

        #configuration button
        Button(control_frame, text="Configuration", command=self.open_config, width=15).grid(row=0, column=9, pady=5)

        # Exit Button
        Button(control_frame, text="Exit", command=root.quit, width=15).grid(row=0, column=10, pady=5)

        # Bind event klik mouse ke fungsi mark_coordinate
        self.canvas.bind("<Button-1>", self.mark_coordinate)

        # Bind event gerakan mouse untuk melacak koordinat
        self.canvas.bind("<Motion>", self.track_mouse)

 
        # Video Stream Label
        self.video_label = Label(root)
        self.video_label.pack(expand=True)
        self.reference_image = None
        self.reference_imgtk = None
        
        # Other variables and objects
        self.camera = None
        self.model_yolo = YOLO(str(self.model))
        self.frame_buffer = deque(maxlen=100)  # Main buffer
        self.alt_buffer = deque(maxlen=100)  # Alternative buffer
        self.last_frame = None
        self.track_points = {}  # Dictionary to store points based on track_id
        self.track_history = defaultdict(lambda: [])
        
    def create_table(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS areas (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT NOT NULL,
                                    coordinates TEXT NOT NULL
                                )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS lines (
                                    id INTEGER PRIMARY KEY ,
                                    name TEXT NOT NULL,
                                    x1 INTEGER,
                                    y1 INTEGER,
                                    x2 INTEGER,
                                    y2 INTEGER
                                )''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS config (
                                    id INTEGER PRIMARY KEY,
                                    calibration_factor REAL,
                                    max_speed REAL,
                                    width_in_pixel REAL,
                                    width_in_meter REAL,
                                    actual_time REAL,
                                    yolo_time REAL,
                                    location type TEXT NOT NULL,
                                    Model type TEXT NOT NULL
                                )''')

        with self.conn_data:
            self.conn_data.execute('''CREATE TABLE IF NOT EXISTS datalog (
                                    id INTEGER PRIMARY KEY,
                                    track_id TEXT NOT NULL,
                                    date TEXT NOT NULL,
                                    plat_license TEXT NOT NULL,
                                    speed TEXT NOT NULL,
                                    max_speed TEXT NOT NULL,
                                    violence_category TEXT NOT NULL,
                                    vehicle TEXT NOT NULL,
                                    location TEXT NOT NULL,
                                    open_photo TEXT NOT NULL
                                )''')
        with self.save_ip:
            self.save_ip.execute('''CREATE TABLE IF NOT EXISTS save_ip (
                                    IP TEXT NOT NULL
                                )''')

    def mark_coordinate(self, event):
        # Dapatkan koordinat klik
        x, y = event.x, event.y
        # Tandai titik pada kanvas
        self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="blue")
        # Tambahkan teks koordinat di titik tersebut
        self.canvas.create_text(x + 10, y, text=f"({x}, {y})", anchor=tk.W, fill="blue")
        # Tampilkan koordinat di label
        self.coordinates_label.config(text=f"Mouse Clicked at: ({x}, {y})")


    def add_area(self):
        coords_str = simpledialog.askstring("Input", "Enter coordinates (x1,y1,x2,y2,x3,y3,...):")
        area_name = simpledialog.askstring("Input", "Enter area name:")
        coords_list = list(map(int, coords_str.split(',')))
        #print(len(coords_list))
        if int(len(coords_list)) % 2 == 0 and int(len(coords_list)) > 2:
            if coords_str and area_name:
                coords = list(map(int, coords_str.split(',')))
                area = self.canvas.create_polygon(coords, outline="red", fill="")
                self.areas.append((area, area_name, coords_str))
                self.save_area_to_db(area_name, coords_str)

    def save_area_to_db(self, name, coordinates):
        with self.conn:
            self.conn.execute("INSERT INTO areas (name, coordinates) VALUES (?, ?)", (name, coordinates))

    def calculate_distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def draw_line(self):
        self.start_x = None
        self.start_y = None
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_mouse_drag(self, event):
        if self.start_x and self.start_y:
            self.canvas.delete("current_line")
            self.current_line = self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, fill="green", width=2, tags="current_line")

    def on_button_release(self, event):
        if self.start_x and self.start_y:
            line_name = simpledialog.askstring("Input", "Enter line name:")
            if line_name:
                line_id = self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, fill="green", width=2)
                distance = round(self.calculate_distance(self.start_x, self.start_y, event.x, event.y), 1)
                line_draw = str(distance)
                self.canvas.create_text((self.start_x + event.x) / 2, (self.start_y + event.y) / 2, text=line_draw, anchor=tk.CENTER, fill="black")
                self.lines.append((line_id, line_name, self.start_x, self.start_y, event.x, event.y))
                self.save_line_to_db(line_name, self.start_x, self.start_y, event.x, event.y)

                # Check for collisions with other lines
                for line in self.lines:
                    if line[0] != line_id:  # Pastikan kita tidak mengecek garis yang sama
                        f_collision_x, f_collision_y = self.check_line_collision((self.start_x, self.start_y, event.x, event.y), (line[2], line[3], line[4], line[5]))
                        if f_collision_x is not None and f_collision_y is not None:
                            collision_x = round(f_collision_x, 1)
                            collision_y = round(f_collision_y, 1)
                            self.canvas.create_text(collision_x, collision_y, text=f"x={collision_x}, y={collision_y}", fill="black")

            self.canvas.delete("current_line")
            self.start_x = None
            self.start_y = None

    def check_line_collision(self, line1, line2):
        x1, y1, x2, y2 = line1
        x3, y3, x4, y4 = line2

        def det(a, b, c, d):
            return a * d - b * c

        denominator = det(x1 - x2, y1 - y2, x3 - x4, y3 - y4)
        if denominator == 0:
            return None, None

        t = det(x1 - x3, y1 - y3, x3 - x4, y3 - y4) / denominator
        u = det(x1 - x3, y1 - y3, x1 - x2, y1 - y2) / denominator

        if 0 <= t <= 1 and 0 <= u <= 1:
            intersection_x = x1 + t * (x2 - x1)
            intersection_y = y1 + t * (y2 - y1)
            return intersection_x, intersection_y
        return None, None

    def save_line_to_db(self, name, x1, y1, x2, y2):
        with self.conn:
            self.conn.execute("INSERT INTO lines (name, x1, y1, x2, y2) VALUES (?, ?, ?, ?, ?)", (name, x1, y1, x2, y2))
    
    def save_datalog(self, track_id, date, plat_license, speed, max_speed, violence_category, vehicle, location, open_photo):
        with self.conn_data:
            self.conn_data.execute("INSERT INTO datalog (track_id, date, plat_license, speed, max_speed, violence_category, vehicle, location, open_photo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (track_id, date, plat_license, speed, max_speed, violence_category, vehicle, location, open_photo))

    def save_string_ip(self, str_in):
        with self.save_ip:
            cursor = self.save_ip.cursor()
        
            # Cek apakah tabel sudah memiliki data
            cursor.execute("SELECT COUNT(*) FROM save_ip")
            row_count = cursor.fetchone()[0]
        
            if row_count == 0:
                # Jika tabel kosong, lakukan INSERT
                cursor.execute("INSERT INTO save_ip (IP) VALUES (?)", (str(str_in),))
            else:
                # Jika tabel sudah ada data, lakukan UPDATE di baris pertama
                cursor.execute("UPDATE save_ip SET IP = ? WHERE ROWID = (SELECT ROWID FROM save_ip LIMIT 1)", (str(str_in),))
        
            self.save_ip.commit()  # Commit perubahan
    
    def load_ip_from_db(self):
        # Menggunakan with untuk memastikan cursor ditutup dengan benar
        with self.save_ip:  # 'self.save_ip' adalah koneksi yang sudah ada
            cursor = self.save_ip.cursor()
            cursor.execute("SELECT IP FROM save_ip")
            ip_addresses = cursor.fetchall()  # Mengambil semua hasil
            for row in ip_addresses:
                if row[0] is not None:
                    #print("test", row[0])  # Mengakses elemen pertama dari setiap tuple (yaitu string '5.mp4')
                    return row[0]

    
    def delete_datalog_from_db(self, track_id):
        with self.conn:
            self.conn.execute("DELETE FROM areas WHERE track_id = ?", (track_id,))

    def undo_last_area(self):
        if self.areas:
            last_area, last_name, last_coords_str = self.areas.pop()
            self.canvas.delete(last_area)
            self.delete_area_from_db(last_name)
        if not self.lines and not self.areas:  # Jika tidak ada garis tersisa, hapus semua
            self.canvas.delete("all")

    def undo_last_line(self):
        if self.lines:
            last_line = self.lines.pop()
            self.canvas.delete(last_line[0])
            self.delete_line_from_db(last_line[1])
        if not self.lines and not self.areas:  # Jika tidak ada garis tersisa, hapus semua
            self.canvas.delete("all")
            
    def delete_area_from_db(self, name):
        with self.conn:
            self.conn.execute("DELETE FROM areas WHERE name = ?", (name,))

    def delete_line_from_db(self, name):
        with self.conn:
            self.conn.execute("DELETE FROM lines WHERE name = ?", (name,))
    
    def check_value_in_column(self, column_name, value_to_check):
        with self.conn_data:    
            # Membuat cursor untuk mengeksekusi query SQL
            cursor = self.conn_data.cursor()

            # Query untuk mengecek nilai berdasarkan nama kolom yang diberikan
            query = f"SELECT * FROM datalog WHERE {column_name} = ?"
        
            # Mengeksekusi query dengan nilai yang ingin dicari
            cursor.execute(query, (value_to_check,))
        
            # Mengambil semua hasil query
            result = cursor.fetchall()

            # Mengecek apakah hasil ditemukan
            if result:
                print(f"Data dengan {column_name} = '{value_to_check}' ditemukan:")
                return True
            else:
                print(f"Data dengan {column_name} = '{value_to_check}' tidak ditemukan")
                return False

    def find_max_track_id(self):
        # Cek apakah koneksi sudah ditutup, jika iya, buka kembali
    
        with self.conn_data:    
            # Membuat cursor untuk mengeksekusi query SQL
            cursor = self.conn_data.cursor()
        
            # Query untuk mencari nilai maksimal di kolom track_id
            # CAST digunakan untuk mengonversi string menjadi FLOAT agar bisa dibandingkan
            query = "SELECT MAX(CAST(track_id AS FLOAT)) FROM datalog"
        
            # Mengeksekusi query
            cursor.execute(query)
        
            # Mengambil hasil query (nilai maksimal)
            max_value = cursor.fetchone()[0]

            if max_value is not None:
                print(f"Nilai maksimal dalam track_id: {max_value}")
                return max_value
            else:
                print("Tidak ada data dalam track_id")
                return 0

    def get_row_by_column_value(self, column_name, value_to_check):
        with self.conn_data:    
            # Membuat cursor untuk mengeksekusi query SQL
            cursor = self.conn_data.cursor()

            # Query untuk mendapatkan baris berdasarkan nama kolom dan nilai
            query = f"SELECT * FROM datalog WHERE {column_name} = ?"
        
            # Mengeksekusi query dengan nilai yang ingin dicari
            cursor.execute(query, (value_to_check,))
        
            # Mengambil semua baris yang cocok dengan kondisi
            rows = cursor.fetchall()

            if rows:
                print(f"Data ditemukan berdasarkan {column_name} = '{value_to_check}':")
                return rows
            else:
                print(f"Tidak ada data yang cocok dengan {column_name} = '{value_to_check}'")
                return []

    def set_value_once(self, array, new_item): #self.array_time
        id_found = False
        # Loop through the array to check if the id already exists
        for i, item in enumerate(array):
            if item[0] == new_item[0]:
                id_found = True
                break
    
        # If the id was not found, append the new item to the array
        if not id_found:
            array.append(new_item)

    def get_single_value_by_id(self, array, search_id):
        for item in array:
            if isinstance(item, (tuple, list)) and len(item) >= 2:  # Cek apakah item adalah tuple/list
                if int(item[0]) == int(search_id):
                    return item[1]
        return 0.0  # Jika id t

    def get_single_string_value_by_id(self, array, search_id):
        for item in array:
            if isinstance(item, (tuple, list)) and len(item) >= 2:  # Cek apakah item adalah tuple/list
                if int(item[0]) == int(search_id):
                    return item[1]
        return ""  # Jika id t

    def get_multi_value_by_id(self, array, search_id):
        for item in array:
            if isinstance(item, (tuple, list)) and len(item) >= 2:  # Cek apakah item adalah tuple/list
                if int(item[0]) == int(search_id):
                    return item[1]
        return []  # Jika id t

    def check_values_by_track_id(self, track_id, data_array):
        results = []
        for track_id in track_id:
            found = False
            for item in data_array:
                if track_id in item:
                    results.append(item)
                    found = True
                    break
            if not found:
                results.append(f"ID {track_id} not found")
        return results    

    def update_or_append_tuples(self, array, new_item): #self.array_time
        id_found = False
        # Loop through the array to check if the id already exists
        for i, item in enumerate(array):
            if item[0] == new_item[0]:
                # If id found, update the value
                array[i] = new_item
                id_found = True
                break
    
        # If the id was not found, append the new item to the array
        if not id_found:
            array.append(new_item)

    def update_or_append_tuples_and_sum(self, array, new_item): #self.array_time
        id_found = False
        # Loop through the array to check if the id already exists
        for i, item in enumerate(array):
            if item[0] == new_item[0]:
                # If id found, update the value
                array[i] = new_item[0], (new_item[1] + 1.0)
                id_found = True
                break
    
        # If the id was not found, append the new item to the array
        if not id_found:
            array.append(new_item)    

    def update_or_append_single_var(self, array, new_item): #self.array_time
        id_found = False
        # Loop through the array to check if the id already exists
        for i, item in enumerate(array):
            if item == new_item:
                # If id found, update the value
                array[i] = new_item
                id_found = True
                break
    
        # If the id was not found, append the new item to the array
        if not id_found:
            array.append(new_item)

    def load_data(self):
        with self.conn:
            # Load areas
            cursor = self.conn.execute("SELECT name, coordinates FROM areas")
            for row in cursor:
                name, coords_str = row
                coords = list(map(int, coords_str.split(',')))
                area = self.canvas.create_polygon(coords, outline="red", fill="")
                self.areas.append((area, name, coords_str))

            # Load lines
            cursor = self.conn.execute("SELECT name, x1, y1, x2, y2 FROM lines")
            for row in cursor:
                name, x1, y1, x2, y2 = row
                line_id = self.canvas.create_line(x1, y1, x2, y2, fill="green", width=2)
                self.lines.append((line_id, name, x1, y1, x2, y2))
                distance = round(self.calculate_distance(x1, y1, x2, y2), 1)
                line_draw = str(distance)
                self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=line_draw, anchor=tk.CENTER, fill="black")
            
                # Setelah menambahkan garis, lakukan pengecekan collision dengan garis lain
                for line in self.lines:
                    if line[0] != line_id:  # Pastikan tidak mengecek garis yang sama
                        f_collision_x, f_collision_y = self.check_line_collision(
                            (x1, y1, x2, y2), 
                            (line[2], line[3], line[4], line[5]))

                        if f_collision_x is not None and f_collision_y is not None:
                            collision_x = round(f_collision_x, 1)
                            collision_y = round(f_collision_y, 1)
                            self.canvas.create_text(collision_x, collision_y, text=f"x={collision_x}, y={collision_y}", fill="black")
                        
    def track_mouse(self, event):
        x, y = event.x, event.y
        self.coordinates_label.config(text=f"Mouse Coordinates: ({x}, {y})")

        mouse_in_any_area = False
        for area, name, coords_str in self.areas:
            if self.is_in_area(x, y, area):
                #print(x,y, area)
                self.coordinates_label.config(text=f"Mouse in '{name}' Area at: ({x}, {y})")
                mouse_in_any_area = True
                break

        if not mouse_in_any_area:
            for line in self.lines:
                if self.is_near_line(line, x, y):
                    self.coordinates_label.config(text=f"Mouse near line '{line[1]}' at: ({x}, {y})")
                    mouse_in_any_area = True
                    break

        if not mouse_in_any_area:
            self.coordinates_label.config(text=f"Mouse is not in any Area: ({x}, {y})")

    def is_in_area(self, x, y, area):
        coords = self.canvas.coords(area)
        return self.is_point_in_polygon(x, y, coords)

    def is_point_in_polygon(self, x, y, coords):
        n = len(coords) // 2
        inside = False
        p1x, p1y = coords[0], coords[1]
        for i in range(n + 1):
            p2x, p2y = coords[2 * (i % n)], coords[2 * (i % n) + 1]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def is_near_line(self, line, x, y):
        x1, y1, x2, y2 = line[2:6]
        devider = (((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5)
        
        if devider == 0:
            devider = 1

        distance = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / devider
        return distance < 5  # Adjust tolerance as needed

    def on_closing(self):
        self.conn.close()
        self.root.destroy()

    def init_config(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM config WHERE id=1")
        config = c.fetchone()
        #self.max_track_id = self.find_max_track_id()
        global glob_calibration_factor, glob_width_in_meter, glob_width_in_pixel, glob_actual_time, glob_yolo_time, glob_model
        if config is None:
            # Default config
            self.calibration_factor = 2.0
            self.max_speed = 80  # Initialize max_speed variable default
            self.width_in_pixel = 900
            self.width_in_meter = 7 #meter
            self.actual_time = 5.00
            self.yolo_time = 15.00
            self.location = "Indonesia"
            self.model = "yolov8x.pt"
            glob_calibration_factor = self.calibration_factor
            glob_width_in_meter = self.width_in_meter
            glob_width_in_pixel = self.width_in_pixel
            glob_actual_time = self.actual_time
            glob_yolo_time = self.yolo_time
            glob_model = self.model
            c.execute("INSERT INTO config (id, calibration_factor, max_speed, width_in_pixel, width_in_meter, actual_time, yolo_time, location, Model) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (self.calibration_factor, self.max_speed, self.width_in_pixel, self.width_in_meter, self.actual_time, self.yolo_time, self.location, self.model))
            self.conn.commit()
        else:
            self.calibration_factor, self.max_speed, self.width_in_pixel, self.width_in_meter, self.actual_time, self.yolo_time, self.location, self.model = config[1:]
            glob_calibration_factor = self.calibration_factor
            glob_width_in_meter = self.width_in_meter
            glob_width_in_pixel = self.width_in_pixel
            glob_actual_time = self.actual_time
            glob_yolo_time = self.yolo_time
            glob_model = self.model

    def select_row_model(self, input):
        if input == "yolov8x.pt":
            output = 0
        elif input == "yolov8l.pt":
            output = 1
        elif input == "yolov8m.pt":
            output = 2
        elif input == "yolov8s.pt":
            output = 3
        elif input == "yolov8n.pt":
            output = 4
        else:
            output = 0
        return output
    def select_model(self, input):
        if input == "super":
            output = "yolov8x.pt"
        elif input == "large":
            output = "yolov8l.pt"
        elif input == "medium":
            output = "yolov8m.pt"
        elif input == "small":
            output = "yolov8s.pt"
        elif input == "nano":
            output = "yolov8n.pt"
        else:
            output = "yolov8x.pt"
        return output
    
    def open_config(self):
        config_window = tk.Toplevel(self.root)
        config_window.title("Configuration")
        
        tk.Label(config_window, text="Calibration Factor (e.g., 2.0):").grid(row=0, column=0)
        calibration_factor_entry = tk.Entry(config_window)
        calibration_factor_entry.grid(row=0, column=1)
        calibration_factor_entry.insert(0, str(self.calibration_factor))

        tk.Label(config_window, text="Maximum Speed (e.g., 80.0):").grid(row=1, column=0)
        max_speed_entry = tk.Entry(config_window)
        max_speed_entry.grid(row=1, column=1)
        max_speed_entry.insert(0, str(self.max_speed))
        
        tk.Label(config_window, text="Width in Pixel:").grid(row=2, column=0)
        width_in_pixel_entry = tk.Entry(config_window)
        width_in_pixel_entry.grid(row=2, column=1)
        width_in_pixel_entry.insert(0, str(self.width_in_pixel))
        
        tk.Label(config_window, text="Width in Meter:").grid(row=3, column=0)
        width_in_meter_entry = tk.Entry(config_window)
        width_in_meter_entry.grid(row=3, column=1)
        width_in_meter_entry.insert(0, str(self.width_in_meter))

        tk.Label(config_window, text="Actual Time:").grid(row=4, column=0)
        actual_time_entry = tk.Entry(config_window)
        actual_time_entry.grid(row=4, column=1)
        actual_time_entry.insert(0, str(self.actual_time))

        tk.Label(config_window, text="Yolo Time:").grid(row=5, column=0)
        yolo_time_entry = tk.Entry(config_window)
        yolo_time_entry.grid(row=5, column=1)
        yolo_time_entry.insert(0, str(self.yolo_time))  

        tk.Label(config_window, text="Location:").grid(row=6, column=0)
        location_entry = tk.Entry(config_window)
        location_entry.grid(row=6, column=1)
        location_entry.insert(0, self.location) 
        
        tk.Label(config_window, text="Model AI:").grid(row=7, column=0)
        # Define the available options
        options = ["super", "large", "medium", "small", "nano"]
        # Create a StringVar to hold the selected option
        selected_option = tk.StringVar(config_window)
        print(self.model)
        get_row = int(self.select_row_model(str(self.model)))
        print(get_row)
        selected_option.set(options[get_row])  # Set default value
        # Create OptionMenu and place it in the grid
        model_option = tk.OptionMenu(config_window, selected_option, *options)
        model_option.grid(row=7, column=1)
        model_option.config(width=15)   
        self.model = self.select_model(str(selected_option.get()))
        print(self.model)
     
        
        #save ke database config
        def save_config():
            global glob_calibration_factor, glob_width_in_meter, glob_width_in_pixel, glob_actual_time, glob_yolo_time, glob_model
            self.calibration_factor = float(calibration_factor_entry.get())
            self.max_speed = float(max_speed_entry.get())
            self.width_in_pixel = float(width_in_pixel_entry.get())
            self.width_in_meter = float(width_in_meter_entry.get())
            self.actual_time = float(actual_time_entry.get())
            self.yolo_time = float(yolo_time_entry.get())
            self.location = str(location_entry.get())
            self.model = str(self.select_model(str(selected_option.get())))
            print(selected_option.get())
            print(self.model)
            glob_calibration_factor = self.calibration_factor
            glob_width_in_meter = self.width_in_meter
            glob_width_in_pixel = self.width_in_pixel
            glob_actual_time = self.actual_time
            glob_yolo_time = self.yolo_time
            glob_model = self.model
            
            c = self.conn.cursor()
            c.execute("UPDATE config SET calibration_factor=?, max_speed=?, width_in_pixel=?, width_in_meter=?, actual_time=?, yolo_time=?, location=?, Model=? WHERE id=1",
                      (self.calibration_factor, self.max_speed, self.width_in_pixel, self.width_in_meter, self.actual_time, self.yolo_time, self.location, self.model))
            self.conn.commit()
            
            self.model_yolo = YOLO(str(self.model)) #update model yolo
            config_window.destroy()
            
        
        save_button = tk.Button(config_window, text="Save", command=save_config)
        save_button.grid(row=8, column=0, columnspan=2)
        

    def dir_checker(self, file_path, dir_plat_image_html):
        file_path_read ='database' + glob_slash + 'static' + glob_slash + file_path
        if os.path.isfile(file_path_read):
            return dir_plat_image_html
        else:
            return "Not Detected"

    #connect ke kamera
    def connect_camera(self):
        self.use_camera = not self.use_camera
        #print(self.use_camera)
        if self.use_camera == True:
            self.camera = cv2.VideoCapture(str(self.ip_input.get()))
            self.save_string_ip(str(self.ip_input.get()))
            #print(self.ip_input.get())
        
            if not self.camera.isOpened():
                self.status.set(f"Failed to connect to camera at {self.ip_input.get() }")
            else:
                self.status.set("Connected to camera")
                self.capture_and_process_frames()
        else:
            self.camera.release()
     
    #itung jarak antar titik
    def uclidean_vector(self, x, y, x0, y0):
        dx = x - x0
        dy = y - y0
        distance = math.sqrt(dx ** 2 + dy ** 2)
        return distance

    def draw_line_with_text(self, image, start_point, end_point, color, thickness, text):
        # Menggambar garis
        cv2.line(image, start_point, end_point, color, thickness)
    
        # Menghitung posisi tengah garis
        mid_point = ((start_point[0] + end_point[0]) // 2, (start_point[1] + end_point[1]) // 2)
    
        # Menambahkan teks di tengah garis
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_thickness = 2
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
    
        # Menghitung posisi kiri bawah teks agar teks berada di tengah
        text_position = (mid_point[0] - text_size[0] // 2, mid_point[1] + text_size[1] // 2)
        cv2.putText(image, text, text_position, font, font_scale, color, font_thickness)


    def toggle_yolo(self):
        self.use_yolo = not self.use_yolo
        self.status.set(f"YOLO Enabled: {self.use_yolo}" + f", Distance Detector Enabled: {self.use_distance_detector}")
    
    def toggle_detect_distance(self):
        self.use_distance_detector = not self.use_distance_detector
        self.status.set(f"YOLO Enabled: {self.use_yolo}" + f", Distance Detector Enabled: {self.use_distance_detector}")

    def capture_and_process_frames(self):
        global glob_integral, glob_span_time, glob_width_in_meter, glob_width_in_pixel, glob_actual_time, glob_yolo_time
        success, frame_get = self.camera.read()

        detect_once = False
        # Inisialisasi list untuk menyimpan gambar yang di-crop
        cropped_images_seatbelt = []
        cropped_images_overspeed = []
        cropped_images_wrong_dir = []
        cropped_motor_cycle = []

        if success:
            # Store the frame in both buffers
            frame_get = cv2.resize(frame_get, (1600, 900), interpolation=cv2.INTER_AREA)
            frame = frame_get
            self.frame_buffer.append(frame_get)
            self.alt_buffer.append(frame_get)

            # Process frame
            if self.frame_buffer:
                frame = self.frame_buffer.popleft()
                fps = self.camera.get(cv2.CAP_PROP_FPS)
                #print(self.max_speed)
                #print("test_id", self.use_yolo)

                if self.use_yolo:
                    #print("cek id1")
                    #print(self.model_yolo.model.names)
                    #print(self.speed_cor)     
                    speed_show = 0
                    last_x, last_y = 0, 0                   
                    present_track_id = []
                    #print("cek id2")
                    results = self.model_yolo.track(frame, persist=True,  verbose=False)
                    #print("cek id3")
                    boxes = results[0].boxes.xyxy.cpu()
                    #print("cek id4")
                    # Track objects in the frame
                    #frame = results[0].plot()

                    if results[0].boxes.is_track == True: 
                        for box, track_id in zip(boxes, self.track_id_array):
                            x, y, w, h = box
                            x1, y1, x2, y2 = map(int, box)
                            x_point = int(abs(x2-x1)/2) + x1
                            y_point = int(abs(y2-y1)/2) + y1

                            #counting time sejak
                            get_point_A_B = self.get_single_string_value_by_id(self.get_point_A_B, track_id)
                            #print("track_id", track_id, "get_point_A_B", get_point_A_B)
                            if get_point_A_B == "POINT_A" or get_point_A_B == "POINT_B":
                                counter = self.get_single_value_by_id(self.array_time, track_id)
                                self.update_or_append_tuples_and_sum(self.array_time, (track_id, counter))
                            
                            #counter_ = self.get_single_value_by_id(self.array_time, track_id)
                            #print("track_id", track_id, "counter", counter_)
                                        
                            if self.class_ids[int(self.track_id_array.index(track_id))] in self.detected_values:
                                self.update_or_append_single_var(self.save_id, track_id)

                            #program untuk menggambar jarak aman
                            safe_distance_condition = self.class_ids[int(self.track_id_array.index(track_id))] in self.detected_values and len(self.last_track_id) != 0
                            if self.use_distance_detector == True and safe_distance_condition == True:                                            
                                for id, value_id in enumerate(self.track_id_array):
                                    get_array = []
                                    condition_draw = True
                                    get_array = self.get_multi_value_by_id(self.last_track_id, value_id) 

                                    limit = 50
                                    last_x, last_y = 0, 0
                                    if len(get_array) != 0:
                                        last_x, last_y  = get_array[0], get_array[1]
                                    else:
                                        last_x, last_y = x_point, y_point

                                    if abs(x_point - last_x) <= limit and abs(y_point - last_y) <= limit:
                                        last_x = x_point
                                        last_y = y_point

                                    if track_id == id:
                                        condition_draw = False

                                    distance = self.uclidean_vector(x_point, y_point, last_x, last_y)
                                    #print(track_id, distance)
                                    if condition_draw == True and distance >= ((abs(x2-x1)) * 2) and distance < ((abs(x2-x1)) * 5):
                                        #print("jarak cukup aman", distance)
                                        #cv2.line(frame, (x_point, y_point), (last_x, last_y), (0, 255, 0), 1)  #garis hijau
                                        self.draw_line_with_text(frame, (x_point, y_point), (last_x, last_y), (0, 255, 0), 1, "Safe")  #garis biru (sangat aman)
                                    elif condition_draw == True and distance >= ((abs(x2-x1)) * 1) and distance < ((abs(x2-x1)) * 2):
                                        #print("jarak kurang aman", distance)
                                        #self.draw_line_with_text(frame, (x_point, y_point), (last_x, last_y), (0, 165, 255), 1, "Somewhat Unsafe")  #garis biru (sangat aman)
                                        self.draw_line_with_text(frame, (x_point, y_point), (last_x, last_y), (0, 165, 255), 1, "Enough safe")  #garis biru (sangat aman)
                                    elif condition_draw == True and distance < ((abs(x2-x1))/2) and distance >= limit:
                                         #print("jarak tidak aman", distance)
                                        self.draw_line_with_text(frame, (x_point, y_point), (last_x, last_y), (0, 0, 255), 1, "Not safe !!")  #garis biru (sangat aman)

                            #program untuk support deteksi lawan arah
                            index_direct_array = next((i for i, row in enumerate(self.direct_array) if row[0] == track_id), None)
                            if len(self.direct_array) == 0:
                                # Jika self.direct_array kosong, tambahkan track_id dengan nilai baru
                                self.direct_array.append((track_id, x_point, y_point, x_point, y_point, 0, 0, "NONE"))
                            else:

                                if index_direct_array is None:
                                    self.direct_array.append((track_id, x_point, y_point, x_point, y_point, 0, 0, "NONE"))
                                else:
                                    # Jika track_id sudah ada, perbarui koordinat
                                    x_point_1, y_point_1 = self.direct_array[index_direct_array][1], self.direct_array[index_direct_array][2]
                                    last_dir = self.direct_array[index_direct_array][5]
                                    last_count = self.direct_array[index_direct_array][6]
                                    last_string = self.direct_array[index_direct_array][7]
                                    cek_dir = (y_point-y_point_1) + last_dir
                                    counter = last_count + 1
                                    self.direct_array[index_direct_array] = (track_id, x_point, y_point, x_point_1, y_point_1, cek_dir, counter, last_string)        
                            
                            #program untuk deteksi area
                            for area in self.areas:
                                coords = self.canvas.coords(area[0])
                                condition_1 = len(self.track_id_array) >= 1 and (len(self.class_ids) == len(self.track_id_array))
                                condition_2 = self.is_point_in_polygon(x_point, y_point, coords) and track_id in self.track_id_array
                                class_ids_allows = self.class_ids[int(self.track_id_array.index(track_id))] in self.detected_values

                                if condition_1 == True and condition_2 == True and class_ids_allows == True:
                                    vehicle_name = self.model_yolo.names[self.class_ids[int(self.track_id_array.index(track_id))]]
                                    
                                    #program untuk deteksi seatbelt
                                    if self.class_ids[int(self.track_id_array.index(track_id))] in self.detected_values_non_motorcycle:
                                        y1_new = y1-100
                                        if y1-100 < 0.0:
                                            y1_new = 0

                                        y2_new = y2+50
                                        if (y2+50) > 900:
                                            y2_new = 900
                                        
                                        x1_new = x1-50
                                        if (x1-50) < 0.0:
                                            x1_new = 0

                                        x2_new = x2+50
                                        if (x2+50) > 1600:
                                            x2_new = 1600

                                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                                        #cv2.putText(frame, str(vehicle_name), (int(x1), int(y2+20)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
                                        cropped_images_seatbelt = frame_get[y1_new:y2_new, x1_new:x2_new]
                                        initial_time_final_string = get_current_time()
                                        get_point_A_B = self.get_single_string_value_by_id(self.get_point_A_B, track_id)
                                        validation_point = validation_area_point_A_B = get_point_A_B == "POINT_A" and area[1] == "POINT_B" or get_point_A_B == "POINT_B" and area[1] == "POINT_A"
                                        validation_detect = not track_id in self.get_violence_seatbelt_flag and len(self.get_violence_seatbelt_flag) != 0 and track_id != 0
                                        final_string = recursive_output(initial_time_final_string, 0)  # contoh rekursi 0 kali
                                        if validation_point == True and validation_detect == True:
                                            get_val = queue.Queue() 
                                            detection_thread_seatbelt = threading.Thread(target=lambda:detect_seatbelt(get_val, cropped_images_seatbelt, track_id))
                                            detection_thread_seatbelt.start()
                                            detection_thread_seatbelt.join()
                                            img_get, get_id, status = [], track_id, ""
                                            if not get_val.empty():
                                                img_get, get_id, status = get_val.get()
                                            if status == "no-seatbelt":
                                                text_ = "No Seatbelt !!"
                                                cv2.putText(frame, text_, (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                                save_dir = "Seatbelt" + glob_slash + "[" + str(track_id) + "]" + "-" + str(final_string) + "_no-seatbelt_" + ".jpg"
                                                cv2.imwrite(str('database'+ glob_slash + 'static'+ glob_slash + save_dir), frame)
                                                self.get_violence_seatbelt_id.append(get_id)
                                                self.get_violence_seatbelt_date.append(str(final_string))
                                            self.get_violence_seatbelt_flag.append(get_id)
                                        elif len(self.get_violence_seatbelt_id) == 0:
                                            self.get_violence_seatbelt_id.append(0)
                                            self.get_violence_seatbelt_date.append(0)
                                            self.get_violence_seatbelt_flag.append(0)                                  
                                    #program untuk deteksi helm
                                    if self.model_yolo.model.names[self.class_ids[int(self.track_id_array.index(track_id))]] == "motorcycle":
                                        y1_new = y1-100
                                        if y1-100 < 0.0:
                                            y1_new = 0

                                        y2_new = y2+50
                                        if (y2+50) > 900:
                                            y2_new = 900
                                        
                                        x1_new = x1-50
                                        if (x1-50) < 0.0:
                                            x1_new = 0

                                        x2_new = x2+50
                                        if (x2+50) > 1600:
                                            x2_new = 1600
                                    
                                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2) 
                                        cv2.putText(frame, str(vehicle_name), (int(x1), int(y2+20)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
                                        cropped_motor_cycle = frame_get[y1_new:y2_new, x1_new:x2_new]
                                        initial_time_final_string = get_current_time()
                                        get_point_A_B = self.get_single_string_value_by_id(self.get_point_A_B, track_id)
                                        validation_point = validation_area_point_A_B = get_point_A_B == "POINT_A" and area[1] == "POINT_B" or get_point_A_B == "POINT_B" and area[1] == "POINT_A"
                                        validation_detect = not track_id in self.get_violence_helm_flag and len(self.get_violence_helm_flag)!=0 and track_id != 0
                                        final_string = recursive_output(initial_time_final_string, 0)  # contoh rekursi 0 kali
                                        if validation_point == True and validation_detect == True:
                                            get_val = queue.Queue() 
                                            detection_thread_helmet = threading.Thread(target=lambda:detect_helmet(get_val, cropped_motor_cycle, track_id))
                                            detection_thread_helmet.start()
                                            detection_thread_helmet.join()
                                            img_get, get_id, status = [], track_id, ""
                                            if not get_val.empty():
                                                img_get, get_id, status = get_val.get()
                                            
                                            if status == "no-helm":
                                                text_ = "No Helm !!"                                                
                                                cv2.putText(frame, text_, (int(x1), int(y1_new+50)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                                                cv2.rectangle(frame, (x1, int(y1_new+50)), (x2, y2), (0, 0, 255), 2)
                                                save_dir =   "Helmet" + glob_slash + "[" + str(track_id) + "]" + "-" + str(final_string) + "_no-helmet_" + ".jpg"
                                                cv2.imwrite(str('database'+ glob_slash + 'static'+ glob_slash + save_dir), frame)
                                                self.get_violence_helm_id.append(get_id)
                                                self.get_violence_helm_date.append(str(final_string))
                                            self.get_violence_helm_flag.append(get_id)
                                        elif len(self.get_violence_helm_id) == 0:
                                            self.get_violence_helm_id.append(0)
                                            self.get_violence_helm_date.append(0)
                                            self.get_violence_helm_flag.append(0)
                                        
                                    #algoritma untuk deteksi arah
                                    validation_track_id = len(self.track_id_array) != 0
                                    if validation_track_id == True:

                                        if (any(row[0] == track_id for row in self.direct_array)) and len(self.direct_array) != 0:
                                            row = next((r for r in self.direct_array if r[0] == track_id), None)
                                            xp, yp, xp_1, yp_1, cek_dir, counter_dir, flag_string = row[1],row[2], row[3], row[4], row[5], row[6], row[7]
                                            
                                            #deteksi lawan arah (kanan)
                                            if area[1] == "RIGHT":
                                                if index_direct_array is not None and counter_dir >= 5 and flag_string == "NONE":
                                                    self.direct_array[index_direct_array] =  (track_id, xp, yp, xp_1, yp_1, counter_dir, counter, "RIGHT")

                                                if int(cek_dir) < 0 and counter_dir >= 20 and flag_string == "RIGHT":
                                                    print("pelanggaran RIGHT track_id: ", track_id)
                                                                                        
                                                    y1_new = y1-50
                                                    if y1-50 < 0.0:
                                                        y1_new = 0

                                                    y2_new = y2+50
                                                    if (y2+50) > 900:
                                                        y2_new = 900
                                        
                                                    x1_new = x1-50
                                                    if (x1-50) < 0.0:
                                                        x1_new = 0

                                                    x2_new = x2+50
                                                    if (x2+50) > 1600:
                                                        x2_new = 1600

                                                    #box.xyxy = [[x1_new, y1_new, x2_new, y2_new]]
                                                    cropped_images_wrong_dir = frame_get[y1_new:y2_new, x1_new:x2_new]
                                                    text_ = "Wrong Direction"
                                                    cv2.putText(frame, text_, (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                                    violence_category = "Wrong_direction"
                                                    if not track_id in self.get_violence_wrong_dir_id and len(cropped_images_wrong_dir)>0 and track_id != 0:
                                                        initial_time_final_string = get_current_time()
                                                        final_string = recursive_output(initial_time_final_string, 0)  # contoh rekursi 0 kali
                                                        save_dir = "Wrong Direction" + glob_slash + "[" + str(track_id) + "]" + "-" + str(final_string) + "_WrongDirection_" + ".jpg"
                                                        cv2.imwrite(str('database'+ glob_slash + 'static'+ glob_slash + save_dir), frame)
                                                        self.get_violence_wrong_dir_id.append(track_id)
                                                        self.get_violence_wrong_dir_date.append(str(final_string))
                                                    elif len(self.get_violence_wrong_dir_id) == 0:
                                                        self.get_violence_wrong_dir_id.append(0)
                                                        self.get_violence_wrong_dir_date.append(0)
                                    
                                            #deteksi lawan arah (kiri)
                                            if area[1] == "LEFT" :
                                                if index_direct_array is not None and counter_dir >= 5 and flag_string == "NONE":
                                                    self.direct_array[index_direct_array] =  (track_id, xp, yp, xp_1, yp_1, cek_dir, counter_dir, "LEFT")

                                                if int(cek_dir) > 0 and counter_dir >= 20 and flag_string == "LEFT":
                                                    print("pelanggaran LEFT track_id: ", track_id)
                                                    y1_new = y1-50
                                                    if y1-50 < 0.0:
                                                        y1_new = 0
                                                
                                                    y2_new = y2+50
                                                    if (y2+50) > 900:
                                                        y2_new = 900
                                        
                                                    x1_new = x1-50
                                                    if (x1-50) < 0.0:
                                                        x1_new = 0

                                                    x2_new = x2+50
                                                    if (x2+50) > 1600:
                                                        x2_new = 1600

                                                    box.xyxy = [[x1_new, y1_new, x2_new, y2_new]]
                                                    cropped_images_wrong_dir = frame_get[y1_new:y2_new, x1_new:x2_new]
                                                    text_ = "Wrong Direction"
                                                    cv2.putText(frame, text_, (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                                    if not track_id in self.get_violence_wrong_dir_id and len(cropped_images_wrong_dir)>0 and track_id != 0:
                                                        initial_time_final_string = get_current_time()
                                                        final_string = recursive_output(initial_time_final_string, 0)  # contoh rekursi 0 kali
                                                        save_dir =  "Wrong Direction" + glob_slash + "[" + str(track_id) + "]" + "-" + str(final_string) + "_WrongDirection_" + ".jpg"
                                                        cv2.imwrite(str('database'+ glob_slash + 'static'+ glob_slash + save_dir), frame)
                                                        self.get_violence_wrong_dir_id.append(track_id)
                                                        self.get_violence_wrong_dir_date.append(str(final_string))   
                                                    elif len(self.get_violence_wrong_dir_id) == 0:
                                                        self.get_violence_wrong_dir_id.append(0)
                                                        self.get_violence_wrong_dir_date.append(0)

                                            #deteksi salib kiri
                                            if not track_id in self.get_violence_wrong_dir_id:
                                                if cek_dir < 0 and counter_dir >= 21:
                                                    self.update_or_append_tuples(self.save_left_specific_val_id, (track_id, (x_point, y_point)))          
                                                    self.update_or_append_single_var(self.moving_left_dir_id, track_id)
                                                    print(track_id, "bergerak di lajur kiri")

                                                    y1_new = y1-50
                                                    if y1-50 < 0.0:
                                                        y1_new = 0

                                                    y2_new = y2+50
                                                    if (y2+50) > 900:
                                                        y2_new = 900
                                        
                                                    x1_new = x1-50
                                                    if (x1-50) < 0.0:
                                                        x1_new = 0

                                                    x2_new = x2+50
                                                    if (x2+50) > 1600:
                                                        x2_new = 1600

                                                    violence_category = "Overtaking"
                                                    cropped_images_overtaking = frame_get[y1_new:y2_new, x1_new:x2_new]
                                                    for i, value_id in enumerate(self.moving_left_dir_id):
                                                        get_array = []
                                                        get_array = self.get_multi_value_by_id(self.moving_left_dir_id, value_id) 

                                                        last_x, last_y = 0, 0
                                                        if len(get_array) != 0:
                                                            last_x, last_y  = get_array[0], get_array[1]
                                                        else:
                                                            last_x, last_y = x_point, y_point
                                                        
                                                        if track_id < value_id:
                                                            if x_point < last_x and y_point < last_y:
                                                                print("SALIP KIRI !! sisi kiri")
                                                                text_ = "Overtaking"
                                                                cv2.putText(frame, text_, (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                                                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

                                                                if not track_id in self.get_violence_overtaking_id and len(cropped_images_overtaking)>0 and track_id != 0:
                                                                    initial_time_final_string = get_current_time()
                                                                    final_string = recursive_output(initial_time_final_string, 0)  # contoh rekursi 0 kali
                                                                    save_dir = "Overtaking" + glob_slash + "[" + str(track_id) + "]" + "-" + str(final_string) + "_Overtaking_" + ".jpg"
                                                                    cv2.imwrite(str('database'+ glob_slash + 'static'+ glob_slash + save_dir), frame)
                                                                    self.get_violence_overtaking_id.append(track_id)
                                                                    self.get_violence_overtaking_date.append(str(final_string))
                                                                elif len(self.get_violence_wrong_dir_id) == 0:
                                                                    self.get_violence_overtaking_id.append(0)
                                                                    self.get_violence_overtaking_date.append(0)                                                    
                                                            
                                                if cek_dir > 0 and counter_dir >= 21:
                                                    self.update_or_append_tuples(self.save_right_specific_val_id, (track_id, (x_point, y_point)))
                                                    self.update_or_append_single_var(self.moving_right_dir_id, track_id) 
                                                    print(track_id, "bergerak di lajur kanan")

                                                    y1_new = y1-50
                                                    if y1-50 < 0.0:
                                                        y1_new = 0

                                                    y2_new = y2+50
                                                    if (y2+50) > 900:
                                                        y2_new = 900
                                        
                                                    x1_new = x1-50
                                                    if (x1-50) < 0.0:
                                                        x1_new = 0

                                                    x2_new = x2+50
                                                    if (x2+50) > 1600:
                                                        x2_new = 1600

                                                    violence_category = "Overtaking"
                                                    cropped_images_overtaking = frame_get[y1_new:y2_new, x1_new:x2_new]
                                                    for i, value_id in enumerate(self.moving_right_dir_id):
                                                        get_array = []
                                                        get_array = self.get_multi_value_by_id(self.save_right_specific_val_id, value_id) 

                                                        last_x, last_y = 0, 0
                                                        if len(get_array) != 0:
                                                            last_x, last_y  = get_array[0], get_array[1]
                                                        else:
                                                            last_x, last_y = x_point, y_point

                                                        if track_id < value_id:
                                                            if x_point > last_x and y_point > last_y:
                                                                print("SALIP KANAN !! sisi kanan")
                                                                text_ = "Overtaking"
                                                                cv2.putText(frame, text_, (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                                                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

                                                                if not track_id in self.get_violence_overtaking_id and len(cropped_images_overtaking)>0 and track_id != 0:
                                                                    initial_time_final_string = get_current_time()
                                                                    final_string = recursive_output(initial_time_final_string, 0)  # contoh rekursi 0 kali
                                                                    save_dir = "Overtaking" + glob_slash + "[" + str(track_id) + "]" + "-" + str(final_string) + "_Overtaking_" + ".jpg"
                                                                    cv2.imwrite(str('database'+ glob_slash + 'static'+ glob_slash + save_dir), frame)
                                                                    self.get_violence_overtaking_id.append(track_id)
                                                                    self.get_violence_overtaking_date.append(str(final_string))
                                                                elif len(self.get_violence_wrong_dir_id) == 0:
                                                                    self.get_violence_overtaking_id.append(0)
                                                                    self.get_violence_overtaking_date.append(0)

                                    if area[1] == "POINT_A" or area[1] == "POINT_B": 
                                        last_speed = self.get_single_value_by_id(self.last_speed, track_id)
                                        cel_first_cor = []
                                        distance = 0.00

                                        self.set_value_once(self.get_point_A_B, (track_id, area[1]))
                                        get_point_A_B = self.get_single_string_value_by_id(self.get_point_A_B, track_id)
                                        validation_point = get_point_A_B == "POINT_A" or get_point_A_B == "POINT_B"
                                        validation_area_point_A_B = get_point_A_B == "POINT_A" and area[1] == "POINT_B" or get_point_A_B == "POINT_B" and area[1] == "POINT_A"
                                        
                                        save_cor = (x_point, y_point)
                                        if validation_point == True:
                                            self.set_value_once(self.get_first_point_for_speed, (track_id, save_cor))

                                        if validation_point == True:
                                            cel_first_cor = self.get_multi_value_by_id(self.get_first_point_for_speed, track_id)
                                            if len(cel_first_cor) > 0:
                                                distance = self.uclidean_vector(x_point, y_point, int(cel_first_cor[0]), int(cel_first_cor[1]))

                                        counter_time = self.get_single_value_by_id(self.array_time, track_id)
                                        if counter_time <= 0:
                                            counter_time = 1
                                        
                                        speed_ = round((distance / (counter_time/fps)) * (self.width_in_meter / self.width_in_pixel) * self.calibration_factor * 3.6, 2) #3.6 m/s to km/jam
                                        self.update_or_append_tuples(self.last_speed, (track_id, speed_))
                                        text = str(round(speed_,2)) + " km/h"
                                        window_limit = (last_speed * 2)
                                        speed_out_of_range = speed_ >= window_limit or speed_ <= (window_limit/4) or speed_ > (self.max_speed * 2)

                                        validation_vehicle = self.class_ids[int(self.track_id_array.index(track_id))] in self.detected_values
                                        if speed_out_of_range == True:
                                            speed_ = last_speed #jika speed out of range, maka nilai speed tidak diupdate
                                        else:
                                            if validation_vehicle == True and validation_point == True and validation_area_point_A_B == True:
                                                cv2.putText(frame, text, (int(x1), int(y2+50)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
                                        
                                        y1_new = y1-50
                                        if y1-50 < 0.0:
                                            y1_new = 0
                                                
                                        y2_new = y2+50
                                        if (y2+50) > 900:
                                            y2_new = 900
                                        
                                        x1_new = x1-50
                                        if (x1-50) < 0.0:
                                            x1_new = 0

                                        x2_new = x2+50
                                        if (x2+50) > 1600:
                                            x2_new = 1600
            
                                        #pelanggaran overspeed
                                        if speed_ > self.max_speed:
                                            cropped_images_overspeed = frame_get[y1_new:y2_new, x1_new:x2_new]
                                            speed_limitation = speed_ <= window_limit and speed_ >= (window_limit/4) and speed_ < (self.max_speed * 2)
                                            validation_overspeed = speed_limitation == True and (not track_id in self.get_violence_overspeed_id) and validation_area_point_A_B == True and len(cropped_images_overspeed) != 0 and track_id != 0
                                            if validation_overspeed == True:
                                                initial_time_final_string = get_current_time()
                                                final_string = recursive_output(initial_time_final_string, 0)  # contoh rekursi 0 kali
                                                text = "Overspeed !!"
                                                frame = cv2.putText(frame, text, (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                                                frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2) 
                                                save_dir = "Overspeed" + glob_slash + "[" + str(track_id) + "]" + "-" + str(final_string) + "_overspeed_" + ".jpg"
                                                cv2.imwrite(str('database'+ glob_slash + 'static'+ glob_slash + save_dir), frame)
                                                cv2.waitKey(100)
                                                violence_category = "Overspeed"
                                                speed_get = speed_
                                                vehicle = str(self.model_yolo.model.names[self.class_ids[int(self.track_id_array.index(track_id))]])
                                                
                                                get_val = queue.Queue() 
                                                detection_plat = threading.Thread(target=lambda:detect_plat_and_crop_with_retries(get_val, violence_category, cropped_images_overspeed, track_id))
                                                detection_plat.start()
                                                detection_plat.join()
                                                date_str, get_id = "", track_id
                                                if not get_val.empty():
                                                    date_str, get_id = get_val.get()
                                                    
                                                name_file = date_str + "_" + str(track_id) + ".jpg"
                                                dir_plat_image = "plat_number_" + violence_category + glob_slash + name_file   
                                                dir_plat_image_html =   "plat_number_" + violence_category + glob_slash_html + name_file
                                                save_dir_datalog = "Overspeed" + glob_slash_html + "[" + str(track_id) + "]" + "-" + str(final_string) + "_overspeed_" + ".jpg" 
                                                self.save_datalog(str(track_id), final_string, self.dir_checker(dir_plat_image, dir_plat_image_html), speed_get, self.max_speed, violence_category, vehicle, self.location, save_dir_datalog)
                                                self.get_violence_overspeed_id.append(track_id)
                                            elif speed_limitation == False:
                                                text = "Not Detected !!"
                                                cv2.putText(frame, text, (int(x_point), int(y_point)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
                                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2) 
                                            elif len(self.get_violence_overspeed_id) == 0:
                                                self.get_violence_overspeed_id.append(0)

                                        #proses pembacaan plat nomor dan deteksi
                                        if track_id in self.get_violence_helm_id and validation_area_point_A_B == True:
                                            violence_category = "Helmet"
                                            get_date = self.get_violence_helm_date[int(self.get_violence_helm_id.index(track_id))]
                                            cek_database = self.check_value_in_column("date", get_date)

                                            if cek_database == False:
                                                save_dir = "Helmet" + glob_slash + "[" + str(track_id) + "]" + "-" + str(get_date) + "_no-helmet_" + ".jpg"
                                                vehicle = str(self.model_yolo.model.names[self.class_ids[int(self.track_id_array.index(track_id))]])
                                                speed_get = speed_
                                                cropped_motor_cycle = frame_get[y1_new:y2_new, x1_new:x2_new]  
                                                get_val = queue.Queue() 
                                                detection_plat = threading.Thread(target=lambda:detect_plat_and_crop_with_retries(get_val, violence_category, cropped_motor_cycle, track_id))
                                                detection_plat.start()
                                                detection_plat.join()
                                                date_str, get_id = "", track_id
                                                if not get_val.empty():
                                                    date_str, get_id = get_val.get()
                                                name_file = date_str + "_" + str(track_id) + ".jpg"
                                                dir_plat_image =   "plat_number_" + violence_category + glob_slash + name_file
                                                dir_plat_image_html =   "plat_number_" + violence_category + glob_slash_html + name_file
                                                save_dir_datalog = "Helmet" + glob_slash_html + "[" + str(track_id) + "]" + "-" + str(final_string) + "_no-helmet_" + ".jpg" 
                                                self.save_datalog(str(track_id), get_date, self.dir_checker(dir_plat_image, dir_plat_image_html), speed_get, self.max_speed, violence_category, vehicle, self.location, save_dir_datalog)
                                        
                                        #proses pembacaan plat nomor dan deteksi
                                        if track_id in self.get_violence_seatbelt_id and validation_area_point_A_B == True:                                            
                                            violence_category = "Seatbelt"
                                            get_date = self.get_violence_seatbelt_date[int(self.get_violence_seatbelt_id.index(track_id))]
                                            cek_database = self.check_value_in_column("date", get_date)
                                            if cek_database == False:                                                
                                                speed_get = speed_
                                                cropped_images_seatbelt = frame_get[y1_new:y2_new, x1_new:x2_new]                                                
                                                save_dir = "Seatbelt" + glob_slash + "[" + str(track_id) + "]" + "-" + str(get_date) + "_no-seatbelt_" + ".jpg"
                                                vehicle = str(self.model_yolo.model.names[self.class_ids[int(self.track_id_array.index(track_id))]])
                                                get_val = queue.Queue() 
                                                detection_plat = threading.Thread(target=lambda:detect_plat_and_crop_with_retries(get_val, violence_category, cropped_images_seatbelt, track_id))
                                                detection_plat.start()
                                                detection_plat.join()
                                                date_str, get_id = "", track_id
                                                if not get_val.empty():
                                                    date_str, get_id = get_val.get()                                                
                                                name_file = date_str + "_" + str(track_id) + ".jpg"
                                                dir_plat_image =   "plat_number_" + violence_category + glob_slash + name_file
                                                dir_plat_image_html = "plat_number_" + violence_category + glob_slash_html + name_file
                                                save_dir_datalog = "Seatbelt" + glob_slash_html + "[" + str(track_id) + "]" + "-" + str(final_string) + "_no-seatbelt_" + ".jpg" 
                                                self.save_datalog(str(track_id), get_date, self.dir_checker(dir_plat_image, dir_plat_image_html), speed_get, self.max_speed, violence_category, vehicle, self.location, save_dir_datalog)
                                        
                                        #proses pembacaan plat nomor dan deteksi
                                        if track_id in self.get_violence_wrong_dir_id and validation_area_point_A_B == True:
                                            violence_category = "Wrong_direction"
                                            get_date = self.get_violence_wrong_dir_date[int(self.get_violence_wrong_dir_id.index(track_id))]
                                            cek_database = self.check_value_in_column("date", get_date)
                                            if cek_database == False:
                                                save_dir =   "Wrong Direction" + glob_slash + "[" + str(track_id) + "]" + "-" + str(get_date) + "_WrongDirection_" + ".jpg"
                                                vehicle = str(self.model_yolo.model.names[self.class_ids[int(self.track_id_array.index(track_id))]])
                                                speed_get = speed_
                                                cropped_images_wrong_dir = frame_get[y1_new:y2_new, x1_new:x2_new]
                                                get_val = queue.Queue() 
                                                detection_plat = threading.Thread(target=lambda:detect_plat_and_crop_with_retries(get_val, violence_category, cropped_images_wrong_dir, track_id))
                                                detection_plat.start()
                                                detection_plat.join()
                                                date_str, get_id = "", track_id
                                                if not get_val.empty():
                                                    date_str, get_id = get_val.get()  
                                                name_file = date_str + "_" + str(track_id) + ".jpg"
                                                dir_plat_image =   "plat_number_" + violence_category + glob_slash + name_file
                                                dir_plat_image_html =   "plat_number_" + violence_category + glob_slash_html + name_file
                                                save_dir_datalog = "Wrong Direction" + glob_slash_html + "[" + str(track_id) + "]" + "-" + str(final_string) + "_WrongDirection_" + ".jpg" 
                                                self.save_datalog(str(track_id), get_date, self.dir_checker(dir_plat_image, dir_plat_image_html), speed_get, self.max_speed, violence_category, vehicle, self.location, save_dir_datalog)
                                            
                                        #proses pembacaan plat nomor dan deteksi
                                        if track_id in self.get_violence_overtaking_id and validation_area_point_A_B == True:
                                            violence_category = "Overtaking"
                                            get_date = self.get_violence_overtaking_date[int(self.get_violence_overtaking_id.index(track_id))]
                                            cek_database = self.check_value_in_column("date", get_date)

                                            if cek_database == False:
                                                save_dir = "Overtaking" + glob_slash + "[" + str(track_id) + "]" + "-" + str(get_date) + "_Overtaking_" + ".jpg"
                                                vehicle = str(self.model_yolo.model.names[self.class_ids[int(self.track_id_array.index(track_id))]])
                                                speed_get = speed_
                                                cropped_images_overtaking = frame_get[y1_new:y2_new, x1_new:x2_new]  
                                                get_val = queue.Queue() 
                                                detection_plat = threading.Thread(target=lambda:detect_plat_and_crop_with_retries(get_val, violence_category, cropped_images_overtaking, track_id))
                                                detection_plat.start()
                                                detection_plat.join()
                                                date_str, get_id = "", track_id
                                                if not get_val.empty():
                                                    date_str, get_id = get_val.get()
                                                name_file = date_str + "_" + str(track_id) + ".jpg"
                                                dir_plat_image =   "plat_number_" + violence_category + glob_slash + name_file
                                                dir_plat_image_html =   "plat_number_" + violence_category + glob_slash_html + name_file
                                                save_dir_datalog = "Overtaking" + glob_slash_html + "[" + str(track_id) + "]" + "-" + str(final_string) + "_Overtaking_" + ".jpg" 
                                                self.save_datalog(str(track_id), get_date, self.dir_checker(dir_plat_image, dir_plat_image_html), speed_get, self.max_speed, violence_category, vehicle, self.location, save_dir_datalog)

                            #simpan data terakhir dari x_point, y_point 
                            self.update_or_append_tuples(self.last_track_id, (track_id, (x_point, y_point)))
                            #setup buat track data       
                            track = self.track_history[track_id]
                            track.append((float(x_point), float(y_point)))
                            
                            if len(track) > 30:
                                track.pop(0)
                            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                        
                        self.track_id_array = results[0].boxes.id.numpy().tolist()
                        self.class_ids = results[0].boxes.cls.numpy().tolist()

                        # Mengecek dan memotong jika lebih dari 30
                        if isinstance(self.save_id, list) and len(self.save_id) >= 30:
                            self.save_id = self.save_id[-20:]

                        if isinstance(self.array_time, list) and len(self.array_time) >= 30:
                            self.array_time = self.array_time[-20:]
                        
                        if isinstance(self.get_point_A_B, list) and len(self.get_point_A_B) >= 30:
                            self.get_point_A_B = self.get_point_A_B[-20:]
                        
                        if isinstance(self.get_first_point_for_speed, list) and len(self.get_first_point_for_speed) >= 30:
                            self.get_first_point_for_speed = self.get_first_point_for_speed[-20:]
                        
                        if isinstance(self.point_get_category, list) and len(self.point_get_category) >= 30:
                            self.point_get_category = self.point_get_category[-20:]
                      
                        if isinstance(self.moving_right_dir_id, list) and len(self.moving_right_dir_id) >= 15:
                            self.moving_right_dir_id = self.moving_right_dir_id[-7:]
                        
                        if isinstance(self.moving_left_dir_id, list) and len(self.moving_left_dir_id) >= 15:
                            self.moving_left_dir_id = self.moving_left_dir_id[-7:]

                        if isinstance(self.get_violence_helm_id, list) and len(self.get_violence_helm_id) >= 20:
                            self.get_violence_helm_id = self.get_violence_helm_id[-10:]
                        
                        if isinstance(self.get_violence_seatbelt_id, list) and len(self.get_violence_seatbelt_id) >= 20:
                            self.get_violence_seatbelt_id = self.get_violence_seatbelt_id[-10:]

                        if isinstance(self.get_violence_overspeed_id, list) and len(self.get_violence_overspeed_id) >= 20:
                            self.get_violence_overspeed_id = self.get_violence_overspeed_id[-10:]


                        if isinstance(self.get_violence_overtaking_id, list) and len(self.get_violence_overtaking_id) >= 20:
                            self.get_violence_overtaking_id = self.get_violence_overtaking_id[-10:]


                        if isinstance(self.get_violence_wrong_dir_id, list) and len(self.get_violence_wrong_dir_id) >= 20:
                            self.get_violence_wrong_dir_id = self.get_violence_wrong_dir_id[-10:]
    
                            # Tanggal terkait pelanggaran
                        if isinstance(self.get_violence_helm_date, list) and len(self.get_violence_helm_date) >= 20:
                            self.get_violence_helm_date = self.get_violence_helm_date[-10:]

                        if isinstance(self.get_violence_seatbelt_date, list) and len(self.get_violence_seatbelt_date) >= 20:
                            self.get_violence_seatbelt_date = self.get_violence_seatbelt_date[-10:]

                        if isinstance(self.get_violence_wrong_dir_date, list) and len(self.get_violence_wrong_dir_date) >= 20:
                            self.get_violence_wrong_dir_date = self.get_violence_wrong_dir_date[-10:]

                        if isinstance(self.get_violence_overtaking_date, list) and len(self.get_violence_overtaking_date) >= 20:
                            self.get_violence_overtaking_date = self.get_violence_overtaking_date[-10:]

                            # Flag pelanggaran
                        if isinstance(self.get_violence_helm_flag, list) and len(self.get_violence_helm_flag) >= 20:
                            self.get_violence_helm_flag = self.get_violence_helm_flag[-10:]

                        if isinstance(self.get_violence_seatbelt_flag, list) and len(self.get_violence_seatbelt_flag) >= 20:
                            self.get_violence_seatbelt_flag = self.get_violence_seatbelt_flag[-10:]

                            # Membatasi panjang array menjadi 20 elemen terakhir
                        if isinstance(self.save_left_specific_val_id, list) and len(self.save_left_specific_val_id) >= 20:
                            self.save_left_specific_val_id = self.save_left_specific_val_id[-10:]

                        if isinstance(self.save_right_specific_val_id, list) and len(self.save_right_specific_val_id) >= 20:
                            self.save_right_specific_val_id = self.save_right_specific_val_id[-10:]

                        if isinstance(self.last_track_id, list) and len(self.last_track_id) >= 20:
                            self.last_track_id = self.last_track_id[-10:]
    

                        # Mengecek track_id_array dan elemen lainnya
                        if len(self.track_id_array) >= 50:
                            # Track dan data terkait
                            self.track_id_array = self.track_id_array[-20:]
                            self.class_ids = self.class_ids[-20:]
                            self.direct_array = self.direct_array[-20:]
                            self.sum_array = self.sum_array[-20:]
                            self.last_speed = self.last_speed[-20:]
    
                for area in self.areas:
                    coords = list(map(int, area[2].split(',')))
                    points = np.array(coords, dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(frame, [points], isClosed=True, color=(0, 0, 255), thickness=1)

                for line in self.lines:
                    x1, y1, x2, y2 = line[2], line[3], line[4], line[5]
                    color = (255, 0, 0)  # Warna biru
                    thickness = 1
                    start_point = (x1, y1)  # Titik awal (x, y)
                    end_point = (x2, y2)    # Titik akhir (x, y)
                    cv2.line(frame, start_point, end_point, color, thickness)
                       
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.reference_image = Image.fromarray(img)
                self.reference_imgtk = ImageTk.PhotoImage(image=self.reference_image)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.reference_imgtk)

        # Recursively call the method to process the next frame
        if self.use_camera:
            self.root.after(10, self.capture_and_process_frames)

    #def capture_photo(self):
    #    if self.last_frame is not None:
    #        # Save the last frame as an image
    #        img = Image.fromarray(cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2RGB))
    #        save_path = f"captured_image_{len(self.cropped_images)}.jpg"
    #        img.save(save_path)
    #        self.cropped_images.append(save_path)
    #        self.status.set(f"Photo saved to {save_path}")

    def close(self):
        if self.camera is not None:
            self.camera.release()
        self.root.destroy()

if __name__ == "__main__":
    root = Tk()
    app = VideoApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
print("exit")
lock_file.unlink()