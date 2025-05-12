import matplotlib.pyplot as plt
import numpy as np

def show_plots(labels, times, pressures):
    fig, axs = plt.subplots(2, 1, figsize=(8, 7))
    # Time vs Node
    axs[0].bar(labels, times, color="#4FC3F7")
    axs[0].set_title("Time to Reach Each Node")
    axs[0].set_ylabel("Time")
    axs[0].set_xlabel("Node")
    axs[0].grid(True, linestyle="--", alpha=0.3)

    # Pressure vs Node
    colors = ["#FF5252" if p < 20 else "#81C784" for p in pressures]
    axs[1].bar(labels, pressures, color=colors)
    axs[1].set_title("Pressure at Each Node")
    axs[1].set_ylabel("Pressure")
    axs[1].set_xlabel("Node")
    axs[1].grid(True, linestyle="--", alpha=0.3)
    for i, p in enumerate(pressures):
        if p < 20:
            axs[1].text(i, p+2, "Low", ha='center', color="#FF5252", fontweight='bold')

    plt.tight_layout()
    plt.show()