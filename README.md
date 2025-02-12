# YOLO for Traffic Violence Detection 🚦

This project leverages **YOLO (You Only Look Once)** to detect various traffic violations in real-time, aimed at improving road safety and compliance. The software identifies and tracks:

- **Overtaking** 🚗
- **Overspeeding** 🚨
- **Wrong Direction** 🚧
- **No Helmet Use** 🏍️
- **No Seatbelt Use** 🚗

## Features
- **Real-time Detection**: Instant identification of traffic violations using YOLOv8 models.
- **Safety Distance Calculation**: The system calculates the safety distance between vehicles to prevent accidents.
- **Web-Based Monitoring**: A secure, user-friendly local web interface to view and monitor the results.
- **Security System**: Integrated with security protocols to ensure data protection and reliable monitoring.

## Technologies Used
- **YOLOv8** for object detection and tracking
- **Flask** for the web interface
- **SQLite3** for local database management
- **OpenCV** for image processing
- **Python** for backend development

## Installation & Setup Instructions

1. **Download Full Directory**:
   - Download the full directory containing the built `.exe` files and all dependencies from Google Drive: [Download Directory](https://drive.google.com/file/d/1zEBnQUcYz4C9ExlL_4W57DHypXcI55RV/view?usp=drivesdk)
   - This directory includes all necessary files and is ready to run directly.

2. **Running the Application**:
   - **Main Code**: Run `main.exe` to execute the primary traffic violation detection system.
   - **Web Server Monitoring**: Run `server.exe` to initiate the local web interface for real-time monitoring of traffic violations.

3. **Important Note**:
   - This GitHub repository only contains the source code and does not include the built `.exe` files. To run the application directly, please download the full directory from Google Drive, as mentioned above.

4. **System Requirements**:
   - **VGA**: A graphics card with 8GB or more VRAM is recommended.
   - **RAM**: A minimum of 16GB RAM is suggested for optimal performance.

5. **Troubleshooting**:
   - **File Size Limitations**: Certain files are too large to host on GitHub; hence, the complete package is available only through the Google Drive link above.

## Running Instructions

### 1. Running `main.exe`

#### Displaying IP Camera
```
https://192.168.1.100:80/video
```

#### Displaying Hikvision Camera (RTSP)
```
rtsp://admin:12345@192.168.1.100:554/h264/ch1/main/av_stream
```

#### Running Default Video
```
./cctv example/5.mp4
```
- Press **Connect to Camera** to start.
- Press again to **stop**.

#### Setting Custom Video
1. **Remove all areas**: Press **Undo Area** until all areas are cleared.
2. **Create new monitoring areas**:
   - **POINT_A** → Marks a vehicle’s position from **POINT_A** to **POINT_B** for speed measurement.
   - **POINT_B** → Marks a vehicle’s position from **POINT_B** to **POINT_A** for speed measurement.
   - **LEFT** → Defines the left lane to detect wrong-way violations.
   - **RIGHT** → Defines the right lane to detect wrong-way violations.

📷 **Example Area Setup:**
![Example Area Setup](https://drive.google.com/uc?id=1lrbDVIgVlaDQztWEwS24pkGwOQpgqnUP)

---

### 2. Running `server.exe`
- **Username**: `admin`
- **Password**: `admin`

📌 **Note**: Ensure that `server.exe` is running for web-based monitoring and logging of detected violations.

