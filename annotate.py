import cv2
import os
from tkinter import Tk, Label, Button, StringVar, Canvas
from tkinter import ttk
from PIL import Image, ImageTk

video_path = 'data/7.mp4'
labels_file_path = os.path.join(os.path.dirname(video_path), os.path.basename(video_path).replace('.mp4', '.txt'))

mapping = {
    '0': 'B1_CheckNameSheet', '1': 'B1_CheckLAConnector', '2': 'B2_AlignCable', '3': 'B2_CheckConnector',
    '4': 'B1_AlignCable', '5': 'B3_AlignCable', '6': 'B3_CheckConnector', '7': 'B4_AlignCable',
    '8': 'B4_CheckConnector', '9': 'B5_AlignCable', 'a': 'B5_CheckConnector', 'b': 'B6_AlignCable',
    'c': 'B6_CheckConnector', 'd': 'B7_AlignCable', 'e': 'B7_CheckConnector', 'f': 'B8_CheckProtector',
    'g': 'B8_CheckConnector', 'h': 'B8_CheckLAConnector', 'i': 'B8_AlignCable', 'j': 'B8_CheckConnector',
    'k': 'B9_AlignCable', 'l': 'B9_CheckConnector', 'm': 'B10_CheckFLBlock', 'n': 'B11_CheckFusebox',
    'o': 'B11_CheckFuseboxPower', 'p': 'B11_CheckFusebox', 'q': 'B12_CheckProtector', 'r': 'B12_CheckConnector',
    's': 'B13_CheckConnector', 't': 'B14_CheckConnector', 'u': 'B15_CheckProtector', 'v': 'B15_CheckConnector',
    'w': 'B16_CheckProtector', 'x': 'B16_CheckConnector', 'y': 'B16_CheckProtector', 'z': 'B17_CheckGrommet',
    'A': 'B17_CheckConnector', 'B': 'B18_CheckConnector', 'C': 'B17_CheckConnector', 'D': 'B19_AlignCable',
    'E': 'B19_CheckConnector', 'F': 'B20_CheckConnector', 'G': 'B21_CheckProtector', 'H': 'B21_CheckConnector',
    'I': 'B22_AlignCable', 'J': 'B22_CheckConnector', 'K': 'B23_CheckVinylSheet', 'L': 'B24_AlignCable',
    'M': 'B24_CheckConnector', 'N': 'B25_CheckLAConnector', 'O': 'B25_AlignCable', 'P': 'B25_CheckConnector',
    'Q': 'B26_AlignCable', 'R': 'B26_CheckConnector', 'S': 'B27_AlignCable', 'T': 'B27_CheckConnector',
    'Z': 'bg'
}
label_list = list(mapping.values())

cap = cv2.VideoCapture(video_path)
frame_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // 2
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) // 2

current_frame_index = 0
labels_dict = {}

def get_frame_at_index(index):
    cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    ret, frame = cap.read()
    if not ret:
        return None
    frame = cv2.resize(frame, (frame_width, frame_height))
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img)

def update_frame():
    img = get_frame_at_index(current_frame_index)
    if img is None:
        return
    imgtk = ImageTk.PhotoImage(image=img)
    canvas.imgtk = imgtk
    canvas.create_image(0, 0, anchor='nw', image=imgtk)

    if current_frame_index in labels_dict:
        label_var.set(labels_dict[current_frame_index])

    label_frame.config(text=f"Frame {current_frame_index + 1}/{frame_total}")

def next_frame(event=None):
    global current_frame_index
    labels_dict[current_frame_index] = label_var.get()
    if current_frame_index < frame_total - 1:
        current_frame_index += 1
        root.after(1, update_frame)

def prev_frame(event=None):
    global current_frame_index
    labels_dict[current_frame_index] = label_var.get()
    if current_frame_index > 0:
        current_frame_index -= 1
        root.after(1, update_frame)

def save_labels():
    with open(labels_file_path, 'w') as f:
        for frame_idx in sorted(labels_dict.keys()):
            f.write(f"{frame_idx}: {labels_dict[frame_idx]}\n")
    print("Labels saved to", labels_file_path)
    cap.release()
    root.destroy()

# Initialize GUI
root = Tk()
root.title("Video Labeler")

canvas = Canvas(root, width=frame_width, height=frame_height)
canvas.grid(row=0, column=0, columnspan=4)

label_var = StringVar(root)
label_var.set(label_list[0])

dropdown = ttk.Combobox(root, textvariable=label_var, values=label_list, state='readonly')
dropdown.grid(row=1, column=0)

Button(root, text="◀ Back", command=prev_frame).grid(row=1, column=1)
Button(root, text="Next ▶", command=next_frame).grid(row=1, column=2)
Button(root, text="💾 Save & Exit", command=save_labels).grid(row=1, column=3)

label_frame = Label(root, text="Frame 1")
label_frame.grid(row=2, column=0, columnspan=4)

update_frame()

root.bind('<Right>', next_frame)
root.bind('<Left>', prev_frame)
root.mainloop()
