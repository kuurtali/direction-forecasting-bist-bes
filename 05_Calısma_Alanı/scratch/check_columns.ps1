# This script would normally read the raw data files used for training/testing.
# Since I don't have the labels easily accessible in the results CSVs (only Accuracy/Sens),
# I can verify using Sens/Spec if they are MC.
# But for non-MC, it's harder to get the exact counts without the label files.
# However, I can check the "Out" totals.

# Let's check the labels in the results files.
# Oh, some result files have Up/Down counts in them? No, only metrics.
# Wait, let's look at the results CSV headers again.

$csv = Import-Csv "c:\Users\Kurt\Desktop\PROJE_ALL\2018-2026 çıktılar\LSTM_sonuclar_FINAL.csv"
$csv[0] | Get-Member -MemberType NoteProperty | Select Name
