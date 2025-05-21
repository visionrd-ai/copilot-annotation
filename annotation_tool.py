import os
import cv2
from tkinter import Tk, Toplevel, Label, Button, StringVar, Canvas, filedialog
from tkinter import ttk
from PIL import Image, ImageTk

# Label mapping
mapping = [
    "bg", "collect_item", "install_rod", "unscrew_ib_1", "unscrew_ib_2",
    "unscrew_ib_3", "unscrew_ib_4", "remove_ib", "install_bd_1", "install_bd_2",
    "install_hi_sheet", "install_cp_1", "install_cp_2", "collect_EM", "collect_harness",
    "install_hi_clip_1", "install_hi_clip_2", "install_hi_clip_3", "install_hi_clip_4",
    "mark_EM_bolt_1", "mark_EM_bolt_2", "mark_EM_bolt_3", "install_EM_bolt_1",
    "install_EM_bolt_2", "install_EM_bolt_3", "drill_EM_bolt_1", "drill_EM_bolt_2",
    "drill_EM_bolt_3", "torque_EM_bolt_1", "torque_EM_bolt_2", "torque_EM_bolt_3",
    "drill_DM_bolt_1", "drill_DM_bolt_2", "drill_DM_bolt_3", "drill_DM_bolt_4",
    "drill_DM_bolt_5", "drill_DM_bolt_6", "drill_DB", "drill_LT", "unwrap_harness",
    "install_fusebox", "clip_wh_1", "clip_wh_2", "clip_wh_3", "clip_wh_4", "clip_wh_5",
    "clip_wh_6", "clip_wh_7", "clip_wh_8", "clip_wh_9", "clip_wh_10", "clip_wh_11",
    "clip_wh_12", "clip_wh_13", "clip_wh_14", "install_fusebox_bolt", "marker_check",
    "torque_check"
]
label_list = list(mapping)

# Global vars
labels_dict = {}
current_frame_index = 0
cap = None
frame_total = 0
frame_width = 0
frame_height = 0

# ---------- Labeling GUI ----------
def start_labeling(video_path):
    global cap, frame_total, frame_width, frame_height, current_frame_index, labels_dict, label_list

    cap = cv2.VideoCapture(video_path)
    frame_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = 1080#int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = 720#int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    current_frame_index = 0
    labels_dict = {}

    labeler = Toplevel(root)
    labeler.title("Label Video")

    canvas = Canvas(labeler, width=frame_width, height=frame_height)
    canvas.grid(row=0, column=0, columnspan=5)

    label_var = StringVar(labeler)
    label_var.set(label_list[0] if label_list else "")

    new_label_var = StringVar(labeler)
    jump_var = StringVar(labeler)

    def add_new_label():
        new_label = new_label_var.get().strip()
        if new_label and new_label not in label_list:
            label_list.append(new_label)
            dropdown['values'] = label_list
            label_var.set(new_label)
            new_label_var.set("")

    def get_frame(index):
        cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = cap.read()
        if not ret:
            return None
        frame = cv2.resize(frame, (frame_width, frame_height))
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(frame, (1080, 720))
        return Image.fromarray(img)

    def update_frame():
        img = get_frame(current_frame_index)
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
            update_frame()

    def prev_frame(event=None):
        global current_frame_index
        labels_dict[current_frame_index] = label_var.get()
        if current_frame_index > 0:
            current_frame_index -= 1
            update_frame()

    def jump_to_frame():
        global current_frame_index
        try:
            new_index = int(jump_var.get())
            if 0 <= new_index < frame_total:
                labels_dict[current_frame_index] = label_var.get()
                current_frame_index = new_index
                update_frame()
        except ValueError:
            pass  # Ignore invalid input

    def save_and_exit():
        label_path = video_path.replace('.avi', '.txt')
        with open(label_path, 'w') as f:
            for frame_idx in sorted(labels_dict.keys()):
                f.write(f"{frame_idx}: {labels_dict[frame_idx]}\n")

        mapping_path = video_path.replace('.avi', '_mapping.txt')
        with open(mapping_path, 'w') as f:
            for label in label_list:
                f.write(f"{label}\n")

        cap.release()
        labeler.destroy()
        print("Labels saved to", label_path)
        print("Updated mapping saved to", mapping_path)

    dropdown = ttk.Combobox(labeler, textvariable=label_var, values=label_list, state='readonly', width=20)
    dropdown.grid(row=1, column=0)

    Button(labeler, text="◀ Back", command=prev_frame, width=8).grid(row=1, column=1)
    Button(labeler, text="Next ▶", command=next_frame, width=8).grid(row=1, column=2)
    Button(labeler, text="💾 Save & Exit", command=save_and_exit).grid(row=1, column=3)

    label_frame = Label(labeler, text="Frame 1")
    label_frame.grid(row=2, column=0, columnspan=5)

    # Add label section
    Label(labeler, text="New Label:").grid(row=3, column=0)
    ttk.Entry(labeler, textvariable=new_label_var, width=20).grid(row=3, column=1)
    Button(labeler, text="➕ Add", command=add_new_label).grid(row=3, column=2)

    # Jump to frame section
    Label(labeler, text="Jump to frame:").grid(row=4, column=0)
    ttk.Entry(labeler, textvariable=jump_var, width=10).grid(row=4, column=1)
    Button(labeler, text="🚀 Jump", command=jump_to_frame).grid(row=4, column=2)

    update_frame()
    labeler.bind('<Right>', next_frame)
    labeler.bind('<Left>', prev_frame)

# ---------- Plotting ----------
def start_plotting(video_path, label_path):
    output_path = os.path.basename(video_path).replace('.avi', '_plotted.avi')
    output_video_path = os.path.join(os.path.dirname(video_path), output_path)

    frame_labels = {}
    with open(label_path, 'r') as f:
        for line in f:
            frame_num, label = line.strip().split(": ")
            frame_labels[int(frame_num)] = label

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError("Cannot open video file")

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
    video_path = filedialog.askopenfilename(filetypes=[("avi files", "*.avi")])
    if video_path:
        start_labeling(video_path)

def choose_plotting():
    video_path = filedialog.askopenfilename(title="Select Video", filetypes=[("avi files", "*.avi")])
    if not video_path:
        return
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
