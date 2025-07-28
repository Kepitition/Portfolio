import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import random

# --- Global state ---
# List of anchor coordinates. Each anchor is a list [x, y].
anchors = [[6, 7.5], [9, -3], [5, 7.5]]
# List of distances corresponding to each anchor.
distances = [7.0, 5.0, 8.0]
# Color palette for differentiating anchors on the plot.
colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown', 'cyan', 'magenta', 'gray', 'olive']
# List to hold matplotlib Text objects for anchor labels (A1, A2, etc.).
text_labels = []
# List to hold matplotlib Text objects for anchor coordinate displays.
coord_texts = []
# List to hold matplotlib Circle patch objects for distance circles.
circles = []
# List to hold Tkinter Label widgets displaying anchor coordinates in the UI.
anchor_coord_labels = []
# List to hold Tkinter Entry widgets for inputting distance values.
distance_entries = []
# Matplotlib plot object for the estimated position (red star).
star = None
# Matplotlib Text object for the label of the estimated position.
star_label = None
# Index of the currently selected anchor for dragging.
selected_index = None
# Matplotlib plot object for the dashed line indicating distance to a reference line.
dashed_line = None
# Matplotlib Text object for the label of the distance to a reference line.
distance_text = None

# --- Trilateration ---
def trilateration_3anchors(p1, d1, p2, d2, p3, d3):
    """
    Calculates the position of a point using trilateration with three anchors.

    Given the coordinates of three anchor points and the measured distances
    from an unknown point to each of these anchors, this function computes
    the (x, y) coordinates of the unknown point.

    Args:
        p1 (list): Coordinates of the first anchor point [x1, y1].
        d1 (float): Distance from the unknown point to the first anchor.
        p2 (list): Coordinates of the second anchor point [x2, y2].
        d2 (float): Distance from the unknown point to the second anchor.
        p3 (list): Coordinates of the third anchor point [x3, y3].
        d3 (float): Distance from the unknown point to the third anchor.

    Returns:
        tuple: A tuple containing the estimated (x, y) coordinates of the unknown point.

    Raises:
        ValueError: If the anchor points are collinear, which makes a unique
                    solution impossible (the denominator in the calculation becomes zero).
    """
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

def draw_depot(ax):
    """
    Draws a simplified depot layout (shelving and corridors) on the given matplotlib axes.

    This function adds rectangular patches to the plot to represent the
    physical structure of a depot, providing a visual context for the anchors
    and estimated position.

    Args:
        ax (matplotlib.axes.Axes): The axes object on which to draw the depot layout.
    """
    raf_w, raf_h = 3, 20
    koridor_w = 3
    num_blocks = 8
    total_width = num_blocks * raf_w + (num_blocks - 1) * koridor_w
    start_x = -total_width / 2
    for i in range(num_blocks):
        x = start_x + i * (raf_w + koridor_w)
        for y_off in [-3 - raf_h, 0, 3]:
            ax.add_patch(plt.Rectangle((x, y_off), raf_w, raf_h, color='gray', alpha=1.0))

# --- UI Functions ---
def update_position():
    """
    Updates the estimated position on the plot based on current anchor distances.

    Retrieves distance values from the Tkinter entry widgets, selects the three
    closest anchors, performs trilateration, and updates the star marker, its label,
    and a dashed line indicating distance to a reference line on the plot.
    It also updates the result label in the GUI.
    """
    global star, dashed_line, distance_text, star_label
    if len(anchors) < 3:
        result_label.config(text="Need at least 3 anchors")
        return
    try:
        # Update distances from entry values
        for i, entry in enumerate(distance_entries):
            distances[i] = float(entry.get())

        # pick closest 3 distances
        # Sorts indices based on distance values to pick the three closest anchors.
        d_index = sorted(range(len(distances)), key=lambda i: distances[i])[:3]
        p1, d1 = anchors[d_index[0]], distances[d_index[0]]
        p2, d2 = anchors[d_index[1]], distances[d_index[1]]
        p3, d3 = anchors[d_index[2]], distances[d_index[2]]
        pos = trilateration_3anchors(p1, d1, p2, d2, p3, d3)

        # Remove previous estimated position marker and label
        if star:
            star.remove()
        if 'star_label' in globals() and star_label:
            star_label.remove()

        # Plot new estimated position
        star = ax.plot(pos[0], pos[1], 'r*', markersize=12)[0]

        # Update GUI result label
        result_label.config(text=f"Estimated Position: ({pos[0]:.2f}, {pos[1]:.2f})")

        # Remove old dashed line and label
        if dashed_line:
            dashed_line.remove()
        if distance_text:
            distance_text.remove()

        # Find closest reference line (x = 0 or x = -3) for visual context
        y_star = pos[1]
        ref_lines = [0, -3]
        closest_y = min(ref_lines, key=lambda y: abs(y_star - y))
        distance_to_line = abs(y_star - closest_y)

        # Draw new dashed line and label for distance to reference line
        dashed_line = ax.plot([pos[0], pos[0]], [y_star, closest_y], linestyle='--', color='red')[0]
        mid_y = (y_star + closest_y) / 2
        distance_text = ax.text(pos[0] + 0.3, mid_y, f"{distance_to_line:.2f} m", color="black", fontsize=9)
        # Add label for the estimated position coordinates
        star_label = ax.text(pos[0] + 0.4, pos[1] + 0.4, f"({pos[0]:.2f}, {pos[1]:.2f})", color="red", fontsize=9)

        # Redraw the canvas to reflect changes
        fig.canvas.draw_idle()

    except Exception as e:
        # Display any errors encountered during trilateration or distance parsing
        result_label.config(text=str(e))


def redraw_anchors():
    """
    Redraws all anchors, their labels, distance circles, and associated UI elements.

    This function clears existing anchor-related graphical elements and Tkinter widgets,
    then recreates them based on the current `anchors` and `distances` global lists.
    It's called when anchors are added, removed, or dragged.
    """
    global sc # scatter plot object for anchors
    # Remove all existing text labels, coordinate displays, and circles from the plot
    for t in text_labels: t.remove()
    for c in coord_texts: c.remove()
    for circle in circles: circle.remove()
    text_labels.clear()
    coord_texts.clear()
    circles.clear()
    # Destroy and clear Tkinter labels and entry widgets for anchors
    for lbl in anchor_coord_labels: lbl.destroy()
    anchor_coord_labels.clear()
    for entry in distance_entries: entry.destroy()
    distance_entries.clear()

    # Iterate through current anchors to redraw them
    for i, (a, d) in enumerate(zip(anchors, distances)):
        color = colors[i % len(colors)] # Cycle through predefined colors
        # Create and pack Tkinter label for anchor coordinates
        lbl = ttk.Label(control_frame, text=f"A{i+1} Pos: ({a[0]:.2f}, {a[1]:.2f})")
        lbl.pack()
        anchor_coord_labels.append(lbl)

        # Create and pack Tkinter entry for anchor distance
        entry = ttk.Entry(control_frame, width=10)
        entry.insert(0, str(d))
        entry.pack()
        # Bind KeyRelease event to update position automatically when distance changes
        entry.bind("<KeyRelease>", lambda e: update_position())
        distance_entries.append(entry)

        # Add anchor label (e.g., "A1") to the matplotlib plot
        text = ax.text(a[0] + 0.3, a[1] + 0.3, f"A{i+1}", color=color, fontsize=9)
        # Add anchor coordinates label to the matplotlib plot
        coord = ax.text(a[0] + 0.3, a[1] - 0.7, f"({a[0]:.2f}, {a[1]:.2f})", color=color, fontsize=8)
        # Add a circular patch representing the distance from the anchor
        circle = patches.Circle(a, radius=d, fill=True, linestyle='--', color=color, alpha=0.1)
        ax.add_patch(circle)

        # Store references to matplotlib objects for later removal
        text_labels.append(text)
        coord_texts.append(coord)
        circles.append(circle)

    # Update the scatter plot of anchor points
    sc.remove() # Remove old scatter plot
    sc = ax.scatter([a[0] for a in anchors], [a[1] for a in anchors], s=100, c=[colors[i % len(colors)] for i in range(len(anchors))])
    # Redraw the matplotlib canvas
    fig.canvas.draw_idle()


def add_anchor():
    """
    Adds a new anchor at a random position to the simulation.

    A new anchor is appended to the `anchors` list with random x, y coordinates
    and a default distance. The UI and plot are then redrawn.
    Prevents adding more than 10 anchors.
    """
    if len(anchors) >= 10:
        result_label.config(text="Max 10 anchors allowed")
        return
    x = random.uniform(-10, 10)
    y = random.uniform(-10, 10)
    anchors.append([x, y])
    distances.append(5.0) # Default distance for new anchor
    redraw_anchors() # Update plot and UI


def remove_anchor():
    """
    Removes the last anchor from the simulation.

    The last anchor and its corresponding distance are removed from their
    respective lists. The UI and plot are then redrawn.
    Prevents removing anchors if there are fewer than 3 remaining, as trilateration
    requires at least three.
    """
    if len(anchors) <= 3:
        result_label.config(text="Need minimum 3 anchors")
        return
    anchors.pop() # Remove last anchor coordinates
    distances.pop() # Remove last anchor distance
    redraw_anchors() # Update plot and UI


def on_press(event):
    """
    Event handler for mouse button press on the matplotlib canvas.

    If an anchor is clicked, its index is stored in `selected_index`
    to enable dragging.
    """
    global selected_index
    if event.inaxes != ax: # Check if click was within plot axes
        return
    selected_index = None # Reset selected index
    for i, a in enumerate(anchors):
        # Check if the click is within a small radius of an anchor point
        if ((event.xdata - a[0])**2 + (event.ydata - a[1])**2)**0.5 < 0.5:
            selected_index = i
            break # Found a selected anchor, exit loop


def on_release(event):
    """
    Event handler for mouse button release on the matplotlib canvas.

    Resets `selected_index` to None, indicating no anchor is currently being dragged.
    """
    global selected_index
    selected_index = None # Deselect the anchor


def on_motion(event):
    """
    Event handler for mouse motion on the matplotlib canvas.

    If an anchor is currently selected (`selected_index` is not None) and the
    mouse is moved within the plot axes, the selected anchor's position is
    updated to the new mouse coordinates, and the plot is redrawn.
    """
    global selected_index
    if selected_index is None or event.inaxes != ax:
        return
    # Update the coordinates of the selected anchor to the current mouse position
    anchors[selected_index][0] = event.xdata
    anchors[selected_index][1] = event.ydata
    redraw_anchors() # Update the plot to show the new anchor position
    update_position() # Recalculate and update the estimated position

# --- Plot Setup ---
# Initialize the main Tkinter window
root = tk.Tk()
root.title("Anchor Manager GUI")

# Create main frame for matplotlib canvas
frame = ttk.Frame(root)
frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create control frame for buttons and labels
control_frame = ttk.Frame(root)
control_frame.pack(side=tk.RIGHT, fill=tk.Y)

# Setup matplotlib figure and axes
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_aspect('equal') # Ensure equal scaling on x and y axes
ax.set_xlim(-20, 20)   # Set x-axis limits
ax.set_ylim(-20, 20)   # Set y-axis limits
ax.grid(True)          # Display grid
ax.set_title("Anchor Layout") # Set plot title

# Draw the depot layout on the axes
draw_depot(ax)
# Initial scatter plot of anchors
sc = ax.scatter([a[0] for a in anchors], [a[1] for a in anchors], s=100, c=colors[:len(anchors)])

# Tkinter Label to display estimated position
result_label = ttk.Label(control_frame, text="Estimated Position: (?)")
result_label.pack()

# Tkinter Buttons for adding, removing anchors, and finding position
ttk.Button(control_frame, text="Add Anchor", command=add_anchor).pack(pady=2)
ttk.Button(control_frame, text="Remove Anchor", command=remove_anchor).pack(pady=2)
ttk.Button(control_frame, text="Find Position", command=update_position).pack(pady=2)

# Integrate matplotlib figure into Tkinter window
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Connect mouse events to matplotlib canvas for interactive dragging
fig.canvas.mpl_connect("button_press_event", on_press)
fig.canvas.mpl_connect("button_release_event", on_release)
fig.canvas.mpl_connect("motion_notify_event", on_motion)

# Initial drawing of anchors and update of position
redraw_anchors()
update_position() # Call once at start to display initial position

# Start the Tkinter event loop
root.mainloop()