"""Upload/click interface for Zero-Shot Material similarity maps."""
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageOps
from zero_shot_predict import load_model, descriptor_map, similarity_map

MAX_W, MAX_H = 900, 540
root = tk.Tk(); root.title("Fitwell — Zero-Shot Material Similarity"); root.geometry("980x780")
status = tk.StringVar(value="Open a room photo, then click a surface.")
tk.Label(root, text="Zero-Shot Material Similarity", font=("Arial", 20, "bold")).pack(pady=10)
tk.Label(root, textvariable=status, wraplength=940).pack(pady=4)
bar = tk.Frame(root); bar.pack(pady=6)
canvas = tk.Canvas(root, width=MAX_W, height=MAX_H, bg="#e8ece9"); canvas.pack()
results = tk.Text(root, height=7, width=110); results.pack(pady=8)
state = {}


def show_image(bgr):
    state["bgr"] = bgr; rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    preview = Image.fromarray(rgb); preview.thumbnail((MAX_W, MAX_H))
    state["scale"] = preview.width / bgr.shape[1]; state["preview"] = preview
    state["photo"] = ImageTk.PhotoImage(preview)
    canvas.config(width=preview.width, height=preview.height); canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=state["photo"])
    status.set("Click a surface to create its similarity map. Bright areas are visually similar to the clicked point.")


def choose():
    path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.webp"), ("All files", "*.*")])
    if path:
        image = cv2.imread(path)
        if image is None: messagebox.showerror("Zero-Shot", "Could not read that image.")
        else: state["path"] = path; show_image(image)


def click(event):
    if "bgr" not in state or state.get("busy"): return
    scale = state["scale"]; x, y = int(event.x / scale), int(event.y / scale)
    if not (0 <= x < state["bgr"].shape[1] and 0 <= y < state["bgr"].shape[0]): return
    state["busy"] = True; status.set("Computing similarity map… CPU inference may take a while.")
    threading.Thread(target=work, args=(x, y), daemon=True).start()


def work(x, y):
    try:
        if "model" not in state: state["model"], state["device"] = load_model()
        fmap = descriptor_map(state["bgr"], state["model"])
        sim = similarity_map(fmap, x, y)
        root.after(0, lambda: display_result(sim, x, y))
    except Exception as error: root.after(0, lambda: messagebox.showerror("Zero-Shot", str(error)))
    finally: root.after(0, lambda: state.__setitem__("busy", False))


def display_result(sim, x, y):
    bgr = state["bgr"]; heat = (sim * 255).astype(np.uint8)
    heat = cv2.applyColorMap(heat, cv2.COLORMAP_JET); overlay = cv2.addWeighted(bgr, .45, heat, .55, 0)
    cv2.circle(overlay, (x, y), 8, (255, 255, 255), 2)
    show_image(overlay)
    results.delete("1.0", "end")
    results.insert("end", f"Selected point: x={x}, y={y}\nSimilarity map: bright regions are visually similar to the selected surface.\nDevice: {state['device']}\n\nMINC prediction is optional and separate: click the button below to classify a crop around this point.")
    state["point"] = (x, y); state["base"] = bgr
    status.set("Similarity map ready. The map is not a material name or confidence score.")


def minc():
    if "point" not in state: return
    try:
        from minc_predict import load_model as load_minc, predict
        x, y = state["point"]; image = state["base"]; r = 40
        crop = Image.fromarray(cv2.cvtColor(image[max(0,y-r):y+r, max(0,x-r):x+r], cv2.COLOR_BGR2RGB))
        if crop.width < 8 or crop.height < 8: raise ValueError("Selected point is too close to an image edge.")
        if "minc" not in state: state["minc"] = load_minc()
        predictions = predict(crop, *state["minc"])
        results.insert("end", "\n\nMINC crop classification (different model):\n" + "\n".join(f"{i}. {label}: {score:.2%}" for i,(label,score) in enumerate(predictions,1)))
    except Exception as error: messagebox.showerror("MINC", str(error))


tk.Button(bar, text="Open room photo", command=choose).pack(side="left", padx=5)
tk.Button(bar, text="Classify MINC crop around selected point", command=minc).pack(side="left", padx=5)
canvas.bind("<Button-1>", click)
root.mainloop()
