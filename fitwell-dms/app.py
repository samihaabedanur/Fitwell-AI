"""Local desktop image viewer; run with Python in VS Code."""
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk
from recognise import ROOT, NAMES, load_model, save_results

root = tk.Tk()
root.title('Fitwell — pretrained material recognition')
root.geometry('920x760')
status = tk.StringVar(value='Choose a room photo. First prediction can take longer on CPU.')
tk.Label(root, text='Fitwell Material Recognition', font=('Arial',20,'bold')).pack(pady=12)
tk.Label(root, textvariable=status, wraplength=860).pack(pady=6)
button = tk.Button(root,text='Choose room photo',command=lambda: choose(),font=('Arial',12))
button.pack(pady=8)
canvas = tk.Canvas(root, width=850, height=512, bg='#e8ece9')
canvas.pack()
results = tk.Text(root, height=7, width=100)
results.pack(pady=8)
state = {}

def show_result(value):
    image, mask, overlay, summary = value
    state['mask'] = mask
    state['photo'] = ImageTk.PhotoImage(overlay)
    canvas.delete('all')
    canvas.create_image(0,0,anchor='nw',image=state['photo'])
    results.delete('1.0','end')
    results.insert('end', '\n'.join(f"{r['material']}: {r['image_area_percent']}% of image" for r in summary))
    status.set('Click the coloured image to inspect a predicted material. Results saved in results/.')
    button.config(state='normal')

def failed(error):
    button.config(state='normal')
    status.set('Prediction failed.')
    messagebox.showerror('Fitwell', str(error))

def worker(path):
    try:
        if 'model' not in state:
            state['model'], state['device'] = load_model()
        value = save_results(path,state['model'],state['device'],ROOT/'results')
        root.after(0, lambda: show_result(value))
    except Exception as error:
        root.after(0, lambda error=error: failed(error))

def choose():
    path = filedialog.askopenfilename(filetypes=[('Images','*.jpg *.jpeg *.png *.webp'),('All files','*.*')])
    if path:
        button.config(state='disabled')
        status.set('Recognising materials… Please wait.')
        threading.Thread(target=worker,args=(path,),daemon=True).start()

def inspect(event):
    mask = state.get('mask')
    if mask is not None and 0 <= event.y < mask.shape[0] and 0 <= event.x < mask.shape[1]:
        status.set(f'Predicted material: {NAMES[int(mask[event.y,event.x])]} — visual estimate, not a verified product identification.')

canvas.bind('<Button-1>',inspect)
root.mainloop()
