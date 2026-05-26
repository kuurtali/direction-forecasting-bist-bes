import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Paths
DIR_RESULTS = r"c:\Users\Kurt\Desktop\PROJE_ALL\06_Ham_Veri_ve_Sonuclar\2018-2026 çıktılar"
DIR_OUTPUT = r"c:\Users\Kurt\Desktop\PROJE_ALL\04_Gorseller_Grafikler"

# Academic Style Settings
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
sns.set_context("paper", font_scale=1.2)

def load_data():
    files = {
        "THYAO_LSTM": "LSTM_sonuclar_FINAL.csv",
        "THYAO_CNN": "CNN_sonuclar_FINAL.csv",
        "EM_LSTM": "EMEKLILIK_LSTM_sonuclar.csv",
        "EM_CNN": "EMEKLILIK_CNN_sonuclar.csv"
    }
    
    dfs = []
    for label, fname in files.items():
        path = os.path.join(DIR_RESULTS, fname)
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['Source'] = label
            # Standardize names
            if 'Fon' in df.columns:
                df['Asset'] = df['Fon']
            else:
                df['Asset'] = 'THYAO'
            dfs.append(df)
    
    combined = pd.concat(dfs, ignore_index=True)
    
    # Cleaning Sens/Spec (Replacing NA with empirical Majority Class indicators)
    combined['Sens'] = pd.to_numeric(combined['Sens'], errors='coerce').fillna(1.0)
    combined['Spec'] = pd.to_numeric(combined['Spec'], errors='coerce').fillna(0.0)
    combined['Mean_Acc'] = combined['Mean_Acc'] * 100 # Percentage
    
    return combined

def plot_21_sinkhole(df):
    plt.figure(figsize=(10, 7))
    sns.scatterplot(data=df, x='Spec', y='Sens', hue='Asset', style='Optimizer', s=100, alpha=0.6)
    
    # Highlight Sinkhole
    plt.axhspan(0.9, 1.05, 0, 0.1, color='red', alpha=0.1, label='MC Sinkhole')
    plt.text(0.02, 0.95, "Majority Class Sinkhole", color='darkred', fontsize=10, weight='bold')
    
    # Mark Champion
    champ = df[(df['Asset']=='AMZ') & (df['Mean_Acc'] > 80)].iloc[0]
    plt.annotate('Champion (AMZ LSTM)', xy=(champ['Spec'], champ['Sens']), xytext=(champ['Spec']-0.2, champ['Sens']-0.2),
                 arrowprops=dict(facecolor='black', shrink=0.05), weight='bold')

    plt.title("Visual 21: The MC Sinkhole (Decision Quality Map)", fontsize=14)
    plt.xlabel("Specificity (Ability to predict DOWN)", fontsize=12)
    plt.ylabel("Sensitivity (Ability to predict UP)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_OUTPUT, "21_The_MC_Sinkhole.png"), dpi=300)
    plt.close()

def plot_22_stability(df):
    plt.figure(figsize=(8, 6))
    stability = df.groupby('Optimizer')['SD'].mean()
    colors = ['#1A5276', '#7B241C']
    stability.plot(kind='bar', color=colors, edgecolor='black')
    
    plt.title("Visual 22: Optimizer Stability (Adam vs SGD)", fontsize=14)
    plt.ylabel("Average Standard Deviation (Across Seeds)", fontsize=12)
    plt.xlabel("Optimizer Type", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_OUTPUT, "22_Optimizer_Robustness.png"), dpi=300)
    plt.close()

def plot_23_feature_synergy(df):
    plt.figure(figsize=(10, 6))
    # Standardize feature set names
    df['Feature_Set'] = df['Feature_Set'].replace({'cl': 'closing', 'hist_tech': 'full'})
    
    sns.boxplot(data=df, x='Feature_Set', y='Mean_Acc', palette="vlag")
    sns.swarmplot(data=df, x='Feature_Set', y='Mean_Acc', color=".25", size=4, alpha=0.5)
    
    plt.title("Visual 23: Feature Set Synergy Analysis (Cross-Asset)", fontsize=14)
    plt.ylabel("Mean Accuracy (%)", fontsize=12)
    plt.xlabel("Input Feature Configuration", fontsize=12)
    plt.grid(axis='y', linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_OUTPUT, "23_Feature_Synergy_Boxplot.png"), dpi=300)
    plt.close()

def plot_24_window_sensitivity(df):
    plt.figure(figsize=(9, 6))
    # Filter for non-MC models to show real learning
    filtered = df[df['Spec'] > 0]
    
    sns.lineplot(data=filtered, x='Input', y='Mean_Acc', hue='Asset', marker='o', linewidth=2.5)
    
    plt.title("Visual 24: Input Window Sensitivity (Learning Persistence)", fontsize=14)
    plt.xlabel("Input Window Size (Days/Weeks)", fontsize=12)
    plt.ylabel("Mean Accuracy (%)", fontsize=12)
    plt.xticks([2, 4, 6])
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title='Asset', loc='best')
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_OUTPUT, "24_Window_Sensitivity.png"), dpi=300)
    plt.close()

if __name__ == "__main__":
    print("Reading CSVs for deep academic analysis...")
    master_df = load_data()
    print(f"Loaded {len(master_df)} experimental runs.")
    
    print("Generating Academic Visuals...")
    plot_21_sinkhole(master_df)
    plot_22_stability(master_df)
    plot_23_feature_synergy(master_df)
    plot_24_window_sensitivity(master_df)
    
    print(f"Success! 4 new academic assets saved to: {DIR_OUTPUT}")
