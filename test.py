import cv2
from datetime import datetime
glob_slash = "\\" #windows
# Membaca gambar dari file
image = cv2.imread(str('database'+glob_slash+'BikesHelmets6.png'))  # Ganti dengan nama file gambar Anda

def recursive_output(current_string, repeat_count):
    # Base case: Jika repeat_count sudah 0, kembalikan current_string
    if repeat_count <= 0:
        return current_string
    else:
        # Rekursi: Tambahkan string baru ke current_string dan ulangi
        new_string = current_string + " " + get_current_time()
        return recursive_output(new_string, repeat_count - 1)

def get_current_time():
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H-%M-%S")

# Cek apakah gambar berhasil dibaca
if image is None:
    print("Error: Gambar tidak ditemukan.")
else:
    # Menyimpan gambar ke file baru
    print(str('database'+glob_slash+'out.jpg'))
    print(len(image))
    track_id = 12
    initial_time_final_string = get_current_time()
    final_string = recursive_output(initial_time_final_string, 0)  # contoh rekursi 0 kali
    print(final_string)
    path = str('database'+glob_slash+'static'+glob_slash+'Helmet'+glob_slash+'['+str(track_id)+']'+'-'+str(final_string)+'_no-helmet_'+'.jpg')
    print(len(path))
    cek=cv2.imwrite(path, image)  # Ganti dengan nama file output yang diinginkan
    print("Gambar berhasil disimpan sebagai output_image.jpg")
    print(cek)
