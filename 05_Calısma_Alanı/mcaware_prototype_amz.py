"""
MC-Aware Prototype — Konsept İspatı (AMZ)
==========================================
TÜBİTAK 2209-A Ön Kanıt Çalışması

Amaç:
  AMZ emeklilik fonu üzerinde MC_Penalty teriminin Spec ve mean(ŷ) üzerindeki
  etkisini gösteren minimal feedforward MLP deneyi. LSTM değil (sandbox'ta TF
  yüklenemediği için) ama MC_Penalty mekaniği bağımsız olarak gösteriliyor.

Karşılaştırma:
  Vanilla BCE  vs  BCE + λ·|mean(ŷ)−0.5|   (λ ∈ {0.0, 0.1, 0.3, 0.5})

Konfigürasyon:
  Hedef: yön tahmini (P_{t+Out} > P_t → 1)
  Input length = 2, Output horizon = 3  (mevcut AMZ LSTM şampiyonuyla aynı)
  Feature set = full (Close, RSI, MACD, EMA12, EMA26, Momentum, Volatility)
  3 seed: 23, 27, 98 (mevcut çalışmayla aynı)
  Split: 70/15/15 kronolojik

NOT: Bu numpy MLP basit bir karşılaştırma için. Tam LSTM replikasyonu için
R/keras3 script'i ayrıca üretilecek (kullanıcının Windows makinesinde).
"""

import numpy as np
import pandas as pd
from pathlib import Path

# -------------------- 0. VERİ YÜKLEME --------------------
XLSX = Path("/sessions/laughing-loving-archimedes/mnt/Proje/02_Akademik_Kanıtlar/ALZ_AZS_AMZ_Haftalik.xlsx")
df = pd.read_excel(XLSX)
df.columns = ["Date", "Price_ALZ", "LR_ALZ", "Price_AZS", "LR_AZS", "Price_AMZ", "LR_AMZ"]
df = df.dropna(subset=["Price_AMZ"]).reset_index(drop=True)
print(f"AMZ veri: {len(df)} hafta")

# -------------------- 1. ÖZELLİK MÜHENDİSLİĞİ --------------------
def rsi(prices, period=14):
    delta = np.diff(prices, prepend=prices[0])
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = pd.Series(gain).rolling(period, min_periods=1).mean().values
    avg_loss = pd.Series(loss).rolling(period, min_periods=1).mean().values
    rs = avg_gain / (avg_loss + 1e-10)
    return 100 - (100 / (1 + rs))

def ema(prices, span):
    return pd.Series(prices).ewm(span=span, adjust=False).mean().values

def macd(prices):
    return ema(prices, 12) - ema(prices, 26)

def momentum(prices, lag=14):
    p = pd.Series(prices)
    return (p / p.shift(lag) - 1).fillna(0).values

def volatility(prices, window=14):
    lr = pd.Series(np.log(prices)).diff().fillna(0)
    return lr.rolling(window, min_periods=1).std().values

prices = df["Price_AMZ"].values
features = np.column_stack([
    prices,                  # Close
    rsi(prices, 14),         # RSI(14)
    macd(prices),            # MACD
    ema(prices, 12),         # EMA12
    ema(prices, 26),         # EMA26
    momentum(prices, 14),    # Momentum(14)
    volatility(prices, 14),  # Volatility(14)
])

# Warmup süresi: ilk 14 hafta atılır (RSI/Momentum/Vol için)
features = features[14:]
prices_clean = prices[14:]
print(f"Warmup sonrası: {len(features)} hafta")

# -------------------- 2. PENCERELEME (In=2, Out=3) --------------------
IN_LEN, OUT_LEN = 2, 3
X_list, y_list = [], []
for t in range(IN_LEN, len(prices_clean) - OUT_LEN):
    X_list.append(features[t-IN_LEN:t].flatten())  # In=2 hafta × 7 feature = 14-d
    y_list.append(1 if prices_clean[t + OUT_LEN] > prices_clean[t] else 0)

X = np.array(X_list, dtype=np.float64)
y = np.array(y_list, dtype=np.float64)
print(f"Toplam örnek: {len(X)} | X.shape={X.shape} | Sınıf oranı: Up=%{y.mean()*100:.1f}")

# -------------------- 3. SPLIT (70/15/15 kronolojik) --------------------
n = len(X)
i_tr = int(n * 0.70)
i_va = int(n * 0.85)
X_tr, y_tr = X[:i_tr], y[:i_tr]
X_va, y_va = X[i_tr:i_va], y[i_tr:i_va]
X_te, y_te = X[i_va:], y[i_va:]
print(f"Split: Eğitim={len(X_tr)} | Doğrulama={len(X_va)} | Test={len(X_te)}")
print(f"Test sınıf dağılımı: Up=%{y_te.mean()*100:.1f} (n={len(y_te)}, Up={int(y_te.sum())}, Down={int(len(y_te)-y_te.sum())})")

# Train-only normalization (data leakage önleme)
mu = X_tr.mean(axis=0)
sd = X_tr.std(axis=0) + 1e-8
X_tr = (X_tr - mu) / sd
X_va = (X_va - mu) / sd
X_te = (X_te - mu) / sd

# -------------------- 4. BASİT MLP (manuel gradient) --------------------
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
    yhat = sigmoid(z2).ravel()
    return yhat, h1

def train(X_tr, y_tr, X_va, y_va, seed=23, lam=0.0,
          hidden=16, lr=0.01, epochs=150, verbose=False):
    """
    Loss = BCE(y,ŷ) + lam · |mean(ŷ) − 0.5|
    """
    params = init_mlp(X_tr.shape[1], hidden, seed)
    best_va_acc, best_params, patience_cnt = 0.0, None, 0
    eps = 1e-8

    for ep in range(epochs):
        yhat_tr, h1 = forward(params, X_tr)
        n = len(y_tr)

        # BCE gradient
        dz2 = (yhat_tr - y_tr).reshape(-1, 1) / n   # (n,1)

        # MC_Penalty gradient: lam · sign(mean(ŷ) − 0.5) · d_mean(ŷ)/d_z2
        # d_mean(ŷ)/d_z2_i = ŷ_i(1-ŷ_i) / n
        mean_yhat = yhat_tr.mean()
        if lam > 0:
            sign = np.sign(mean_yhat - 0.5)
            mc_grad = lam * sign * (yhat_tr * (1 - yhat_tr)).reshape(-1, 1) / n
            dz2 = dz2 + mc_grad

        # Backprop
        dW2 = h1.T @ dz2
        db2 = dz2.sum(axis=0)
        dh1 = dz2 @ params["W2"].T
        dz1 = dh1 * (1 - h1**2)
        dW1 = X_tr.T @ dz1
        db1 = dz1.sum(axis=0)

        for k, g in zip(["W1","b1","W2","b2"], [dW1, db1, dW2, db2]):
            params[k] -= lr * g

        # Erken durdurma (val acc bazlı, patience=5)
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
    return {
        "Acc": acc,
        "Sens": sens,
        "Spec": spec,
        "mean_yhat": yhat.mean(),
        "n_pred_Up": int(pred.sum()),
        "n_pred_Down": int(len(pred) - pred.sum()),
        "is_MC": (spec == 0.0) or (sens == 0.0) or np.isnan(spec) or np.isnan(sens),
    }

# -------------------- 5. GRID: λ × seed --------------------
SEEDS = [23, 27, 98]
LAMBDAS = [0.0, 0.1, 0.3, 0.5]

print("\n" + "="*80)
print(f"AMZ — full / In={IN_LEN} / Out={OUT_LEN} — MC_Penalty λ-grid")
print("="*80)
print(f"{'λ':>5} | {'Seed':>4} | {'Acc':>6} | {'Sens':>6} | {'Spec':>6} | {'mean(ŷ)':>8} | {'#Up':>4} | {'#Dn':>4} | {'MC?':>3}")
print("-" * 80)

rows = []
for lam in LAMBDAS:
    for sd in SEEDS:
        params = train(X_tr, y_tr, X_va, y_va, seed=sd, lam=lam)
        m = evaluate(params, X_te, y_te)
        rows.append({"lambda": lam, "seed": sd, **m})
        print(f"{lam:>5.1f} | {sd:>4d} | {m['Acc']:>6.4f} | "
              f"{m['Sens']:>6.4f} | {m['Spec']:>6.4f} | {m['mean_yhat']:>8.4f} | "
              f"{m['n_pred_Up']:>4d} | {m['n_pred_Down']:>4d} | {'YES' if m['is_MC'] else 'no':>3}")

# -------------------- 6. ÖZET TABLO (λ başına ortalama) --------------------
print("\n" + "="*80)
print("ÖZET — λ başına 3-seed ortalaması")
print("="*80)
print(f"{'λ':>5} | {'Acc±SD':>14} | {'Sens±SD':>14} | {'Spec±SD':>14} | {'mean(ŷ)':>9} | {'MC vakası':>9}")
print("-" * 80)
res = pd.DataFrame(rows)
for lam in LAMBDAS:
    sub = res[res["lambda"] == lam]
    mc_count = sub["is_MC"].sum()
    print(f"{lam:>5.1f} | "
          f"{sub['Acc'].mean():>6.4f}±{sub['Acc'].std():>5.4f} | "
          f"{sub['Sens'].mean():>6.4f}±{sub['Sens'].std():>5.4f} | "
          f"{sub['Spec'].mean():>6.4f}±{sub['Spec'].std():>5.4f} | "
          f"{sub['mean_yhat'].mean():>9.4f} | "
          f"{int(mc_count):>2d}/3")

# Sonuçları CSV'ye yaz
out_csv = Path("/sessions/laughing-loving-archimedes/mnt/Proje/06_Calısma_Alanı/mcaware_prototype_amz_RESULTS.csv")
res.to_csv(out_csv, index=False)
print(f"\nCSV: {out_csv}")
