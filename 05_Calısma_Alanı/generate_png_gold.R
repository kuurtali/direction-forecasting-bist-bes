library(ggplot2)
library(dplyr)
library(tidyr)

# Academic Color Palette
cols <- c("#1A3A6B", "#7B241C", "#7F8C8D", "#D35400")

# Directories
en_dir <- "c:/Users/Kurt/Desktop/Proje/04_Gorsel_Portfolyo/EN_Graphics"
tr_dir <- "c:/Users/Kurt/Desktop/Proje/04_Gorsel_Portfolyo/TR_Grafikler"

dir.create(en_dir, showWarnings = FALSE)
dir.create(tr_dir, showWarnings = FALSE)

# Helper for saving
save_plot <- function(filename, plot_obj, lang="EN") {
  path <- if(lang=="EN") file.path(en_dir, filename) else file.path(tr_dir, filename)
  ggsave(path, plot = plot_obj, width = 7, height = 5, units = "in", dpi = 300, bg="white")
}

# Base Theme
base_theme <- theme_minimal(base_size = 14) + 
  theme(plot.title = element_text(face="bold", size=14),
        panel.grid.minor = element_blank())

# 1. Accuracy Illusion
generate_plot_1 <- function(lang) {
  df <- data.frame(
    Metric = if(lang=="EN") c("Accuracy", "Specificity") else c("Doğruluk", "Özgüllük"),
    Value = c(52.67, 0.0)
  )
  title <- if(lang=="EN") "Graphic 1: The Accuracy Illusion (LSTM Closing)\nAcc %52.67 but Spec %0!" else "Grafik 1: Doğruluk Yanılgısı (LSTM Kapanış)\nDoğruluk %52.67 ama Özgüllük %0!"
  
  p <- ggplot(df, aes(x=Metric, y=Value, fill=Metric)) + 
    geom_bar(stat="identity", width=0.6) + 
    scale_fill_manual(values=c(cols[1], "#C0392B")) +
    coord_cartesian(ylim=c(0, 100)) + 
    labs(title=title, x="", y="") +
    base_theme + theme(legend.position="none")
  
  save_plot("01_Accuracy_Illusion.png", p, lang)
}

# 2. Horizon vs Accuracy
generate_plot_2 <- function(lang) {
  df <- data.frame(
    Horizon = if(lang=="EN") factor(c("1 Day", "3 Day", "5 Day"), levels=c("1 Day", "3 Day", "5 Day")) else factor(c("1. Gün", "3. Gün", "5. Gün"), levels=c("1. Gün", "3. Gün", "5. Gün")),
    LSTM = c(52.85, 57.56, 54.73),
    Naive = c(53.11, 73.93, 79.73)
  )
  df_long <- pivot_longer(df, cols=c(LSTM, Naive), names_to="Model", values_to="Accuracy")
  
  title <- if(lang=="EN") "Graphic 2: Prediction Horizon vs. Accuracy\nLSTM melts against Naive as horizon grows" else "Grafik 2: Ufuk Süresi ve Doğruluk (Horizon Analizi)\nUfuk süresi uzadıkça LSTM, Naive gerisinde kalıyor"
  ylabel <- if(lang=="EN") "Accuracy (%)" else "Doğruluk (%)"
  
  p <- ggplot(df_long, aes(x=Horizon, y=Accuracy, group=Model, color=Model, linetype=Model)) +
    geom_line(size=1.5) + geom_point(size=4) +
    scale_color_manual(values=c(cols[1], cols[3])) +
    labs(title=title, x="", y=ylabel) + base_theme
  
  save_plot("02_Horizon_vs_Accuracy.png", p, lang)
}

# 3. Model x Asset Heatmap
generate_plot_3 <- function(lang) {
  models <- c("ARIMA", "CNN", "LSTM", "Naive")
  assets <- c("THYAO", "AZS", "AMZ")
  data <- c(55.78, 53.97, 57.56, 79.73, 
            80.65, 75.56, 68.89, 90.32, 
            80.65, 74.36, 80.21, 83.87)
  
  df <- data.frame(
    Model = rep(models, times=3),
    Asset = rep(assets, each=4),
    Value = data
  )
  df$Model <- factor(df$Model, levels=rev(models))
  
  title <- if(lang=="EN") "Graphic 3: Model x Asset Accuracy Heatmap" else "Grafik 3: Model ve Varlık Doğruluk Isı Haritası"
  
  p <- ggplot(df, aes(x=Asset, y=Model, fill=Value)) + 
    geom_tile(color="white", size=1) +
    geom_text(aes(label=sprintf("%.2f", Value)), size=5, fontface="bold", color="black") +
    scale_fill_gradient(low="yellow", high="red") +
    labs(title=title, x="", y="") + base_theme + theme(legend.position="none")
  
  save_plot("03_Model_Asset_Heatmap.png", p, lang)
}

# 4. Balanced Accuracy
generate_plot_4 <- function(lang) {
  df <- data.frame(
    Model = factor(c("AMZ LSTM", "AMZ CNN"), levels=c("AMZ LSTM", "AMZ CNN")),
    Score = c(84.85, 61.67)
  )
  title <- if(lang=="EN") "Graphic 4: Balanced Accuracy Comparison\nAMZ LSTM is the true winner" else "Grafik 4: Dengeli Doğruluk Karşılaştırması\nAMZ LSTM gerçek kazanan"
  ylabel <- if(lang=="EN") "Balanced Accuracy (%)" else "Dengeli Doğruluk (%)"
  
  p <- ggplot(df, aes(x=Model, y=Score, fill=Model)) + geom_bar(stat="identity", width=0.5) +
    scale_fill_manual(values=c(cols[1], cols[2])) + coord_cartesian(ylim=c(0, 100)) +
    labs(title=title, x="", y=ylabel) + base_theme + theme(legend.position="none")
  
  save_plot("04_Balanced_Accuracy_AMZ.png", p, lang)
}

# 5. Risk vs Learning
generate_plot_5 <- function(lang) {
  df <- data.frame(
    Fund = if(lang=="EN") factor(c("ALZ (Low)", "AZS (Med)", "AMZ (High)"), levels=c("ALZ (Low)", "AZS (Med)", "AMZ (High)")) else factor(c("ALZ (Düşük)", "AZS (Orta)", "AMZ (Yüksek)"), levels=c("ALZ (Düşük)", "AZS (Orta)", "AMZ (Yüksek)")),
    Score = c(0.0, 44.0, 47.4)
  )
  title <- if(lang=="EN") "Graphic 5: Asset Risk vs Model Learning Ability\nRisk yields real Specificity" else "Grafik 5: Varlık Riski ve Model Öğrenme Kabiliyeti\nRisk, gerçek Özgüllük sağlar"
  ylabel <- if(lang=="EN") "Avg Specificity (%)" else "Ort. Özgüllük (%)"
  
  p <- ggplot(df, aes(x=Fund, y=Score, fill=Fund)) + geom_bar(stat="identity", width=0.6) +
    scale_fill_viridis_d(option="D") + coord_cartesian(ylim=c(0, 60)) +
    labs(title=title, x="", y=ylabel) + base_theme + theme(legend.position="none")
  
  save_plot("05_Risk_vs_Learning.png", p, lang)
}

# 6. MC Resistance Comparison
generate_plot_6 <- function(lang) {
  df <- data.frame(
    Period = factor(c("2018-2022","2018-2022","2018-2026","2018-2026"), levels=c("2018-2022", "2018-2026")),
    Model = c("LSTM", "CNN", "LSTM", "CNN"),
    MCCount = c(16, 8, 12, 9)
  )
  title <- if(lang=="EN") "Graphic 6: LSTM vs CNN - Majority Class Resistance\nCNN is consistently more robust" else "Grafik 6: LSTM vs CNN - Çoğunluk Sınıfı Direnci\nCNN sürekli olarak daha dirençli"
  ylabel <- if(lang=="EN") "MC Target Condition Count" else "Majority Sınıfı Oluşum Sayısı"
  
  p <- ggplot(df, aes(x=Period, y=MCCount, fill=Model)) + geom_bar(stat="identity", position="dodge", width=0.6) +
    scale_fill_manual(values=c(cols[2], cols[1])) +
    labs(title=title, x="", y=ylabel) + base_theme
  
  save_plot("06_MC_Resistance_Comparison.png", p, lang)
}

# 7. Impact of Feature Sets
generate_plot_7 <- function(lang) {
  df <- data.frame(
    Feature = if(lang=="EN") factor(c("Closing", "Hist+Tech"), levels=c("Closing", "Hist+Tech")) else factor(c("Kapanış", "Tarihsel+Teknik"), levels=c("Kapanış", "Tarihsel+Teknik")),
    Rate = c(100.0, 0.0)
  )
  title <- if(lang=="EN") "Graphic 7: Impact of Feature Enrichment\nAdding indicators kills the MC bias" else "Grafik 7: Özellik Zenginleştirmenin Etkisi\nİndikatör eklemek MC yanlılığını yok eder"
  ylabel <- if(lang=="EN") "MC Rate (%)" else "MC Yanlılık Oranı (%)"
  
  p <- ggplot(df, aes(x=Feature, y=Rate, fill=Feature)) + geom_bar(stat="identity", width=0.5) +
    scale_fill_manual(values=c("#C0392B", "#27AE60")) + coord_cartesian(ylim=c(0, 110)) +
    labs(title=title, x="", y=ylabel) + base_theme + theme(legend.position="none")
  
  save_plot("07_Feature_Set_Impact.png", p, lang)
}

# 8. Concept Drift (Points)
generate_plot_8 <- function(lang) {
  df <- data.frame(
    Metric = factor(c("LSTM Best", "LSTM Avg", "CNN Avg"), levels=rev(c("LSTM Best", "LSTM Avg", "CNN Avg"))),
    Old = c(60.04, 55.83, 56.79),
    New = c(57.56, 50.52, 49.55)
  )
  df_long <- pivot_longer(df, cols=c(Old, New), names_to="Period", values_to="Accuracy")
  df_long$Period <- factor(df_long$Period, levels=c("Old", "New"), labels=c("2018-2022", "2018-2026"))
  
  title <- if(lang=="EN") "Graphic 8: Concept Drift Evidence\nGlobal performance drop after 2022" else "Grafik 8: Concept Drift (Kavramsal Kayma) Kanıtı\n2022 sonrasında performans düşüşü"
  xlabel <- if(lang=="EN") "Accuracy (%)" else "Doğruluk (%)"
  
  p <- ggplot(df_long, aes(x=Accuracy, y=Metric, color=Period)) + 
    geom_line(aes(group=Metric), color="gray", size=1) +
    geom_point(size=5) +
    scale_color_manual(values=c(cols[1], cols[4])) +
    labs(title=title, y="", x=xlabel, color=if(lang=="EN") "Period" else "Dönem") + base_theme
  
  save_plot("08_Concept_Drift.png", p, lang)
}

# 9. Model Signal Quality
generate_plot_9 <- function(lang) {
  df <- data.frame(
    Metric = if(lang=="EN") factor(c("Accuracy", "F1", "Sens", "Spec"), levels=c("Accuracy", "F1", "Sens", "Spec")) else factor(c("Doğruluk", "F1", "Duyarlılık", "Özgüllük"), levels=c("Doğruluk", "F1", "Duyarlılık", "Özgüllük")),
    Score = c(80.21, 89.36, 84.00, 85.71)
  )
  title <- if(lang=="EN") "Graphic 9: AMZ LSTM Balanced Performance\nHigh Spec + High Sens = Real Power" else "Grafik 9: AMZ LSTM Dengeli Performansı\nYüksek Özgüllük + Yüksek Duyarlılık = Gerçek Güç"
  ylabel <- if(lang=="EN") "Score" else "Skor"
  
  p <- ggplot(df, aes(x=Metric, y=Score, fill=Metric)) + geom_bar(stat="identity", width=0.6) +
    scale_fill_viridis_d(option="B") + coord_cartesian(ylim=c(0, 100)) +
    labs(title=title, x="", y=ylabel) + base_theme + theme(legend.position="none")
  
  save_plot("09_Model_Signal_Quality.png", p, lang)
}

# 10. Confusion Matrix N=96
generate_plot_10 <- function(lang) {
  actuals <- if(lang=="EN") c("Act: Increase", "Act: Decrease") else c("Gerçek: Yükseliş", "Gerçek: Düşüş")
  preds <- if(lang=="EN") c("Pred: Increase", "Pred: Decrease") else c("Tahmin: Yükseliş", "Tahmin: Düşüş")
  
  df <- data.frame(
    Actual = rep(actuals, each=2),
    Predicted = rep(preds, times=2),
    Value = c(63, 3, 12, 18)
  )
  df$Actual <- factor(df$Actual, levels=rev(actuals))
  df$Predicted <- factor(df$Predicted, levels=preds)
  
  title <- if(lang=="EN") "Graphic 10: AMZ LSTM Confusion Matrix (N=96)\n77/96 Pooled Correct Predictions" else "Grafik 10: AMZ LSTM Karmaşıklık Matrisi (N=96)\n77/96 Havuzlanmış Doğru Tahmin"
  
  p <- ggplot(df, aes(x=Predicted, y=Actual, fill=Value)) + geom_tile(color="white", size=1) +
    geom_text(aes(label=Value), size=12, fontface="bold", color="white") +
    scale_fill_gradient(low="#1F618D", high="#154360") +
    labs(title=title, x="", y="") + base_theme + theme(legend.position="none")
  
  save_plot("10_Confusion_Matrix_Final.png", p, lang)
}

cat("Generating all plots internally via R script...\n")
for(lang in c("EN", "TR")) {
  generate_plot_1(lang); generate_plot_2(lang); generate_plot_3(lang)
  generate_plot_4(lang); generate_plot_5(lang); generate_plot_6(lang)
  generate_plot_7(lang); generate_plot_8(lang); generate_plot_9(lang)
  generate_plot_10(lang)
}
cat("Rendered fully!\n")
