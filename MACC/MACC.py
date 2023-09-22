import matplotlib.pyplot as plt
import numpy as np


# Define functions for getting text and annotation positions
def get_text_position(left, width, height, previous):
    text_x = left + width / 2
    text_y = height / 2 if height >= 0 else height + (previous - height) / 2
    rotation = 90 if height >= 0 else -90
    return text_x, text_y, rotation


# Data from dfMACC
emission = dfMACC["Cumulative Emission"].tolist()
abat_cost = dfMACC["Abatement Cost"].tolist()
differences = dfMACC["Abatement Potential"].tolist()
opportunity = dfMACC["Opportunity"].tolist()
cpex = dfMACC["Cumulative CAPEX"].tolist()

# Create subplots
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(2, 1, height_ratios=[2, 1])  # Adjust height ratios as needed

# Create the top and bottom subplots
ax2 = fig.add_subplot(gs[1], sharex=ax1)
ax1 = fig.add_subplot(gs[0])

# Set spines for ax1
ax1.spines[["left", "bottom"]].set_position(("data", 0))
ax1.spines[["top", "right"]].set_visible(False)

# Plot Bar Chart on Top Plot
left = 0
previous = 0
x_scale = 100  # Define your own x_scale value
for height, width, opp in zip(abat_cost, differences, opportunity):
    text_x, text_y, rotation = get_text_position(left, width, height, previous)

    ax1.bar(left, height, width=width, align="edge", label=opp)
    # Add annotations if needed
    # ax1.annotate(
    #     opp,
    #     xy=(left, height),
    #     xytext=(text_x, text_y),
    #     textcoords="offset points",
    #     ha="left",
    #     va="bottom",
    #     rotation=rotation,
    #     arrowprops=dict(arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90,rad=10", color="black"),
    #     fontsize=8,
    # )
    left += width
    previous = get_text_position(left, width, height, previous)[0]

ax1.set_xlim(0, 1.1 * max(emission))
ax1.set_xticks(np.arange(0, 1.1 * max(emission), x_scale))
ax1.set_xlabel("Cumulative Emission (tCO2e)")
ax1.set_ylabel("Abatement Cost ($)")
ax1.legend(loc="upper left", fontsize=8)
ax1.set_ylim(-150, 500)
ax1.set_yticks(np.arange(-150, 500, 50))
ax1.grid(visible=True, axis="y")

# Plot Line Graph on Bottom Plot
ax2.grid(visible=False)
ax2.set_ylabel("Cumulative CAPEX (Million $)")
ax2.set_xlabel("Cumulative Emission (tCO2e)")
ax2.plot(emission, cpex, marker="x", markersize=2, color="b", label="Cumulative CAPEX")
ax2.set_ylim(0, 1.1 * max(cpex))

# Add a title and adjust layout
title = "Overall Marginly Abated Cost Curve (MACC)"
plt.suptitle(title)
plt.tight_layout()

# Show the plots
plt.show()
