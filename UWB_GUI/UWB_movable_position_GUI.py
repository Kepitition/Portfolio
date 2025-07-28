import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import numpy as np

# Fixed anchor positions
"""
anchors = [
    [-16.5, 0], [-10.5, 0], [-4.5, 0], [1.5, 0], [7.5, 0], [13.5, 0],
    [-13.5, -3], [-7.5, -3], [-1.5, -3], [4.5, -3], [10.5, -3], [16.5, -3]
]

"""

anchors = [
    [-15, 0], [-9, 0], [-3, 0], [3, 0], [9, 0], [15, 0],
    [-15, -3], [-9, -3], [-3, -3], [3, -3], [9, -3], [15, -3]
]

# --- Globals ---
star_pos = [0.0, 0.0]
circles = []
text_labels = []
star = None
star_label = None
selected_star = False
corridor_line = None
corridor_text = None


# --- Draw depot layout ---
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

# --- GUI Setup ---
root = tk.Tk()
root.title("Draggable Star - Closest Anchors Visualization")

frame = ttk.Frame(root)
frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

control_frame = ttk.Frame(root)
control_frame.pack(side=tk.RIGHT, fill=tk.Y)

fig, ax = plt.subplots(figsize=(12, 6))
ax.set_aspect('equal')
ax.set_xlim(-25, 25)
ax.set_ylim(-25, 10)
ax.grid(True)
ax.set_title("Anchor Layout with Draggable Star")

# Draw depot background
draw_depot(ax)

canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# --- Plot anchors ---
anchor_scatter = ax.scatter([a[0] for a in anchors], [a[1] for a in anchors], c='blue', s=100)
for i, (x, y) in enumerate(anchors):
    ax.text(x + 0.3, y + 0.3, f"A{i+1}", fontsize=9, color='blue')

# --- Initial Star ---
star = ax.plot([star_pos[0]], [star_pos[1]], 'r*', markersize=15)[0]
star_label = ax.text(star_pos[0] + 0.5, star_pos[1] + 0.5, f"({star_pos[0]:.2f}, {star_pos[1]:.2f})", color='black')

# --- Functions ---
def update_circles():
    global circles, text_labels, star_label, corridor_line, corridor_text

    # Clear old visuals
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

    # Step 1: Compute distances
    distances = [np.linalg.norm(np.array(anchor) - np.array(star_pos)) for anchor in anchors]

    # Step 2: Filter anchors within 10m
    within_10m = [(i, d) for i, d in enumerate(distances) if d <= 10]

    # Step 3: Sort by distance and take top 3
    closest_valid = sorted(within_10m, key=lambda x: x[1])[:3]

    # Step 4: Color by number of selected anchors
    count = len(closest_valid)
    if count == 3:
        circle_color = 'green'
    elif count == 2:
        circle_color = 'yellow'
    elif count == 1:
        circle_color = 'red'
    else:
        circle_color = None  # No circles if nothing is close enough

    # Step 5: Draw
    for i, d in closest_valid:
        anchor = anchors[i]
        circle = patches.Circle(anchor, radius=d, fill=True, color=circle_color, alpha=0.3, linestyle='--')
        ax.add_patch(circle)
        circles.append(circle)

        label = ax.text(anchor[0] + 0.5, anchor[1] - 0.7, f"{d:.2f} m", color='black', fontsize=8)
        text_labels.append(label)

    # Star label
    star_label = ax.text(star_pos[0] + 0.5, star_pos[1] + 0.5, f"({star_pos[0]:.2f}, {star_pos[1]:.2f})", color='red')

    # Corridor line (to y=0 or y=-3)
    y_ref_lines = [0, -3]
    closest_y = min(y_ref_lines, key=lambda y: abs(star_pos[1] - y))
    corridor_line = ax.plot([star_pos[0], star_pos[0]], [star_pos[1], closest_y], linestyle='--', color='red')[0]
    mid_y = (star_pos[1] + closest_y) / 2
    corridor_text = ax.text(star_pos[0] + 0.5, mid_y, f"{abs(star_pos[1] - closest_y):.2f} m", color='black', fontsize=12)

    fig.canvas.draw_idle()

def on_press(event):
    global selected_star
    if event.inaxes != ax or event.xdata is None or event.ydata is None:
        return
    dist = np.linalg.norm(np.array([event.xdata, event.ydata]) - np.array(star_pos))
    if dist < 0.7:
        selected_star = True

def on_release(event):
    global selected_star
    selected_star = False

def on_motion(event):
    if not selected_star or event.inaxes != ax or event.xdata is None or event.ydata is None:
        return
    star_pos[0] = event.xdata
    star_pos[1] = event.ydata
    star.set_data([star_pos[0]], [star_pos[1]])
    update_circles()

# --- Bind mouse events ---
fig.canvas.mpl_connect("button_press_event", on_press)
fig.canvas.mpl_connect("button_release_event", on_release)
fig.canvas.mpl_connect("motion_notify_event", on_motion)

# --- Initial update ---
update_circles()

root.mainloop()
