"""
MC-Aware STRES TESTİ — AZS Closing-Only (Saf MC Vakası)
========================================================
Hedef:
  Mevcut çalışmada AZS closing feature set'inde TÜM 9 konfigürasyon LSTM'de
  %100 MC. Burada en sert vakayı (In=2, Out=5) feedforward MLP'de prototiple
  test ediyorum.

Beklenti:
  Vanilla (λ=0): MC olmalı (Spec=0 veya 1, tek yön).
  λ artırıldıkça: MC'den kurtulma var mı?

NOT: 1-feature (closing-only) zaten az bilgi → öğrenme zayıf olacak. Asıl
soru: MC_Penalty mean(ŷ)'yi 0.5'e iterken Spec/Sens dengesini iyileştiriyor mu?
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, "/sessions/laughing-loving-archimedes/mnt/Proje/06_Calısma_Alanı")

# Aynı yardımcı fonksiyonları yeniden tanımla
def sigmoid(z): return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))

def init_mlp(in_dim, hidden, seed):
    rng = np.random.default_rng(seed)
    return {
        "W1": rng.normal(0, np.sqrt(2/in_dim), (in_dim, hidden)),
        "b1": np.zeros(hidden),
        "W2": rng.normal(0, np.sqrt(2/hidden), (hidden, 1)),
        "b2": np.zeros(1),
    }

def forward(params, X):
    z1 = X @ params["W1"] + params["b1"]
    h1 = np.tanh(z1)
    z2 = h1 @ params["W2"] + params["b2"]
    return sigmoid(z2).ravel(), h1

def train(X_tr, y_tr, X_va, y_va, seed=23, lam=0.0,
          hidden=16, lr=0.01, epochs=200):
    params = init_mlp(X_tr.shape[1], hidden, seed)
    best_va_acc, best_params, patience_cnt = 0.0, None, 0
    for ep in range(epochs):
        yhat_tr, h1 = forward(params, X_tr)
        n = len(y_tr)
        dz2 = (yhat_tr - y_tr).reshape(-1, 1) / n
        if lam > 0:
            sign = np.sign(yhat_tr.mean() - 0.5)
            mc_grad = lam * sign * (yhat_tr * (1 - yhat_tr)).reshape(-1, 1) / n
            dz2 = dz2 + mc_grad
        dW2 = h1.T @ dz2
        db2 = dz2.sum(axis=0)
        dh1 = dz2 @ params["W2"].T
        dz1 = dh1 * (1 - h1**2)
        dW1 = X_tr.T @ dz1
        db1 = dz1.sum(axis=0)
        for k, g in zip(["W1","b1","W2","b2"], [dW1, db1, dW2, db2]):
            params[k] -= lr * g
        if ep % 5 == 4:
            yhat_va, _ = forward(params, X_va)
            va_acc = ((yhat_va > 0.5).astype(int) == y_va.astype(int)).mean()
            if va_acc > best_va_acc:
                best_va_acc = va_acc
                best_params = {k: v.copy() for k, v in params.items()}
                patience_cnt = 0
            else:
                patience_cnt += 1
                if patience_cnt >= 5:
                    break
    return best_params if best_params is not None else params

def evaluate(params, X_te, y_te):
    yhat, _ = forward(params, X_te)
    pred = (yhat > 0.5).astype(int)
    y_int = y_te.astype(int)
    tp = ((pred == 1) & (y_int == 1)).sum()
    tn = ((pred == 0) & (y_int == 0)).sum()
    fp = ((pred == 1) & (y_int == 0)).sum()
    fn = ((pred == 0) & (y_int == 1)).sum()
    acc = (tp + tn) / len(y_int) if len(y_int) > 0 else np.nan
    sens = tp / (tp + fn) if (tp + fn) > 0 else np.nan
    spec = tn / (tn + fp) if (tn + fp) > 0 else np.nan
    return {"Acc": acc, "Sens": sens, "Spec": spec, "mean_yhat": yhat.mean(),
            "n_pred_Up": int(pred.sum()), "n_pred_Down": int(len(pred) - pred.sum()),
            "is_MC": (spec == 0.0) or (sens == 0.0) or np.isnan(spec) or np.isnan(sens)}

# AZS verisini yükle
XLSX = Path("/sessions/laughing-loving-archimedes/mnt/Proje/02_Akademik_Kanıtlar/ALZ_AZS_AMZ_Haftalik.xlsx")
df = pd.read_excel(XLSX)
df.columns = ["Date", "Price_ALZ", "LR_ALZ", "Price_AZS", "LR_AZS", "Price_AMZ", "LR_AMZ"]
df = df.dropna(subset=["Price_AZS"]).reset_index(drop=True)
prices_azs = df["Price_AZS"].values
print(f"AZS veri: {len(prices_azs)} hafta")

# CLOSING-ONLY feature: sadece Close
features = prices_azs.reshape(-1, 1)

# Pencereleme: In=2, Out=5 (mevcut çalışmada AZS LSTM closing/In=2/Out=5 → Sens=0, Spec=1, saf MC Down)
IN_LEN, OUT_LEN = 2, 5
X_list, y_list = [], []
for t in range(IN_LEN, len(prices_azs) - OUT_LEN):
    X_list.append(features[t-IN_LEN:t].flatten())
    y_list.append(1 if prices_azs[t + OUT_LEN] > prices_azs[t] else 0)

X = np.array(X_list, dtype=np.float64)
y = np.array(y_list, dtype=np.float64)
print(f"Toplam örnek: {len(X)} | Up=%{y.mean()*100:.1f}")

n = len(X)
i_tr = int(n * 0.70)
i_va = int(n * 0.85)
X_tr, y_tr = X[:i_tr], y[:i_tr]
X_va, y_va = X[i_tr:i_va], y[i_tr:i_va]
X_te, y_te = X[i_va:], y[i_va:]
print(f"Split: Eğitim={len(X_tr)} | Doğrulama={len(X_va)} | Test={len(X_te)}")
print(f"Test Up=%{y_te.mean()*100:.1f} (n={len(y_te)}, Up={int(y_te.sum())}, Down={int(len(y_te)-y_te.sum())})")

mu = X_tr.mean(axis=0)
sd = X_tr.std(axis=0) + 1e-8
X_tr = (X_tr - mu) / sd
X_va = (X_va - mu) / sd
X_te = (X_te - mu) / sd

SEEDS = [23, 27, 98]
LAMBDAS = [0.0, 0.1, 0.3, 0.5, 1.0]  # daha geniş lambda aralığı

print("\n" + "="*85)
print(f"AZS — closing / In={IN_LEN} / Out={OUT_LEN} — STRES TESTİ (saf MC vakası)")
print("="*85)
print(f"{'λ':>5} | {'Seed':>4} | {'Acc':>6} | {'Sens':>6} | {'Spec':>6} | {'mean(ŷ)':>8} | {'#Up':>4} | {'#Dn':>4} | {'MC?':>3}")
print("-" * 85)

rows = []
for lam in LAMBDAS:
    for sd_ in SEEDS:
        params = train(X_tr, y_tr, X_va, y_va, seed=sd_, lam=lam)
        m = evaluate(params, X_te, y_te)
        rows.append({"lambda": lam, "seed": sd_, **m})
        print(f"{lam:>5.1f} | {sd_:>4d} | {m['Acc']:>6.4f} | "
              f"{m['Sens']:>6.4f} | {m['Spec']:>6.4f} | {m['mean_yhat']:>8.4f} | "
              f"{m['n_pred_Up']:>4d} | {m['n_pred_Down']:>4d} | {'YES' if m['is_MC'] else 'no':>3}")

print("\n" + "="*85)
print("ÖZET — λ başına 3-seed ortalaması + MC sayısı")
print("="*85)
print(f"{'λ':>5} | {'Acc±SD':>14} | {'Sens±SD':>14} | {'Spec±SD':>14} | {'mean(ŷ)':>9} | {'MC':>3}")
print("-" * 85)
res = pd.DataFrame(rows)
for lam in LAMBDAS:
    sub = res[res["lambda"] == lam]
    mc_count = sub["is_MC"].sum()
    print(f"{lam:>5.1f} | "
          f"{sub['Acc'].mean():>6.4f}±{sub['Acc'].std():>5.4f} | "
          f"{sub['Sens'].mean():>6.4f}±{sub['Sens'].std():>5.4f} | "
          f"{sub['Spec'].mean():>6.4f}±{sub['Spec'].std():>5.4f} | "
          f"{sub['mean_yhat'].mean():>9.4f} | "
          f"{int(mc_count):>1d}/3")

out_csv = Path("/sessions/laughing-loving-archimedes/mnt/Proje/06_Calısma_Alanı/mcaware_prototype_azs_closing_stress_RESULTS.csv")
res.to_csv(out_csv, index=False)
print(f"\nCSV: {out_csv}")
