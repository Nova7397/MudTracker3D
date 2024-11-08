import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load data
data = pd.read_csv("C:\\Users\\dinki\\OneDrive - Delft University of Technology\\MSc3_CORE_Group 6\\Dataset\\Prototype V2\\Rating assessment\\Prototype rating.csv")

print(data.columns)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Set up a grid of subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot each score type as a heatmap
score_types = ['Overhang', 'Zigzag', 'Freeform']
for i, score in enumerate(score_types):
    # Create pivot table for each score type
    try:
        pivot_table = data.pivot(index="Layer_height", columns="Extrusion_rate", values=score)
        sns.heatmap(pivot_table, ax=axes[i // 2, i % 2], annot=True, cmap="coolwarm", cbar=True)
        axes[i // 2, i % 2].set_title(score)
    except KeyError as e:
        print(f"KeyError: {e}. Please ensure the column '{score}' exists in the data.")
    except ValueError as e:
        print(f"ValueError: {e}. Check for duplicate entries in 'Layer_height' and 'Extrusion_rate'.")

plt.tight_layout()
plt.show()

from pandas.plotting import parallel_coordinates

# Melt the data for easier plotting
melted_data = data.melt(id_vars=["Layer_height", "Extrusion_rate"], 
                        value_vars=score_types, 
                        var_name="Score Type", value_name="Score")

# Plot using parallel coordinates
plt.figure(figsize=(10, 6))
parallel_coordinates(melted_data, class_column="Score Type", cols=["Layer_height", "Extrusion_rate", "Score"])
plt.title("Parallel Coordinates Plot")
plt.show()

import seaborn as sns

# Pairplot for all variables
sns.pairplot(data)
plt.show()

from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Example: Visualizing Top Overhang Score
ax.scatter(data["Layer_height"], data["Extrusion_rate"], data["Overhang"], c=data["Overhang"], cmap='viridis')
ax.set_xlabel("Layer_height")
ax.set_ylabel("Extrusion_rate")
ax.set_zlabel("Overhang")