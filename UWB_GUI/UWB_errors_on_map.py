import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import random

# Output directory
SAVE_FOLDER = "errors_on_map"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Settings
ANCHORS = [np.array([-4.5, 0]), np.array([-1.5, -3]), np.array([1.5, 0])]
NOISE_LEVELS = [0, 1, 2, 3, 4, 5]
TRIALS_PER_SETTING = 3

# Trilateration Function
def trilateration(p1, d1, p2, d2, p3, d3):
    """
    Calculates the position of a point using trilateration.

    Given three anchor points and the distances to them from an unknown point,
    this function determines the coordinates of the unknown point.

    Args:
        p1 (np.ndarray): Coordinates of the first anchor point [x1, y1].
        d1 (float): Distance from the unknown point to the first anchor.
        p2 (np.ndarray): Coordinates of the second anchor point [x2, y2].
        d2 (float): Distance from the unknown point to the second anchor.
        p3 (np.ndarray): Coordinates of the third anchor point [x3, y3].
        d3 (float): Distance from the unknown point to the third anchor.

    Returns:
        np.ndarray: The estimated coordinates of the unknown point [x, y].

    Raises:
        ValueError: If the anchor points are collinear, which makes a unique
                    solution impossible (denominator becomes zero).
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
    return np.array([x, y])

# Depot Layout Drawing
def draw_depot(ax):
    """
    Draws a simplified depot layout on the given matplotlib axes.

    The layout consists of multiple rectangular "raf" (shelving) blocks
    arranged with "koridor" (corridor) spaces in between.

    Args:
        ax (matplotlib.axes.Axes): The axes object on which to draw the depot.
    """
    raf_w, raf_h = 3, 20
    koridor_w = 3
    num_blocks = 8
    total_width = num_blocks * raf_w + (num_blocks - 1) * koridor_w
    start_x = -total_width / 2
    for i in range(num_blocks):
        x = start_x + i * (raf_w + koridor_w)
        for y_off in [-3 - raf_h, 0, 3]:
            ax.add_patch(plt.Rectangle((x, y_off), raf_w, raf_h, color='gray'))

# Simulation & Plotting
def simulate_and_plot(case, noise_level, trial_index, TRUE_POS):
    """
    Simulates a trilateration scenario with specified noise conditions and plots the results.

    This function generates true and noisy distance measurements from a true position
    to predefined anchor points, performs trilateration to estimate the position,
    and then plots the true position, estimated position, anchor points, and
    corresponding distance circles. The resulting plot is saved as a PNG image.

    Args:
        case (int): The noise application case (1, 2, or 3).
                    Case 1: Noise applied to one random anchor.
                    Case 2: Noise applied to two random anchors.
                    Case 3: Noise applied to all three anchors.
        noise_level (float): The maximum level of uniform noise to apply to distances.
        trial_index (int): The current trial number for the given case and noise level.
        TRUE_POS (np.ndarray): The actual (true) coordinates of the point being located [x, y].
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.set_xlim(-20, 20)
    ax.set_ylim(-20, 20)
    ax.set_title(f"Case {case}, Noise {noise_level:.1f}m, Trial {trial_index}")
    draw_depot(ax)

    true_distances = [np.linalg.norm(TRUE_POS - a) for a in ANCHORS]
    """
        for i in range(len(true_distances)):
        if  true_distances[i] > 10:
            true_distances[i] = 10
    """

    noisy = true_distances.copy()

    if case == 1:

        i = random.choice([0, 1, 2])
        noisy[i] += random.uniform(0, noise_level)
    elif case == 2:

        for i in random.sample([0, 1, 2], 2):
            noisy[i] += random.uniform(0, noise_level)
    elif case == 3:
        noisy = [d + random.uniform(0, noise_level) for d in true_distances]

    try:
        est_pos = trilateration(ANCHORS[0], noisy[0],
                                ANCHORS[1], noisy[1],
                                ANCHORS[2], noisy[2])

        colors = ['blue', 'green', 'red']
        for i, (a, true_d, noisy_d) in enumerate(zip(ANCHORS, true_distances, noisy)):
            ax.scatter(*a, c=colors[i], s=100)

            ax.text(a[0] + 0.5, a[1] + 1.2,
                    f"A{i+1}\nTrue: {true_d:.2f} m\nNoisy: {noisy_d:.2f} m\nΔ: {noisy_d - true_d:+.2f}",
                    fontsize=9, color=colors[i])

            # Noisy circle (filled)
            noisy_circle = patches.Circle(a, radius=noisy_d, fill=True, alpha=0.1, color=colors[i])
            ax.add_patch(noisy_circle)

            # True distance circle (dashed)
            true_circle = patches.Circle(a, radius=true_d, fill=False, linestyle='--', linewidth=1.2, color=colors[i])
            ax.add_patch(true_circle)

        # Positions
        ax.scatter(*TRUE_POS, c='yellow', marker='o', s=100, label="True Pos")
        ax.scatter(*est_pos, c='red', marker='*', s=150, label="Estimated Pos")

        # Error Line
        ax.plot([TRUE_POS[0], est_pos[0]], [TRUE_POS[1], est_pos[1]], 'r--')
        mid = (TRUE_POS + est_pos) / 2
        ax.text(mid[0], mid[1], f"{np.linalg.norm(est_pos - TRUE_POS):.2f} m", fontsize=10, color='black')

        ax.legend()
        fig.tight_layout()

        # Save figure
        fname = f"case{case}_noise{noise_level:.1f}_trial{trial_index}.png"
        fig.savefig(os.path.join(SAVE_FOLDER, fname))
        plt.close(fig)

    except Exception as e:
        print(f"[ERROR] {e}")

# Main Loop
for case in [1, 2, 3]:
    for noise in NOISE_LEVELS:
        for trial in range(TRIALS_PER_SETTING):
            TRUE_POS = np.array([random.uniform(-1.5,1.5),random.choice(range(0,10))])
            simulate_and_plot(case, noise, trial, TRUE_POS)
