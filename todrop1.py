# Senior Data Scientist Interview Questions & Answers (Concise)

## Question 1: Explain the bias-variance tradeoff and how it manifests differently in high-dimensional versus low-dimensional settings. How would you diagnose which problem you're facing in production?

**Answer:**

The bias-variance tradeoff describes how prediction error decomposes into bias (underfitting from oversimplified models), variance (overfitting from excessive sensitivity to training data), and irreducible error, with total error equaling bias² + variance + irreducible error.

In low-dimensional settings, you see a classic U-shaped curve with a clear optimal complexity point. In high-dimensional settings, variance amplifies exponentially due to the curse of dimensionality, spurious correlations become common, and the "double descent" phenomenon can occur where performance improves again after interpolation.

To diagnose in production, plot learning curves where high bias shows parallel training and validation errors with a gap, while high variance shows large gaps between low training error and high validation error. Test whether simpler or more complex models help, check cross-validation stability across folds, examine feature importance stability, and look for systematic residual patterns indicating bias.

---

## Question 2: Explain why batch normalization works. What are its limitations, and what alternatives exist for sequence models or small batch sizes?

**Answer:**

Batch normalization works by smoothing the loss landscape enabling higher learning rates, reducing internal covariate shift, and providing regularization through batch statistics noise. It normalizes as BN(x) = γ(x - μ_batch)/σ_batch + β.

Limitations include failure with small batches (< 16-32) due to noisy statistics, train-test discrepancy between batch and running statistics, problems with variable-length sequences, and synchronization overhead in distributed training.

Alternatives include Layer Normalization (normalizes per sample across features, standard for transformers/RNNs), Group Normalization (normalizes within channel groups, batch-independent for vision tasks), Instance Normalization (per-sample per-channel for GANs/style transfer), and Weight Normalization (reparameterizes weights directly without batch dependency).

---

## Question 3: You need to join two massive datasets where one has 100 billion rows. The join is causing memory issues and taking hours. What optimization strategies would you employ?

**Answer:**

Key strategies include using broadcast joins if one dataset is small (< 1GB), applying partition pruning with WHERE clauses before joining, and pre-partitioning both datasets on the join key using bucketing to co-locate matching records.

Address data skew with salting by adding random suffixes to hot keys. Use sort-merge joins by pre-sorting on join keys, store data in columnar formats (Parquet/ORC) to read only needed columns, and apply Bloom filters to pre-filter candidates.

Process incrementally by joining only new/changed records if possible, consider approximate joining methods for non-exact matches, and optimize execution plans by adjusting spark.sql.shuffle.partitions and increasing executor memory. Always check for data skew first as a few hot keys with massive records often cause the bottleneck.

---

## Question 4: A stakeholder claims your model is biased. How would you investigate this claim mathematically, identify sources of bias, and mitigate them while maintaining model performance?

**Answer:**

First, define bias mathematically using disparate impact (comparing P(Ŷ=1|A=a) across protected attributes), equalized odds (equal TPR/FPR across groups), or calibration (consistent P(Y=1|Ŷ=p, A=a) across groups).

Investigate by analyzing class distribution across protected groups, checking feature correlations with protected attributes, identifying label bias, and ensuring sufficient representation. Measure fairness with confusion matrices per demographic, calibration plots by subgroup, feature importance differences, and threshold analysis.

Identify bias sources including training data bias (underrepresentation, biased labels), feature bias (proxy variables), algorithm bias (majority class favoritism), or measurement bias (different error costs across groups).

Mitigate through pre-processing (reweighting/resampling underrepresented groups, removing proxies), in-processing (fairness constraints as regularization, adversarial debiasing, multi-objective optimization), or post-processing (group-specific thresholds, calibration adjustment per group). Monitor fairness metrics alongside accuracy in production and conduct regular audits. Note that some fairness metrics are mathematically incompatible, so choose based on business context and legal requirements.
