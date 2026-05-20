# Customer Churn Model Evaluation

## Model

```text
Algorithm: Gradient Boosting Classifier
Target: is_churned
Dataset: Telco Customer Churn
ROC-AUC: 0.8435
Selected threshold: 0.28
```

## Threshold 0.50

```text
Precision churn: 0.6713
Recall churn: 0.5134
F1 churn: 0.5818
```

Confusion matrix:

```text
[[941  94]
 [182 192]]
```

Classification report:

```text
              precision    recall  f1-score   support

           0       0.84      0.91      0.87      1035
           1       0.67      0.51      0.58       374

    accuracy                           0.80      1409
   macro avg       0.75      0.71      0.73      1409
weighted avg       0.79      0.80      0.80      1409

```

## Selected Threshold 0.28

```text
Precision churn: 0.5315
Recall churn: 0.7888
F1 churn: 0.6351
```

Confusion matrix:

```text
[[775 260]
 [ 79 295]]
```

Classification report:

```text
              precision    recall  f1-score   support

           0       0.91      0.75      0.82      1035
           1       0.53      0.79      0.64       374

    accuracy                           0.76      1409
   macro avg       0.72      0.77      0.73      1409
weighted avg       0.81      0.76      0.77      1409

```

## Business Interpretation

The selected threshold improves churn recall, helping the business identify more at-risk customers for retention campaigns. The trade-off is lower precision, meaning some customers flagged as high risk may not churn.

Key churn risk signals from EDA:

```text
- Month-to-month contract
- Short tenure
- High monthly charges
- Electronic check payment
- Lack of support services such as online security or tech support
```
