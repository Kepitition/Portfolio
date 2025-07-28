import numpy as np
import matplotlib.pyplot as plt
import random

# Trilateration function
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

# Anchors
anchors = [
    np.array([-4.5, 0]),    # A1
    np.array([-1.5, -3]),   # A2
    np.array([1.5, 0])      # A3
]

# True object position
true_pos = np.array([0, 2])

# Compute true distances from anchors to object
true_distances = [np.linalg.norm(true_pos - a) for a in anchors]

# Simulation function
def simulate_error(case, trials=1000):
    """
    Simulates trilateration errors for a specific noise application case.

    This function introduces random noise to the true distances to anchor points
    based on the specified 'case', performs trilateration, and calculates the
    position estimation error for a given number of trials.

    Args:
        case (int): The noise application case:
                    1: Noise is added to the distance of one randomly chosen anchor.
                    2: Noise is added to the distances of two randomly chosen anchors.
                    3: Noise is added to the distances of all three anchors.
                    The noise is a random uniform value between 0 and 5 meters.
        trials (int, optional): The number of simulation trials to perform. Defaults to 1000.

    Returns:
        list: A list of position estimation errors (in meters) for each successful
              trilateration attempt. Attempts where trilateration fails (e.g., due to
              aligned anchors) are skipped.
    """
    errors = []
    for _ in range(trials):
        noisy_distances = true_distances.copy()

        if case == 1:  # One anchor wrong
            i = random.choice([0, 1, 2])
            noisy_distances[i] += random.uniform(0, 5)

        elif case == 2:  # Two anchors wrong
            indices = random.sample([0, 1, 2], 2)
            for i in indices:
                noisy_distances[i] += random.uniform(0, 5)

        elif case == 3:  # All anchors wrong
            noisy_distances = [d + random.uniform(0, 5) for d in true_distances]

        try:
            pos = trilateration(anchors[0], noisy_distances[0],
                                anchors[1], noisy_distances[1],
                                anchors[2], noisy_distances[2])
            error = np.linalg.norm(pos - true_pos)
            errors.append(error)
        except ValueError: # Catch the specific error when anchors are aligned
            continue  # Skip if trilateration fails due to aligned anchors
        except Exception: # Catch any other unexpected errors during trilateration
            continue
    return errors

# Run simulations
errors_one = simulate_error(case=1)
errors_two = simulate_error(case=2)
errors_three = simulate_error(case=3)

# Check if results are populated
if not errors_one or not errors_two or not errors_three:
    print("One or more error lists are empty. Check for issues.")
else:
    print("Simulation completed.")

# Plotting
plt.figure(figsize=(12, 6))
plt.boxplot([errors_one, errors_two, errors_three],
            tick_labels=["1 Anchor Wrong", "2 Anchors Wrong", "3 Anchors Wrong"],
            patch_artist=True,
            boxprops=dict(facecolor="lightblue"),
            medianprops=dict(color="red", linewidth=2))
plt.title("Trilateration Error with Increasing Distance Measurement Noise")
plt.ylabel("Position Estimation Error (m)")
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()