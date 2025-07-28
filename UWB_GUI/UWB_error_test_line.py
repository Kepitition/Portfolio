import numpy as np
import matplotlib.pyplot as plt
import random

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
true_distances = [np.linalg.norm(true_pos - a) for a in anchors]

def simulate_errors(noise_levels, case, trials=100):
    """
    Simulates trilateration errors for various noise levels and a given error case.

    This function calculates the mean position error of trilateration by
    introducing random noise to the true distances from an object to anchors
    under different "error cases" (how noise is applied).

    Args:
        noise_levels (list or np.ndarray): A list or array of maximum noise
                                           magnitudes (in meters) to simulate.
                                           Noise is applied uniformly within
                                           [-noise, noise] for each level.
        case (int): The specific error case to simulate:
                    1: Noise is applied to one randomly selected anchor's distance.
                    2: Noise is applied to two randomly selected anchors' distances.
                    3: Noise is applied to all three anchors' distances.
        trials (int, optional): The number of simulation trials to run for
                                each noise level. Defaults to 100.

    Returns:
        list: A list of mean position errors (in meters), corresponding to each
              noise level. If no valid position can be calculated for a given
              noise level (e.g., due to aligned anchors), np.nan is returned.
    """
    mean_errors = []

    for noise in noise_levels:
        errors = []
        for _ in range(trials):
            noisy = true_distances.copy()

            if case == 1:  # 1 anchor wrong
                i = random.choice([0, 1, 2])
                noisy[i] += random.uniform(-noise, noise)

            elif case == 2:  # 2 anchors wrong
                for i in random.sample([0, 1, 2], 2):
                    noisy[i] += random.uniform(-noise, noise)

            elif case == 3:  # 3 anchors wrong
                noisy = [d + random.uniform(-noise, noise) for d in true_distances]

            try:
                pos = trilateration(anchors[0], noisy[0],
                                    anchors[1], noisy[1],
                                    anchors[2], noisy[2])
                error = np.linalg.norm(pos - true_pos)
                errors.append(error)
            except ValueError:  # Catch specific ValueError for aligned anchors
                continue
            except Exception: # Catch any other unexpected errors during trilateration
                continue

        # Calculate mean error, handling cases where 'errors' might be empty
        mean_errors.append(np.mean(errors) if errors else np.nan)

    return mean_errors

# Noise levels from 0 to 5 meters
noise_levels = np.linspace(0, 5, 11)

# Run simulations
errors_1 = simulate_errors(noise_levels, case=1)
errors_2 = simulate_errors(noise_levels, case=2)
errors_3 = simulate_errors(noise_levels, case=3)

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(noise_levels, errors_1, marker='o', label="1 Anchor Wrong")
plt.plot(noise_levels, errors_2, marker='s', label="2 Anchors Wrong")
plt.plot(noise_levels, errors_3, marker='^', label="3 Anchors Wrong")

plt.title("Trilateration Error vs. Distance Noise Level")
plt.xlabel("Max Distance Noise (m)")
plt.ylabel("Mean Position Error (m)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()