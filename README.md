# 🚦 YOLO for Traffic Violence Detection

This project leverages **YOLO (You Only Look Once)** to detect various traffic violations in real-time, improving road safety and compliance. The software identifies and tracks:

- **Overtaking** 🚗
- **Overspeeding** 🚨
- **Wrong Direction** 🚧
- **No Helmet Use** 🏍️
- **No Seatbelt Use** 🚗

## ✨ Features

✔ **Real-time Detection**: Instantly identifies traffic violations using YOLOv8 models.  
✔ **Safety Distance Calculation**: Measures vehicle distances to prevent accidents.  
✔ **Web-Based Monitoring**: Secure and user-friendly local web interface.  
✔ **Security System**: Ensures data protection and reliable monitoring.  

---

## 🛠 Technologies Used

| Technology  | Purpose                          |
|------------|----------------------------------|
| **YOLOv8** | Object detection & tracking     |
| **Flask**  | Web interface backend           |
| **SQLite3**| Local database management       |
| **OpenCV** | Image processing                |
| **Python** | Programming Language          |

---

## 🚀 Installation & Setup

### 1️⃣ **Download Full Directory**
📥 Download the full directory containing `.exe` files and dependencies from Google Drive:

[🔗 Download Directory](https://drive.google.com/file/d/1zEBnQUcYz4C9ExlL_4W57DHypXcI55RV/view?usp=drivesdk)

This directory includes all necessary files and is ready to run directly.

### 2️⃣ **Running the Application**

| File         | Function                                  |
|-------------|-------------------------------------------|
| `main.exe`  | Runs the traffic violation detection system |
| `server.exe`| Starts the local web interface for monitoring |

### 3️⃣ **Important Notes**
📌 The GitHub repository only contains the source code and **does not** include `.exe` files. Download the full package from Google Drive.

### 4️⃣ **System Requirements**

✅ **VGA**: Graphics card with **8GB VRAM** or more recommended.  
✅ **RAM**: Minimum **16GB RAM** suggested for optimal performance.  

### 5️⃣ **Troubleshooting**

⚠ **File Size Limitations**: Certain files are too large for GitHub; the full package is available via Google Drive.

---

## 🎬 Running Instructions

### 🔹 Running `main.exe`

#### 📡 Displaying IP Camera
```bash
https://<IP_ADDRESS>:<PORT>/<STREAM_PATH>
```

#### 📡 Displaying Hikvision Camera (RTSP)
```bash
rtsp://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<STREAM_PATH>
```

#### ▶ Running Default Video
```bash
./cctv example/5.mp4
```
- Press **Connect to Camera** to start.
- Press again to **stop**.

#### 🎯 Setting Custom Video
1. **Remove all areas**: Press **Undo Area** until cleared.
2. **Create new monitoring areas**:
   - **POINT_A** → Marks vehicle’s start position.
   - **POINT_B** → Marks vehicle’s end position for speed measurement.
   - **LEFT** → Defines left lane for wrong-way detection.
   - **RIGHT** → Defines right lane for wrong-way detection.

📷 **Example Area Setup:**  
![Example Area Setup](https://drive.google.com/uc?id=1lrbDVIgVlaDQztWEwS24pkGwOQpgqnUP)

---

### 🔹 Running `server.exe`
- **Username**: `admin`  
- **Password**: `admin`

📌 **Ensure** `server.exe` is running for web-based monitoring and logging of detected violations.
