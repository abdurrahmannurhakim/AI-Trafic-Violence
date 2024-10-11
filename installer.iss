[Setup]
AppName=CCTV AI Trafic Violence
AppVersion=2.1
DefaultDirName={pf}\CCTV AI Trafic Violence
DefaultGroupName=CCTV AI Trafic Violence
OutputBaseFilename=CCTV_AI_Trafic_Violence
Compression=lzma
SolidCompression=yes

[Files]
; Menyalin file model yang harus dibaca tanpa perizinan
Source: "seat_belt_5.pt"; DestDir: "{app}"; Flags: ignoreversion
Source: "helmet_9.pt"; DestDir: "{app}"; Flags: ignoreversion
Source: "plat_license.pt"; DestDir: "{app}"; Flags: ignoreversion
Source: "yolov8n.pt"; DestDir: "{app}"; Flags: ignoreversion
Source: "yolov8s.pt"; DestDir: "{app}"; Flags: ignoreversion
Source: "yolov8m.pt"; DestDir: "{app}"; Flags: ignoreversion
Source: "yolov8l.pt"; DestDir: "{app}"; Flags: ignoreversion
Source: "yolov8x.pt"; DestDir: "{app}"; Flags: ignoreversion

; Menyalin file database
Source: "database\configuration.db"; DestDir: "{app}\database"; Flags: ignoreversion
Source: "database\database.db"; DestDir: "{app}\database"; Flags: ignoreversion
Source: "database\login.db"; DestDir: "{app}\database"; Flags: ignoreversion

; Semua file dalam folder lain akan disalin ke direktori instalasi
Source: "*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Shortcut untuk main.exe di Desktop dan Start Menu
Name: "{commondesktop}\CCTV AI Trafic Violence - Main"; Filename: "{app}\main.exe"
Name: "{group}\CCTV AI Trafic Violence"; Filename: "{app}\main.exe"

; Shortcut untuk server.exe di Desktop dan Start Menu
Name: "{commondesktop}\CCTV Web Server"; Filename: "{app}\server.exe"
Name: "{group}\CCTV Web Server"; Filename: "{app}\server.exe"

; Shortcut untuk reset.exe di Desktop dan Start Menu
Name: "{commondesktop}\CCTV Error Reset"; Filename: "{app}\reset.exe"
Name: "{group}\CCTV Error Reset"; Filename: "{app}\reset.exe"

[Run]
; Jalankan install.bat setelah instalasi
Filename: "{app}\install.bat"; Description: "Menjalankan script instalasi"; Flags: runhidden

; Menghapus atribut read-only setelah instalasi
Filename: "cmd.exe"; Parameters: "/c attrib -r ""{app}\seat_belt_5.pt"" ""{app}\helmet_9.pt"" ""{app}\plat_license.pt"" ""{app}\yolov8n.pt"" ""{app}\yolov8s.pt"" ""{app}\yolov8m.pt"" ""{app}\yolov8l.pt"" ""{app}\yolov8x.pt"""; Flags: runhidden
