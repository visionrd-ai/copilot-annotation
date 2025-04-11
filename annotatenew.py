import os
import cv2
from tkinter import Tk, Toplevel, Label, Button, StringVar, Canvas, filedialog
from tkinter import ttk
from PIL import Image, ImageTk

# Label mapping
mapping = {
    '0': 'B1_CheckNameSheet', '1': 'B1_CheckLAConnector', '2': 'B2_AlignCable',
    '3': 'B2_CheckConnector', '4': 'B1_AlignCable', '5': 'B3_AlignCable',
    '6': 'B3_CheckConnector', '7': 'B4_AlignCable', '8': 'B4_CheckConnector',
    '9': 'B5_AlignCable', 'a': 'B5_CheckConnector', 'b': 'B6_AlignCable',
    'c': 'B6_CheckConnector', 'd': 'B7_AlignCable', 'e': 'B7_CheckConnector',
    'f': 'B8_CheckProtector', 'g': 'B8_CheckConnector', 'h': 'B8_CheckLAConnector',
    'i': 'B8_AlignCable', 'k': 'B9_AlignCable', 'l': 'B9_CheckConnector',
    'm': 'B10_CheckFLBlock', 'n': 'B11_CheckFusebox', 'o': 'B11_CheckFuseboxPower',
    'q': 'B12_CheckProtector', 'r': 'B12_CheckConnector', 's': 'B13_CheckGrommet',
    't': 'B13_CheckConnector', 'u': 'B14_CheckConnector', 'v': 'B15_CheckProtector',
    'w': 'B15_CheckConnector', 'x': 'B16_CheckGrommet', 'y': 'B16_CheckConnector',
    'z': 'B17_CheckConnector', 'A': 'B18_CheckConnector', 'B': 'B19_CheckConnector',
    'C': 'B20_CheckConnector', 'D': 'B21_CheckVinylSheet', 'E': 'B22_AlignCable',
    'F': 'B22_CheckConnector', '$': 'B22_CheckLAConnector', 'G': 'B23_AlignCable',
    'H': 'B23_CheckConnector', 'I': 'B24_AlignCable', 'J': 'B24_CheckConnector',
    'K': 'B25_AlignCable', 'L': 'B25_CheckConnector', 'Z': 'bg'
}
label_list = list(mapping.values())

# Global vars
labels_dict = {}
current_frame_index = 0
cap = None
frame_total = 0
frame_width = 0
frame_height = 0

# ---------- Labeling GUI ----------
def start_labeling(video_path):
    global cap, frame_total, frame_width, frame_height, current_frame_index, labels_dict

    cap = cv2.VideoCapture(video_path)
    frame_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // 2
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) // 2
    current_frame_index = 0
    labels_dict = {}

    labeler = Toplevel(root)
    labeler.title("Label Video")

    canvas = Canvas(labeler, width=frame_width, height=frame_height)
    canvas.grid(row=0, column=0, columnspan=4)

    label_var = StringVar(labeler)
    label_var.set(label_list[0])

    def get_frame(index):
        cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = cap.read()
        if not ret: return None
        frame = cv2.resize(frame, (frame_width, frame_height))
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img)

    def update_frame():
        img = get_frame(current_frame_index)
        if img is None: return
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
            update_frame()

    def prev_frame(event=None):
        global current_frame_index
        labels_dict[current_frame_index] = label_var.get()
        if current_frame_index > 0:
            current_frame_index -= 1
            update_frame()

    def save_and_exit():
        label_path = video_path.replace('.mp4', '.txt')
        with open(label_path, 'w') as f:
            for frame_idx in sorted(labels_dict.keys()):
                f.write(f"{frame_idx}: {labels_dict[frame_idx]}\n")
        cap.release()
        labeler.destroy()
        print("Labels saved to", label_path)

    dropdown = ttk.Combobox(labeler, textvariable=label_var, values=label_list, state='readonly')
    dropdown.grid(row=1, column=0)

    Button(labeler, text="◀ Back", command=prev_frame).grid(row=1, column=1)
    Button(labeler, text="Next ▶", command=next_frame).grid(row=1, column=2)
    Button(labeler, text="💾 Save & Exit", command=save_and_exit).grid(row=1, column=3)

    label_frame = Label(labeler, text="Frame 1")
    label_frame.grid(row=2, column=0, columnspan=4)

    update_frame()
    labeler.bind('<Right>', next_frame)
    labeler.bind('<Left>', prev_frame)

# ---------- Plotting ----------
def start_plotting(video_path, label_path):
    output_path = os.path.basename(video_path).replace('.mp4', '_plotted.mp4')
    output_video_path = os.path.join(os.path.dirname(video_path), output_path)

    frame_labels = {}
    with open(label_path, 'r') as f:
        for line in f:
            frame_num, label = line.strip().split(": ")
            frame_labels[int(frame_num)] = label

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened(): raise IOError("Cannot open video file")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        label = frame_labels.get(frame_idx, "")
        if label:
            cv2.putText(frame, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()
    print(f"Labeled video saved to {output_video_path}")

# ---------- Main Menu ----------
def choose_labeling():
    video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
    if video_path:
        start_labeling(video_path)

def choose_plotting():
    video_path = filedialog.askopenfilename(title="Select Video", filetypes=[("MP4 files", "*.mp4")])
    if not video_path: return
    label_path = filedialog.askopenfilename(title="Select Label File", filetypes=[("Text files", "*.txt")])
    if label_path:
        start_plotting(video_path, label_path)

# ---------- Root GUI ----------
root = Tk()
root.title("Video Annotation Tool")

Label(root, text="Choose an action:").pack(pady=10)

Button(root, text="🎬 Label a Video", command=choose_labeling, width=30).pack(pady=5)
Button(root, text="📹 Plot Labeled Video", command=choose_plotting, width=30).pack(pady=5)

root.mainloop()