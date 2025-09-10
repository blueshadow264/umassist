# Initial commit
import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 

# Capture screenshot (replace with actual game window capture)
img = cv2.imread('screenshot.png')

# OCR
text = pytesseract.image_to_string(img)
print(text)