import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Best 4 Models Confusion Matrices
# 1. AMZ LSTM
# 2. AZS CNN
# 3. THYAO LSTM MC (Illusion)
# 4. THYAO LSTM Optimized (Realist)

matrices = {
    "AMZ LSTM Champion": np.array([[21, 1], [4, 6]]), # TP=21, FP=1, FN=4, TN=6
    "AZS CNN Balanced": np.array([[25, 3], [3, 6]]), # TP=25, FP=3, FN=3, TN=6
    "THYAO MC Illusion": np.array([[96, 89], [0, 0]]), # TP=96, FP=89, FN=0, TN=0
    "THYAO Optimized": np.array([[92, 60], [68, 90]]) # TP=92, FP=60, FN=68, TN=90
}

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()

for i, (name, matrix) in enumerate(matrices.items()):
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", ax=axes[i], 
                xticklabels=["Pred Up", "Pred Down"], 
                yticklabels=["Actual Up", "Actual Down"])
    axes[i].set_title(name, fontweight='bold', fontsize=14)
    axes[i].set_xlabel("Predicted")
    axes[i].set_ylabel("Actual")

plt.suptitle("Appendix D: Key Models Confusion Matrix Portfolio", fontsize=18, fontweight='bold', y=0.95)
plt.tight_layout(rect=[0, 0.03, 1, 0.92])
plt.savefig("Appendix_D_Matrix_Portfolio.png", dpi=300)
print("Appendix D Portfolio generated successfully!")
