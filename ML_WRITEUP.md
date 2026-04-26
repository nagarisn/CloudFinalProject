# ML Models Write-Up (Requirement #1)

## i. Linear Regression
Linear Regression models the relationship between a continuous target and one or more predictors as a weighted linear combination, fit by minimizing squared error. It is fast, fully interpretable through its coefficients, and serves as a strong baseline. Its main weakness is the assumption of linearity and additivity, so it underfits when interactions or non-linear effects dominate.

## ii. Random Forest
Random Forest is an ensemble of decision trees, each trained on a bootstrap sample of rows and a random subset of features; predictions are averaged (regression) or voted (classification). Because trees split on thresholds, the model captures non-linearities and interactions automatically, is robust to outliers, and provides feature-importance scores. It costs more memory and is harder to interpret than a single tree.

## iii. Gradient Boosting
Gradient Boosting builds trees sequentially, each new tree fit to the residual errors of the prior ensemble using gradient descent on a loss function. It typically achieves the best accuracy on tabular data but is sensitive to learning rate and tree depth and can overfit without early stopping or regularization.

## Selected Model for CLV
We use **Linear Regression** as the primary CLV predictor (interpretable coefficients showing how basket count, units, distinct products, and average spend drive lifetime value), with a **Random Forest** comparison reported for R². Implementation: `ml_models.compute_clv` exposed at `GET /ml/clv`.

## Mapping to Requirements
- **Req 1 (write-up):** this document.
- **Req 7 (Basket Analysis ML):** association-rule mining (support / confidence / lift) over commodity baskets — `GET /ml/basket`. Cross-sell candidates are pairs with lift > 1.
- **Req 8 (Churn Prediction):** Gradient Boosting classifier (primary) + Logistic Regression baseline; label = no purchase in last 90 days. Returns model accuracy, feature importance, and top at-risk households — `GET /ml/churn`.
