# Evaluation

Track model quality separately for each task.

- Detection: precision, recall, F1
- Classification: macro-F1 and confusion matrix using the selected IMD intensity classes
- Intensity: MAE/RMSE for wind speed and pressure where labels are available
- Track: mean geodesic position error at +6/+12/+24/+48h
- Calibration: forecast uncertainty coverage/error relationship

Always report results on storms that were not present in training. Avoid random frame-level splitting.
