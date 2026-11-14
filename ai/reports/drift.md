# Concept drift: train sớm vs train lại gần đây (test trên giai đoạn muộn nhất)

| pond     | early   |   early_fish_cm |   early_do | recent   |   recent_fish_cm |   recent_do | test   |   test_fish_cm |   test_do |
|:---------|:--------|----------------:|-----------:|:---------|-----------------:|------------:|:-------|---------------:|----------:|
| IoTpond1 | 19/06   |             7.4 |       8.61 | 24/07    |             17.9 |        5.22 | 09/08  |           22   |      4.33 |
| IoTPond3 | 19/06   |             7.1 |       9.17 | 15/08    |             21.5 |        4.84 | 27/08  |           26.3 |      4.64 |
| IoTPond4 | 19/06   |             7.2 |       9.32 | 09/08    |             24.1 |        3.69 | 27/08  |           28.4 |      1.81 |
| IoTPond6 | 22/06   |             8.2 |       9.91 | 28/08    |             24.8 |        0.56 | 15/09  |           29.2 |      5.53 |

## Isolation Forest trên dữ liệu muộn chưa chèn sự cố

| train   |   iforest_alarm_rate_clean |   mean_anomaly_clean |
|:--------|---------------------------:|---------------------:|
| early   |                      0.03  |                0.303 |
| recent  |                      0.011 |                0.112 |

## Chỉ số khi có sự cố chèn (trung bình seed [1, 2, 3])

|                          |   precision |   recall |    f1 |   false_alarms_per_day |
|:-------------------------|------------:|---------:|------:|-----------------------:|
| ('fuzzy_only', 'early')  |       0.31  |    0.589 | 0.405 |                  1.967 |
| ('fuzzy_only', 'recent') |       0.311 |    0.558 | 0.398 |                  2.017 |
| ('hybrid', 'early')      |       0.286 |    0.643 | 0.395 |                  2.63  |
| ('hybrid', 'recent')     |       0.311 |    0.558 | 0.398 |                  2.033 |
| ('iforest', 'early')     |       0.295 |    0.13  | 0.18  |                  0.917 |
| ('iforest', 'recent')    |       0.11  |    0.019 | 0.033 |                  0.633 |
| ('threshold', 'early')   |       0.157 |    0.693 | 0.255 |                  1.933 |
| ('threshold', 'recent')  |       0.157 |    0.693 | 0.255 |                  1.933 |
