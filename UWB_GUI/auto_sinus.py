import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import numpy as np
import threading
import time
import math

# --- Anchor setup ---
anchors = [
    [-16.5, 0], [-10.5, 0], [-4.5, 0], [1.5, 0], [7.5, 0], [13.5, 0],
    [-13.5, -3], [-7.5, -3], [-1.5, -3], [4.5, -3], [10.5, -3], [16.5, -3]
]

# --- Globals ---
star_pos = [0.0, 0.0]
fig, ax = None, None
star = None
star_label = None
circles = []
text_labels = []
corridor_line = None
corridor_text = None
received_label = None

# --- GUI Functions ---
def update_circles():
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

    distances = [np.linalg.norm(np.array(anchor) - np.array(star_pos)) for anchor in anchors]
    within_10m = [(i, d) for i, d in enumerate(distances) if d <= 10.0]
    closest_valid = sorted(within_10m, key=lambda x: x[1])[:3]

    count = len(closest_valid)
    if count == 3:
        circle_color = 'purple'
    elif count == 2:
        circle_color = 'yellow'
    elif count == 1:
        circle_color = 'red'
    else:
        circle_color = None

    for i, d in closest_valid:
        anchor = anchors[i]
        circle = patches.Circle(anchor, radius=d, fill=True, color=circle_color, alpha=0.3, linestyle='--')
        ax.add_patch(circle)
        circles.append(circle)

        label = ax.text(anchor[0] + 0.5, anchor[1] - 0.7, f"{d:.2f} m", color='black', fontsize=8)
        text_labels.append(label)

    star_label = ax.text(star_pos[0] + 0.5, star_pos[1] + 0.5,
                         f"({star_pos[0]:.2f}, {star_pos[1]:.2f})", color='red')

    y_ref_lines = [0, -3]
    closest_y = min(y_ref_lines, key=lambda y: abs(star_pos[1] - y))
    corridor_line = ax.plot([star_pos[0], star_pos[0]], [star_pos[1], closest_y], linestyle='--', color='red')[0]
    mid_y = (star_pos[1] + closest_y) / 2
    corridor_text = ax.text(star_pos[0] + 0.5, mid_y, f"{abs(star_pos[1] - closest_y):.2f} m", color='red', fontsize=9)

    fig.canvas.draw_idle()

# --- Depot drawing ---
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

# --- Server polling simulation (sine wave movement) ---
def poll_server():
    t = 0
    while True:
        try:
            x = 15 * math.sin(t)
            y = 10 * math.cos(t)
            star_pos[0] = x
            star_pos[1] = y
            star.set_data([x], [y])
            update_circles()
            received_label.config(text=f"Received Position: ({x:.2f}, {y:.2f})")
            t += 0.01
        except Exception as e:
            print("Simulation error:", e)
        time.sleep(0.01)

# --- GUI Setup ---
root = tk.Tk()
root.title("UWB Simulation - Pattern Movement")

frame = ttk.Frame(root)
frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
control_frame = ttk.Frame(root)
control_frame.pack(side=tk.RIGHT, fill=tk.Y)

fig, ax = plt.subplots(figsize=(10, 6))
ax.set_aspect('equal')
ax.set_xlim(-20, 20)
ax.set_ylim(-20, 20)
ax.grid(True)
ax.set_title("Anchor Layout")

# Draw depot
draw_depot(ax)

# Plot anchors and initial star
ax.scatter([a[0] for a in anchors], [a[1] for a in anchors], s=100, color='green')
star, = ax.plot(star_pos[0], star_pos[1], 'r*', markersize=12)

canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

received_label = ttk.Label(control_frame, text="Received Position: (?)")
received_label.pack(pady=5)

# Start polling thread
threading.Thread(target=poll_server, daemon=True).start()

root.mainloop()
