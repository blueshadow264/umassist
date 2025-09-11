import pytesseract
import keyboard
import tkinter as tk
import platform
from PIL import ImageGrab, ImageTk
import threading

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

using_debug_mode = False

class DragScreenshotPanel:  
    def __init__(self, root: tk.Tk, master: tk.Toplevel, screenshot_img, callback=None, cancel_callback=None):
        self.root = root
        self.master = master
        self.callback = callback
        self.cancel_callback = cancel_callback
        self.start_x = None
        self.start_y = None
        self.rect = None

        # Convert PIL image to Tkinter PhotoImage
        self.tk_img = ImageTk.PhotoImage(screenshot_img)
        self.canvas = tk.Canvas(master, cursor="cross", width=screenshot_img.width, height=screenshot_img.height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        # Display the screenshot as the canvas background
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.screenshot_img = screenshot_img  # Save for cropping

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='white', width=2)  

    def on_mouse_drag(self, event):  
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)
        self.canvas.delete(self.rect)
        dy = abs(y2-y1)
        dx = abs(x2-x1)
        if dy*dx != 0:
            self.master.withdraw()
            # Crop from the frozen screenshot, not a new grab
            img = self.screenshot_img.crop((x1, y1, x2, y2))
            if using_debug_mode: print("Screenshot taken!")
            self.root.after(1, lambda: self.callback(img))
        else:
            if using_debug_mode: print("Screenshot canceled!")
            self.root.after(1, lambda: self.cancel_callback())
        
        self.master.destroy()

def set_bg_transparent(toplevel: tk.Toplevel, invisible_color_Windows_OS_Only='#100101'):
    if platform.system() == "Windows":
        toplevel.attributes("-transparentcolor", invisible_color_Windows_OS_Only)
        toplevel.config(bg=invisible_color_Windows_OS_Only)
    elif platform.system() == "Darwin":
        toplevel.attributes("-transparent", True)
        toplevel.config(bg="systemTransparent")
    else:
        window_alpha_channel = 0.3
        toplevel.attributes('-alpha', window_alpha_channel)
        toplevel.lift()
        toplevel.attributes("-topmost", True)
        toplevel.attributes("-transparent", True)

def drag_screen_shot(root: tk.Tk, callback=None, cancel_callback=None, debug_logging=False):
    global using_debug_mode
    using_debug_mode = debug_logging
    # Take a screenshot before showing the overlay
    screenshot_img = ImageGrab.grab()
    top = tk.Toplevel(root)
    top.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
    top.overrideredirect(True)
    top.lift()
    top.attributes("-topmost", True)
    set_bg_transparent(top)
    DragScreenshotPanel(root, top, screenshot_img, callback, cancel_callback)

def ocr_callback(img):
    img.save("snip.png")
    text = pytesseract.image_to_string(img)
    print("--- OCR results for snip ---")
    print(text)
    print("\n")

def cancel_callback():
    print("Screenshot canceled.")

def snip_and_ocr():
    root.after(0, lambda: drag_screen_shot(root, callback=ocr_callback, cancel_callback=cancel_callback))

def keyboard_thread():
    print("Press Shift+S to snip and OCR. Press ESC to exit.")
    keyboard.add_hotkey('shift+s', snip_and_ocr)
    keyboard.wait('esc')
    # When ESC is pressed, quit the Tkinter mainloop
    root.after(0, root.quit)

# Create the root window once and keep it alive
root = tk.Tk()
root.withdraw()  # Hide the root window

# Start the keyboard listener in a background thread
threading.Thread(target=keyboard_thread, daemon=True).start()

# Start the Tkinter event loop (main thread)
root.mainloop()