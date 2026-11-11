"""Small desktop uploader and crop tool for the local MINC material classifier."""
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
from minc_predict import load_model, predict

MAX_W, MAX_H = 850, 520
root = tk.Tk()
root.title("Fitwell — MINC Materials-23 classifier")
root.geometry("940x760")
status = tk.StringVar(value="Open a material photo or room photo, then drag a crop over a surface.")
tk.Label(root, text="MINC Materials-23", font=("Arial", 20, "bold")).pack(pady=10)
tk.Label(root, textvariable=status, wraplength=900).pack(pady=4)
toolbar = tk.Frame(root); toolbar.pack(pady=6)
canvas = tk.Canvas(root, width=MAX_W, height=MAX_H, bg="#e8ece9"); canvas.pack()
results = tk.Text(root, height=7, width=105); results.pack(pady=8)
state = {}


def display(image):
    state["image"] = image
    preview = image.copy(); preview.thumbnail((MAX_W, MAX_H))
    state["scale"] = preview.width / image.width
    state["preview"] = preview
    state["photo"] = ImageTk.PhotoImage(preview)
    canvas.config(width=preview.width, height=preview.height)
    canvas.delete("all"); canvas.create_image(0, 0, anchor="nw", image=state["photo"])
    status.set("Drag over a surface to classify that crop, or click Classify whole image.")


def choose():
    path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.webp"), ("All files", "*.*")])
    if path:
        try: display(ImageOps.exif_transpose(Image.open(path)).convert("RGB"))
        except Exception as error: messagebox.showerror("MINC", str(error))


def classify(image):
    button.config(state="disabled"); status.set("Classifying… CPU inference may take a moment.")
    def work():
        try:
            if "model" not in state: state["processor"], state["model"], state["device"] = load_model()
            predictions = predict(image, state["processor"], state["model"], state["device"])
            root.after(0, lambda: show_predictions(predictions))
        except Exception as error: root.after(0, lambda: messagebox.showerror("MINC", str(error)))
        finally: root.after(0, lambda: button.config(state="normal"))
    threading.Thread(target=work, daemon=True).start()


def show_predictions(predictions):
    results.delete("1.0", "end")
    results.insert("end", "Top material predictions\n\n" + "\n".join(f"{i}. {label}: {score:.2%}" for i, (label, score) in enumerate(predictions, 1)))
    status.set("Prediction complete. This model classifies the selected image/crop; it does not segment a whole room.")


def whole():
    if "image" in state: classify(state["image"])


def down(event): state["start"] = (event.x, event.y); canvas.delete("selection")
def move(event):
    if "start" in state: canvas.delete("selection"); x, y = state["start"]; canvas.create_rectangle(x, y, event.x, event.y, outline="red", width=2, tags="selection")
def up(event):
    if "start" not in state: return
    x1, y1 = state.pop("start"); x2, y2 = event.x, event.y
    left, right = sorted((x1, x2)); top, bottom = sorted((y1, y2))
    if right-left > 8 and bottom-top > 8:
        scale = state["scale"]; classify(state["image"].crop((int(left/scale), int(top/scale), int(right/scale), int(bottom/scale))))

tk.Button(toolbar, text="Open image", command=choose).pack(side="left", padx=5)
button = tk.Button(toolbar, text="Classify whole image", command=whole); button.pack(side="left", padx=5)
canvas.bind("<ButtonPress-1>", down); canvas.bind("<B1-Motion>", move); canvas.bind("<ButtonRelease-1>", up)
root.mainloop()
