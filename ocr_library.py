import easyocr
import cv2

class OCRProcessor:
    def __init__(self, languages=['en']):
        """Inisialisasi reader EasyOCR dengan bahasa yang diinginkan."""
        self.reader = easyocr.Reader(languages)

    def read_text(self, image_path):
        """Membaca teks dari gambar yang diberikan path-nya dan mengembalikan hasil sebagai array of strings."""
        # Membaca gambar dari path
        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(f"Image not found at the path: {image_path}")

        # Melakukan OCR menggunakan EasyOCR
        result = self.reader.readtext(image)
        texts = [text for (_, text, _) in result]  # Mengumpulkan semua teks dalam array
        return texts

    def recursive_texts(self, texts):
        """Menggabungkan teks menjadi satu string atau array rekursif jika ada beberapa."""
        if not texts:
            return ""
        elif len(texts) == 1:
            return texts[0]
        else:
            return texts  # Kembalikan array jika lebih dari satu teks

    def process_image(self, image_path):
        """Proses gambar dan kembalikan teks yang ditemukan sebagai string atau array of strings."""
        texts = self.read_text(image_path)
        return self.recursive_texts(texts)

# Fungsi utama untuk digunakan dalam file lain
def process_image(image_path):
    ocr_processor = OCRProcessor()
    return ocr_processor.process_image(image_path)

