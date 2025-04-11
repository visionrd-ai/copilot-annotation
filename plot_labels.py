import cv2
import os

# Paths
video_path = "/home/multi-gpu/amur/production/data/all_videos/3.mp4"
label_path = "/home/multi-gpu/amur/production/data/all_videos/3.txt"
output_video_path = "3_plotted.mp4"

# Read labels from file
frame_labels = {}
with open(label_path, 'r') as f:
    for line in f:
        frame_num, label = line.strip().split(": ")
        frame_labels[int(frame_num)] = label

# Open the video
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise IOError("Cannot open video file")

# Video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Output video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

frame_idx = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    label = frame_labels.get(frame_idx, "")
    if label:
        cv2.putText(
            frame, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
            1, (0, 255, 0), 2, cv2.LINE_AA
        )

    out.write(frame)
    frame_idx += 1

cap.release()
out.release()
print(f"Labeled video saved to {output_video_path}")
