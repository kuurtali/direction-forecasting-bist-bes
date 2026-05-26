import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Akademik stil ayarları (APA tarzı temiz arka plan)
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.4)
# Akademik Renk Paleti: Lacivert, Bordo, Gri, Turuncu
colors_academic = ["#1A3A6B", "#7B241C", "#7F8C8D", "#D35400"]

def save_plot(filename):
    plt.tight_layout()
    plt.savefig(f"{filename}.png", dpi=300, bbox_inches='tight')
    plt.close()

# 🏆 AKADEMİK ALTIN STANDART 10 GRAFİK 🏆

# 1. Accuracy İllüzyonu (THYAO LSTM Closing)
def plot_1():
    data = {"Metric": ["Accuracy", "Specificity"], "Value": [52.67, 0.0]}
    df = pd.DataFrame(data)
    plt.figure(figsize=(7, 5))
    ax = sns.barplot(x="Metric", y="Value", data=df, palette=[colors_academic[0], "#C0392B"])
    plt.title("Graphic 1: The Accuracy Illusion (LSTM Closing)\nAcc %52 but Spec %0!", fontweight='bold')
    plt.ylim(0, 100)
    save_plot("01_Accuracy_Illusion")

# 2. Vade vs Accuracy (Horizon Analysis)
def plot_2():
    data = {
        "Horizon": ["1 Day", "3 Day", "5 Day"],
        "LSTM": [52.85, 57.56, 54.73],
        "Naive": [53.11, 73.93, 79.73]
    }
    df = pd.DataFrame(data).melt(id_vars="Horizon", var_name="Model", value_name="Accuracy")
    plt.figure(figsize=(7, 5))
    sns.lineplot(x="Horizon", y="Accuracy", hue="Model", style="Model", data=df, markers=True, dashes={"Naive": (2,2), "LSTM": ""}, linewidth=3, palette=[colors_academic[0], colors_academic[2]])
    plt.title("Graphic 2: Prediction Horizon vs. Accuracy\nDL melts against Naive as horizon grows", fontweight='bold')
    save_plot("02_Horizon_vs_Accuracy")

# 3. Model x Varlık Isı Haritası (Heatmap)
def plot_3():
    data = np.array([
        [55.78, 80.65, 80.65], # ARIMA
        [53.97, 75.56, 74.36], # CNN
        [57.56, 68.89, 80.21], # LSTM
        [79.73, 90.32, 83.87]  # Naive
    ])
    models = ["ARIMA", "CNN", "LSTM", "Naive"]
    assets = ["THYAO", "AZS", "AMZ"]
    plt.figure(figsize=(8, 6))
    sns.heatmap(data, annot=True, fmt=".2f", cmap="YlOrRd", xticklabels=assets, yticklabels=models, annot_kws={"weight": "bold"})
    plt.title("Graphic 3: Model x Asset Accuracy Heatmap", fontweight='bold')
    save_plot("03_Model_Asset_Heatmap")

# 4. Balanced Accuracy Krallığı (AMZ Champion)
def plot_4():
    data = {"Model": ["AMZ LSTM", "AMZ CNN"], "Balanced Accuracy": [84.85, 61.67]}
    df = pd.DataFrame(data)
    plt.figure(figsize=(7, 5))
    sns.barplot(x="Model", y="Balanced Accuracy", data=df, palette=[colors_academic[0], colors_academic[1]])
    plt.title("Graphic 4: Balanced Accuracy Comparison\nAMZ LSTM is the true winner", fontweight='bold')
    plt.ylim(0, 100)
    save_plot("04_Balanced_Accuracy_AMZ")

# 5. Risk vs Öğrenilebilirlik (Specificity Trend)
def plot_5():
    data = {"Fund": ["ALZ (Low)", "AZS (Med)", "AMZ (High)"], "Avg Specificity": [0.0, 44.0, 47.4]}
    df = pd.DataFrame(data)
    plt.figure(figsize=(7, 5))
    sns.barplot(x="Fund", y="Avg Specificity", data=df, palette="viridis")
    plt.title("Graphic 5: Asset Risk vs Model Learning Ability\nRisk yields real Specificity", fontweight='bold')
    plt.ylim(0, 60)
    save_plot("05_Risk_vs_Learning")

# 6. LSTM vs CNN Körlük Testi (MC Counts)
def plot_6():
    data = {
        "Period": ["2018-2022", "2018-2022", "2018-2026", "2018-2026"],
        "Model": ["LSTM", "CNN", "LSTM", "CNN"],
        "MC_Count": [16, 8, 12, 9]
    }
    df = pd.DataFrame(data)
    plt.figure(figsize=(8, 5))
    sns.barplot(x="Period", y="MC_Count", hue="Model", data=df, palette=[colors_academic[0], colors_academic[1]])
    plt.title("Graphic 6: LSTM vs CNN - Majority Class Resistance\nCNN is consistently more robust", fontweight='bold')
    save_plot("06_MC_Resistance_Comparison")

# 7. Özellik Seti Etkisi (MC Rate by Set)
def plot_7():
    data = {"Feature Set": ["Closing", "Hist+Tech"], "MC Rate (%)": [100.0, 0.0]}
    df = pd.DataFrame(data)
    plt.figure(figsize=(6, 5))
    ax = sns.barplot(x="Feature Set", y="MC Rate (%)", data=df, palette=["#C0392B", "#27AE60"])
    plt.title("Graphic 7: Impact of Feature Enrichment\nAdding indicators kills the MC bias", fontweight='bold')
    plt.ylim(0, 110)
    save_plot("07_Feature_Set_Impact")

# 8. Concept Drift (2018-2022 vs 2018-2026)
def plot_8():
    metrics = ["LSTM Best", "LSTM Avg", "CNN Avg"]
    old_vals = [60.04, 55.83, 56.79]
    new_vals = [57.56, 50.52, 49.55]
    plt.figure(figsize=(9, 5))
    for i, m in enumerate(metrics):
        plt.plot([old_vals[i], new_vals[i]], [i, i], "r-", alpha=0.3)
        plt.scatter(old_vals[i], i, color=colors_academic[0], s=100, label="2018-2022" if i==0 else "")
        plt.scatter(new_vals[i], i, color=colors_academic[-1], s=100, label="2018-2026" if i==0 else "")
    plt.yticks(range(len(metrics)), metrics)
    plt.title("Graphic 8: Concept Drift Evidence\nGlobal performance drop after 2022", fontweight='bold')
    plt.xlabel("Accuracy (%)")
    plt.legend()
    save_plot("08_Concept_Drift")

# 9. F1-Score ve Sens Dengesi (Quality Signal)
def plot_9():
    data = {"Metric": ["Accuracy", "F1", "Sens", "Spec"], "Score": [80.21, 89.36, 84.00, 85.71]}
    df = pd.DataFrame(data)
    plt.figure(figsize=(7, 5))
    sns.barplot(x="Metric", y="Score", data=df, palette="magma")
    plt.title("Graphic 9: AMZ LSTM Balanced Performance\nHigh Spec + High Sens = Real Power", fontweight='bold')
    plt.ylim(0, 100)
    save_plot("09_Model_Signal_Quality")

# 10. Appendix D: Confusion Matrix (AMZ LSTM)
def plot_10():
    matrix = np.array([[21, 1], [4, 6]]) # TP, FP \n FN, TN
    plt.figure(figsize=(6, 5))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", xticklabels=["Pos", "Neg"], yticklabels=["Pos", "Neg"])
    plt.title("Graphic 10: AMZ LSTM Confusion Matrix\n27/32 Correct Predictions", fontweight='bold')
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    save_plot("10_Confusion_Matrix_Final")

print("Generating Gold Standard 10 Graphics...")
plot_1(); plot_2(); plot_3(); plot_4(); plot_5()
plot_6(); plot_7(); plot_8(); plot_9(); plot_10()
print("All 10 graphics generated in high resolution!")
