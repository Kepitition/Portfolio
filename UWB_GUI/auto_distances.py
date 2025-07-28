import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import numpy as np
import threading
import requests
import time

# --- Anchor Setup ---
anchors = [
    [-16.5, 0], [-10.5, 0], [-4.5, 0], [1.5, 0], [7.5, 0], [13.5, 0],
    [-13.5, -3], [-7.5, -3], [-1.5, -3], [4.5, -3], [10.5, -3], [16.5, -3]
]

# --- Globals ---
fig, ax = None, None
star = None
star_label = None
circles = []
text_labels = []
corridor_line = None
corridor_text = None
received_label = None
star_pos = [0.0, 0.0]

# --- Trilateration Function ---
def trilateration_3anchors(p1, d1, p2, d2, p3, d3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    A = 2 * (x2 - x1)
    B = 2 * (y2 - y1)
    C = d1**2 - d2**2 - x1**2 + x2**2 - y1**2 + y2**2
    D = 2 * (x3 - x1)
    E = 2 * (y3 - y1)
    F = d1**2 - d3**2 - x1**2 + x3**2 - y1**2 + y3**2
    denominator = A * E - B * D
    if denominator == 0:
        raise ValueError("Anchors are aligned")
    x = (C * E - B * F) / denominator
    y = (A * F - C * D) / denominator
    return x, y

# --- GUI Functions ---
def update_plot(est_pos, used_indices, used_distances):
    global circles, text_labels, star_label, corridor_line, corridor_text

    for c in circles:
        c.remove()
    for t in text_labels:
        t.remove()
    if star_label:
        star_label.remove()
    if corridor_line:
        corridor_line.remove()
    if corridor_text:
        corridor_text.remove()

    circles.clear()
    text_labels.clear()

    colors = ['red', 'yellow', 'purple']
    for i, (idx, d) in enumerate(zip(used_indices, used_distances)):
        anchor = anchors[idx]
        circle = patches.Circle(anchor, radius=d, fill=True, color=colors[i], alpha=0.3, linestyle='--')
        ax.add_patch(circle)
        circles.append(circle)

        label = ax.text(anchor[0] + 0.5, anchor[1] - 0.7, f"{d:.2f} m", color='black', fontsize=8)
        text_labels.append(label)

    star.set_data([est_pos[0]], [est_pos[1]])
    star_label = ax.text(est_pos[0] + 0.5, est_pos[1] + 0.5, f"({est_pos[0]:.2f}, {est_pos[1]:.2f})", color='red')

    y_ref_lines = [0, -3]
    closest_y = min(y_ref_lines, key=lambda y: abs(est_pos[1] - y))
    corridor_line = ax.plot([est_pos[0], est_pos[0]], [est_pos[1], closest_y], linestyle='--', color='red')[0]
    mid_y = (est_pos[1] + closest_y) / 2
    corridor_text = ax.text(est_pos[0] + 0.5, mid_y, f"{abs(est_pos[1] - closest_y):.2f} m", color='red', fontsize=9)

    fig.canvas.draw_idle()

# --- Depot Drawing ---
def draw_depot(ax):
    raf_w, raf_h = 3, 20
    koridor_w = 3
    num_blocks = 8
    total_width = num_blocks * raf_w + (num_blocks - 1) * koridor_w
    start_x = -total_width / 2
    for i in range(num_blocks):
        x = start_x + i * (raf_w + koridor_w)
        for y_off in [-3 - raf_h, 0, 3]:
            ax.add_patch(plt.Rectangle((x, y_off), raf_w, raf_h, color='gray', alpha=1.0))

# --- Server Polling (DISTANCE DATA) ---
def poll_distances():
    while True:
        try:
            # Flask sunucudan veri çek
            response = requests.get("http://172.20.10.2:5000/get")  # Flask sunucu IP'si buraya
            if response.status_code == 200:
                data = response.json()
                distance_data = data.get("distances", [])

                if len(distance_data) != 3:
                    raise ValueError("Beklenen 3 mesafe verisi yok")

                used_ids = [item['anchor_id'] for item in distance_data]
                used_distances = [item['distance'] for item in distance_data]

                p1, d1 = anchors[used_ids[0]], used_distances[0]
                p2, d2 = anchors[used_ids[1]], used_distances[1]
                p3, d3 = anchors[used_ids[2]], used_distances[2]

                est_pos = trilateration_3anchors(p1, d1, p2, d2, p3, d3)
                update_plot(est_pos, used_ids, used_distances)

                received_label.config(
                    text=f"Distances: {used_distances[0]:.2f}, {used_distances[1]:.2f}, {used_distances[2]:.2f}"
                )
            else:
                print(f"Sunucu hatası: {response.status_code}")

        except Exception as e:
            print("Veri alma hatası:", e)
        time.sleep(0.5)

# --- GUI Setup ---
root = tk.Tk()
root.title("UWB Simulation - Distance to Anchors")

frame = ttk.Frame(root)
frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
control_frame = ttk.Frame(root)
control_frame.pack(side=tk.RIGHT, fill=tk.Y)

fig, ax = plt.subplots(figsize=(20, 12))
ax.set_aspect('equal')
ax.set_xlim(-20, 20)
ax.set_ylim(-20, 20)
ax.grid(True)
ax.set_title("Anchor Layout")

draw_depot(ax)

ax.scatter([a[0] for a in anchors], [a[1] for a in anchors], s=100, color='green')
star, = ax.plot(star_pos[0], star_pos[1], 'r*', markersize=12)

canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

received_label = ttk.Label(control_frame, text="Distances: (?)")
received_label.pack(pady=5)

threading.Thread(target=poll_distances, daemon=True).start()

root.mainloop()
