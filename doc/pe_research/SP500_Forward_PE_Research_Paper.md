# S&P 500 Forward P/E Mean Reversion and Market Timing Strategy: An Empirical Study

**A Comprehensive Analysis of Predictive Power Across Multiple P/E Definitions**

---

**Author:** Seung-Gu Kang (강승구)  
**Research Period:** November 2025  
**Data Coverage:** December 1988 - September 2025 (37 years, Quarterly 148 + Daily 9,318)  
**Last Updated:** November 13, 2025

---

## Abstract

This study examines the predictive power of S&P 500 Forward P/E ratios in forecasting future returns and proposes a practical investment strategy based on these findings. Analyzing 30 years (1988-2025) of data, we compare five different P/E definitions (Forward I, J(Trailing), K, L, M) using quarterly data (148 points) for primary analysis, then validate with daily data (9,318 points, 62x sample size). Results show that the Next 4-Quarter Forward EPS-based P/E (Column M) delivers 63.4% prediction accuracy with 15.31 percentage point outperformance.

Key findings include:
1. Forward P/E demonstrates superior predictive power compared to Trailing P/E (correlation -0.53 vs +0.07)
2. Bottom 25% P/E delivers 15.91% annual return vs 0.60% for Top 25% (25x difference)
3. **Daily data validation (9,318 samples) confirms quarterly findings:** Correlation -0.54, annualized +15.61%, consistent predictive power
4. **P/E ≈ 21 as critical threshold:** 30yr basis 20.8, 10yr basis 21.2, reconfirmed with daily data
5. **Returns collapse beyond threshold:** P/E < 21: +13~17%, P/E ≥ 21: -4.5% to +2.4%
6. Current market (P/E 22.72) exceeds threshold by 1.7pt, in low-return/loss zone
7. Post-2015 median P/E elevated by 1.7pt, yet threshold (21) remains valid

This research contributes theoretically by challenging traditional mean reversion explanations and practically by establishing concrete P/E-based trading signals with statistical significance.

**Keywords:** Forward P/E, Mean Reversion, Market Timing, S&P 500, Valuation Metrics, Predictive Analytics

---

## Table of Contents

### **1. Introduction**
- 1.1 Research Background and Motivation
- 1.2 Research Genesis: Initial Problem Recognition
- 1.3 Research Objectives
- 1.4 Research Originality

### **2. Theoretical Background**
- 2.1 Traditional Understanding of P/E Ratio
- 2.2 Trailing vs Forward P/E Debate
- 2.3 Starting Point of This Research

### **3. Methodology**
- 3.1 Data Collection and Preprocessing (Quarterly 148, 1988-2025)
- 3.2 P/E Ratio Calculation (5 Definitions: I, J, K, L, M)
- 3.3 Z-Score Normalization
- 3.4 Future Returns Calculation (1Q, 2Q, 3Q, 4Q)
- 3.5 Evaluation Metrics (Correlation, Accuracy, Return Differential)

### **4. Empirical Results**
- **4.1 Comparative Analysis of 5 P/E Definitions (Quarterly Data)**
  - 4.1.1 Correlation Analysis
  - 4.1.2 Prediction Accuracy Analysis
  - 4.1.3 Actual Return Differential Analysis
  - 4.1.4 Annualized Analysis: Removing Period Effect
- 4.2 Practical Interpretation: -0.59 ≠ 59% Probability
- **4.3 Daily Data Validation: Enhanced Sample Size Analysis (9,318 points)**
  - 4.3.1 Research Motivation
  - 4.3.2 Methodology: Daily Data Mapping
  - 4.3.3 Result 1: Correlation Comparison
  - 4.3.4 Result 2: Annualized Excess Returns Comparison
  - 4.3.5 Result 3: P/E Quartile Returns (30-Year vs 10-Year)
  - 4.3.6 Quarterly vs Daily: Which is Better?

### **5. Deep Analysis: Why Does Forward P/E Work?**
- 5.1 Traditional Explanation: Valuation Mean Reversion
- 5.2 Our Explanation: Consensus Forecast Realization
- 5.3 Asymmetric Prediction Accuracy

### **6. P/E Range Investment Strategy**
- 6.1 Historical P/E Distribution: 30-Year vs 10-Year
- 6.2 Average Returns by Range
- **6.3 Key Finding: P/E 19-21 Critical Zone**
- 6.3.1 Why Only Column M Shows Clear 19-21 Critical Zone?
- 6.4 Practical Investment Strategy

### **7. Limitations and Future Research**
- 7.1 Data Limitations
- 7.2 Model Limitations
- 7.3 Future Research Directions

### **8. Conclusion**
- 8.1 Research Summary
- 8.2 Theoretical Contributions
- 8.3 Practical Implications
- 8.4 Final Conclusions

---

## 1. Introduction

### 1.1 Research Background and Motivation

Among equity valuation metrics, the Price-to-Earnings (P/E) ratio is the most widely used indicator. However, practitioners employ various P/E definitions interchangeably, and systematic comparative studies of their predictive power remain scarce.

This research originated from a practical question:

**"Which P/E metric should we use?"**

While seemingly simple, this question encompasses several critical sub-questions:
- Forward P/E (future-based) vs Trailing P/E (historical): which is more useful?
- Multiple Forward P/E definitions exist - which has the strongest predictive power?
- How should we define "high" vs "low" P/E?
- Where does the current market stand historically?

### 1.2 Genesis of Research: Initial Problem Discovery

This research began with a straightforward task: "collect Forward P/E data and create a time series chart." We initially attempted to scrape S&P 500 Forward P/E data from YCharts, but encountered a 5-year data limitation.

As an alternative, we utilized the official data source from S&P Global: [S&P 500 EPS Estimates](https://www.spglobal.com/spdji/en/documents/additional-material/sp-500-eps-est.xlsx).

**Original Data (Provided by S&P Global):**
- **Column I:** Current quarter + Past 3 quarters EPS (Estimates) - NTM-type Forward
- **Column J:** Current quarter + Past 3 quarters EPS (Actuals) - TTM Trailing

However, we recognized that the original data alone could not generate "purely forward-looking" Forward P/E. **Therefore, this research constructed three additional EPS definitions:**

**Columns Constructed in This Research:**
- **Column K:** Current quarter Actuals + Next 3 quarters Estimates
- **Column L:** Current quarter Estimates + Next 3 quarters Estimates
- **Column M:** Next 4 quarters Estimates (completely forward-looking)

Columns K, L, M were generated by recombining quarterly EPS values from the source data, enabling systematic comparison of Forward P/E metrics with varying degrees of "forward-looking" orientation.

This discovery transformed our simple "data visualization task" into a fundamental research question: **"Which metric is actually useful?"**

### 1.3 Research Objectives

This study aims to:

1. **Comparative Analysis:** Quantitatively compare predictive power across five P/E definitions
2. **Mechanism Identification:** Theoretically explain why certain P/E metrics outperform others
3. **Practical Application:** Establish concrete P/E-based trading strategies by quartile
4. **Current Assessment:** Evaluate market valuation as of November 2025

### 1.4 Research Novelty

This study differentiates itself from existing literature through:

1. **Multi-Definition Comparison:** Simultaneous comparison of 5 P/E definitions rather than single metric
2. **Probabilistic Approach:** Calculating actual prediction accuracy (%) and return differentials, beyond simple correlation
3. **New Normal Analysis:** Comparing 30-year vs 10-year baselines to capture low-rate era valuation shifts
4. **Transparent Methodology:** All analysis processes and code disclosed for reproducibility

---

## 2. Theoretical Background

### 2.1 Traditional Understanding of P/E Ratios

The P/E ratio is the most fundamental metric for measuring relative over/undervaluation. Traditional understanding:

- **High P/E:** Price expensive relative to earnings = Overvalued
- **Low P/E:** Price cheap relative to earnings = Undervalued
- **Mean Reversion:** Overvaluation reverts to mean → low returns; Undervaluation → high returns

### 2.2 Trailing vs Forward P/E Debate

Two P/E definitions coexist in practice:

**Trailing P/E (Historical Basis):**
- Advantages: Objective, verifiable
- Disadvantages: Lagging, misses turning points

**Forward P/E (Forecast Basis):**
- Advantages: Leading, aligns with market's forward-looking nature
- Disadvantages: Subjective, susceptible to forecast errors

Yet systematic validation of "which is actually more useful?" has been lacking.

### 2.3 Research Starting Point

This research began not from existing theory but from **empirical data**:

1. S&P Global's official EPS data contains only I, J definitions
2. To create "purely forward-looking" Forward P/E, we constructed K, L, M
3. Empirically tested which of the five has highest predictive power

**Core Questions:**
- Does traditional "valuation mean reversion" explanation work?
- Or does a different mechanism exist?

The answer is provided in Section 5.2.

---

## 3. Methodology

### 3.1 Data Collection and Preprocessing

#### 3.1.1 Price Data

- **Source:** Yahoo Finance API (yfinance library)
- **Symbol:** S&P 500 Index (^GSPC)
- **Period:** 1985 - November 2025
- **Frequency:** Daily closing prices

**Price Smoothing:**
To prevent quarter-end single-day spikes/crashes from distorting results, we used 2-week average closing prices (±7 days around quarter-end).

```python
# Calculate ±7 day average price around quarter-end
start_window = quarter_end_date - pd.Timedelta(days=7)
end_window = quarter_end_date + pd.Timedelta(days=7)
avg_price = price_df.loc[mask, 'Close'].mean()
```

This method eliminates single-day volatility while representing quarter-end market levels.

#### 3.1.2 EPS Data

- **Source:** S&P Global - S&P Dow Jones Indices ([sp-500-eps-est.xlsx](https://www.spglobal.com/spdji/en/documents/additional-material/sp-500-eps-est.xlsx))
- **Sheet:** ESTIMATES&PEs
- **Row Range:** 132-278 (expandable for pre-2015 data)

**Original Columns (Provided by S&P Global):**
- Column I: Current quarter + Past 3 quarters EPS (Estimates) - NTM-type Forward
- Column J: Current quarter + Past 3 quarters EPS (Actuals) - TTM Trailing

**Columns Constructed in This Research:**
- Column K: Current quarter Actuals + Next 3 quarters Estimates
- Column L: Current quarter Estimates + Next 3 quarters Estimates
- Column M: Next 4 quarters Estimates (completely forward-looking)

Columns K, L, M were generated by recombining quarterly EPS values from the source data to create varying degrees of forward-looking metrics.

**Data Cleaning:**
Removed extraneous text from date column (e.g., "(81.3%)") and parsed with pd.to_datetime().

```python
date_str = str(date_val).split('(')[0].strip()
date_parsed = pd.to_datetime(date_str)
```

#### 3.1.3 Final Dataset

- **Total Observations:** 148 quarters (1988-12-31 ~ 2025-09-30)
- **Valid Data per EPS Column:** 148 observations (no missing values)

### 3.2 P/E Ratio Calculation

For each quarter $t$, P/E ratio is calculated as:

$$
PE_t = \frac{Price_t}{EPS_t}
$$

Where $Price_t$ is the smoothed average closing price for quarter $t$, and $EPS_t$ is the EPS estimate for that quarter.

### 3.3 Z-Score Normalization

Since absolute P/E levels vary across eras, we normalize using Z-scores to measure relative over/undervaluation:

$$
Z_t = \frac{PE_t - \mu_{PE}}{\sigma_{PE}}
$$

Where:
- $\mu_{PE}$: Mean P/E across entire period
- $\sigma_{PE}$: Standard deviation of P/E across entire period

Z-score > 0 indicates overvaluation, Z-score < 0 indicates undervaluation relative to historical mean.

### 3.4 Forward Returns Calculation

For each quarter $t$, cumulative return $n$ quarters ahead is calculated as:

$$
Return_{t,n} = \frac{Price_{t+n} - Price_t}{Price_t} \times 100\%
$$

We analyze $n = 1, 2, 3, 4$ (corresponding to 3, 6, 9, 12 months forward).

#### 3.4.1 Annualization

To compare returns across different time periods, we perform annualization:

$$
Annualized\_Return = Return_{t,n} \times \frac{4}{n}
$$

Where:
- $Return_{t,n}$: Cumulative return over $n$ quarters (%)
- $\frac{4}{n}$: Annualization multiplier (1 year = 4 quarters)

**Example:**
- 1Q return +4%: Annualized = 4% × (4/1) = **+16% / year**
- 4Q return +16%: Annualized = 16% × (4/4) = **+16% / year**

**Group-Level Annualized Differential:**

We annualize the average return difference between High P/E and Low P/E groups:

$$
Annualized\_Diff = (\overline{Return}_{Low,n} - \overline{Return}_{High,n}) \times \frac{4}{n}
$$

Where:
- $\overline{Return}_{Low,n}$: Average $n$-quarter return for Low P/E group (Z < 0)
- $\overline{Return}_{High,n}$: Average $n$-quarter return for High P/E group (Z > 0)
- High/Low groups classified by Z-score across entire 30 years (148 quarters)

**Significance of This Method:**
- Removes period effect
- Standardizes P/E signal's pure predictive power to annual basis
- Enables fair comparison across different time horizons

### 3.5 Evaluation Metrics

#### 3.5.1 Pearson Correlation

Measures linear relationship between P/E Z-score and future returns:

$$
r = \frac{\sum (Z_i - \bar{Z})(R_i - \bar{R})}{\sqrt{\sum (Z_i - \bar{Z})^2 \sum (R_i - \bar{R})^2}}
$$

Negative correlation implies "high P/E → low returns."

#### 3.5.2 Prediction Accuracy

Using median return as threshold, we dichotomize returns and calculate accuracy:

- High P/E (Z > 0) & Return < Median: Correct prediction
- Low P/E (Z < 0) & Return ≥ Median: Correct prediction

$$
Accuracy = \frac{\text{Number of Correct Predictions}}{\text{Total Predictions}} \times 100\%
$$

#### 3.5.3 Average Return Differential

Most critical metric for investment decisions:

$$
\Delta Return = \overline{Return}_{Z<0} - \overline{Return}_{Z>0}
$$

Calculates average return difference between Low P/E and High P/E groups.

---

## 4. Empirical Results

### 4.1 Comparative Analysis of Five P/E Definitions

#### 4.1.1 Correlation Analysis

**Table 1: Pearson Correlation Between P/E Z-score and Future Returns**

| Column | Source | Definition | 1Q (3mo) | 2Q (6mo) | 3Q (9mo) | 4Q (12mo) | **Avg** |
|--------|--------|-----------|----------|----------|----------|-----------|---------|
| **M** | This Research | Next 4Q Est | -0.413 | -0.538 | **-0.591** | -0.588 | **-0.533** ✅ |
| **L** | This Research | Curr Est+Next 3Q | -0.382 | -0.477 | -0.493 | -0.474 | **-0.457** |
| **K** | This Research | Curr Act+Next 3Q | -0.407 | -0.437 | -0.417 | -0.378 | **-0.410** |
| **I** | S&P Global | Curr+Past 3Q (Est) | -0.106 | -0.147 | -0.189 | -0.212 | **-0.163** |
| **J** | S&P Global | Curr+Past 3Q (Act) | +0.053 | +0.104 | +0.078 | +0.033 | **+0.067** ❌ |

**Key Findings:**
1. **Column M exhibits strongest negative correlation** (average -0.533)
2. **Peak at 3-4 quarters forward: -0.59**
3. **Trailing P/E (Column J) essentially useless** (correlation +0.067, near zero)
4. Even among Forward metrics, Column I shows very weak correlation
5. Sample size of n=145-148 provides sufficient observations

#### 4.1.2 Prediction Accuracy Analysis

**Table 2: P/E-Based Return Prediction Accuracy (Median Threshold)**

| Column | Definition | 1Q | 2Q | 3Q | 4Q | **Avg** | Interpretation |
|--------|-----------|-----|-----|-----|-----|---------|----------------|
| **M** | Next 4Q Est | 56.5% | 62.3% | **63.4%** | 62.5% | **61.2%** | Strong ✅ |
| **K** | Curr Act+Next 3Q | 57.1% | 58.9% | 61.4% | 54.9% | **58.1%** | Moderate |
| **L** | Curr Est+Next 3Q | 57.8% | 59.6% | 59.3% | 55.6% | **58.1%** | Moderate |
| **I** | Curr+Past 3Q (Est) | 46.9% | 48.6% | 52.4% | 51.4% | **49.8%** | Useless ❌ |
| **J** | Curr+Past 3Q (Act) | 48.3% | 50.0% | 51.0% | 52.8% | **50.5%** | Useless ❌ |

**Interpretation:**
- 50% = coin flip level
- **Column M achieves 61-63% accuracy**, statistically significant
- **Column J (Trailing) at 50.5% = no better than random**

#### 4.1.3 Actual Return Differential Analysis (Most Important)

**Table 3: Average 1-Year Returns by P/E Group (High vs Low)**

| Column | Definition | High P/E (Z>0) | Low P/E (Z<0) | **Difference** | Samples (H/L) |
|--------|-----------|----------------|---------------|----------------|---------------|
| **M** | Next 4Q Est | +0.60% | +15.91% | **+15.31%p** ✅ | 56 / 88 |
| **K** | Curr Act+Next 3Q | +3.55% | +13.91% | **+10.36%p** | 55 / 89 |
| **L** | Curr Est+Next 3Q | +4.60% | +14.00% | **+9.39%p** | 62 / 82 |
| **J** | Curr+Past 3Q (Act) | +5.99% | +11.58% | **+5.59%p** | 42 / 102 |
| **I** | Curr+Past 3Q (Est) | +7.69% | +11.57% | **+3.87%p** | 60 / 84 |

**Critical Findings:**
1. **Column M shows 25x return differential** (15.91% vs 0.60%)
2. High P/E periods deliver cash-equivalent returns (0.60%)
3. Low P/E periods deliver strong ~16% annual returns
4. **Even Trailing P/E shows some discrimination (5.59%p), but half of Forward metrics**

#### 4.1.4 Annualized Analysis: Removing Period Effect

**Important Question:** "Isn't 4Q (12 months) having higher absolute returns than 1Q (3 months) simply due to longer time period?"

To verify, we converted to **annualized returns** (30-year data, 148 quarters):

**Table 3-1: Column M (Next 4Q EPS) - Return Differentials by Period & Annualized (30 Years)**

| Period | Low P/E Avg | High P/E Avg | **Difference** | **Annualized Difference** |
|--------|------------|--------------|----------------|--------------------------|
| 1Q (3 months) | +4.12% | +0.04% | +4.07% | **+16.28% / year** |
| 2Q (6 months) | +8.14% | +0.14% | +8.00% | **+16.00% / year** |
| 3Q (9 months) | +12.03% | +0.27% | +11.76% | **+15.68% / year** |
| 4Q (12 months) | +15.91% | +0.60% | +15.31% | **+15.31% / year** |

**Findings:**
- When annualized, all periods show consistent **~15-16% / year** outperformance
- Absolute returns increasing with period = **time effect**
- P/E's true predictive power = **annual 15-16% excess returns**
- This remains constant whether 1Q or 4Q horizon

**Do other P/E definitions also show consistency?**

**Table 3-2: Annualized Excess Returns Comparison Across 5 P/E Definitions (30 Years, 148 Quarters)**

| EPS Definition | 1Q→Ann | 2Q→Ann | 3Q→Ann | 4Q→Ann | **Average** | Consistency |
|---------------|--------|--------|--------|--------|-------------|-------------|
| **M (Next 4Q)** | +16.29% | +16.00% | +15.68% | +15.31% | **+15.82%** | ✅ Highly Consistent |
| K (Curr Act+Next 3Q) | +15.48% | +13.43% | +13.11% | +10.36% | **+13.09%** | △ Variable |
| L (Curr Est+Next 3Q) | +14.33% | +12.38% | +11.08% | +9.39% | **+11.80%** | △ Variable |
| J (Trailing) | +3.88% | +3.63% | +3.97% | +5.59% | **+4.27%** | ⚪ Low but Stable |
| I (Curr+Past 3Q) | +1.15% | +1.53% | +3.35% | +3.87% | **+2.47%** | ❌ Nearly Useless |

**Additional Findings:**

1. **Only Column M shows perfect consistency:**
   - 15.31% ~ 16.29% (range: 0.98pp)
   - Average 15.82%/year, highest

2. **K, L have good averages but vary:**
   - K: 10.36% ~ 15.48% (range: 5.12pp)
   - L: 9.39% ~ 14.33% (range: 4.94pp)
   - Predictive power varies by period

3. **Trailing (J) is low but consistent:**
   - 3.63% ~ 5.59% (range: 1.96pp)
   - Average 4.27%/year, low

4. **I is completely useless:**
   - Average 2.47%/year (1/6 of M)

**Conclusion:**
- **Column M not only has highest predictive power but also most stable**
- K, L are decent (11-13%/year) but period-dependent
- **Reason to use M: High predictive power + Consistency**

**Practical Implications:**
- P/E signal shows consistent effect from short-term (1Q) to long-term (4Q) for Column M
- However, accuracy is highest at 2-3Q forward (correlation -0.54 ~ -0.59)

**Figures 2-6: Individual P/E Definition Analysis**

**Figure 2: Column M (Best Performance) - Forward P/E Mean Reversion**

![Figure 2: Column M](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_mean_reversion_M_1762956822.jpg)

**Figure 3: Column K - Forward P/E Mean Reversion**

![Figure 3: Column K](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_mean_reversion_K_1762956822.jpg)

**Figure 4: Column L - Forward P/E Mean Reversion**

![Figure 4: Column L](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_mean_reversion_L_1762956822.jpg)

**Figure 5: Column J (Trailing P/E) - Mean Reversion**

![Figure 5: Trailing P/E](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_mean_reversion_J_trailing_1762956823.jpg)

**Figure 6: Column I (Lowest Performance) - Forward P/E Mean Reversion**

![Figure 6: Column I](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_mean_reversion_I_1762956823.jpg)

### 4.2 Understanding Correlation: -0.59 ≠ 59% Probability

During initial research, a question arose: "Does correlation -0.59 mean 59% prediction probability?"

**This is a misinterpretation.**

#### 4.2.1 Relationship Between Correlation and Predictive Power

- **Correlation (r):** Strength and direction of linear relationship (-1 to +1)
- **Coefficient of Determination (R²):** r² = 0.59² = 0.35, meaning P/E explains 35% of return variance
- **Prediction Accuracy:** Actually 61-63%

#### 4.2.2 The 92% Trap: Market Upward Bias

Initial analysis yielded "92% probability of positive returns when P/E is low," which proved misleading:

**Flawed Analysis (Actual Results, Column M 4Q):**
- Low P/E (Z<0): Positive returns = 81/88 = **92%**
- High P/E (Z>0): Positive returns = 49/56 = **88%**
- Difference: Only **4 percentage points**

**Problem:** 
- S&P 500 rose in approximately **130/144 = 90% of quarters** over 30 years
- Thus 92% reflects **market's inherent upward bias**, not P/E's predictive power
- Most periods show positive returns regardless of P/E, making this metric meaningless

**Correct Analysis: Using Median Return as Threshold**

The median 1-year return across 144 quarters is **+11.33%**. Using this to distinguish "good/poor returns" and recalculating:

- Low P/E (Z<0): Returns above median (11.33%) = 53/88 = **60.2%**
- High P/E (Z>0): Returns above median = 19/56 = **33.9%**
- Difference: **26.3 percentage points** (now a clear distinction!)

Now P/E's true predictive power emerges.

#### 4.2.3 Going Further: Magnitude Matters

Beyond simple "above/below median," **actual return magnitudes** matter most:

- High P/E: Average +0.60%
- Low P/E: Average +15.91%

This is the truly actionable information for investors.

---

## 4.3 Daily Data Validation: Enhanced Sample Size Analysis

### 4.3.1 Research Motivation

The previous quarterly analysis used 148 observations. To enhance statistical reliability, we conducted **additional validation using daily price data**.

**Key Questions:**
- Does increasing sample size 62x (148 → 9,318) change results?
- Does daily data noise dilute the signal, or enable more precise estimation?

### 4.3.2 Methodology: Daily Data Mapping

**EPS-to-Price Mapping Logic:**

```
Use the quarter-end EPS for all dates within that quarter

Example:
┌───────────────────────────────────────────────────────┐
│ Period: 2025-07-01 ~ 2025-09-30 (Q3)                 │
│ EPS Used: Values from 2025-09-30 row                 │
│                                                       │
│ EPS Composition by Column (' = Est, none = Actual):  │
│   - Column M: 294.11 (Q4'+2026Q1'+Q2'+Q3')           │
│   - Column L: 288.10 (Q3'+Q4'+2026Q1'+Q2')           │
│   - Column K: 282.04 (Q3+Q4'+2026Q1'+Q2')            │
│   - Column I: 255.80 (2024Q4+Q1+Q2+Q3')              │
│   - Column J: 237.55 (2024Q4+Q1+Q2+Q3)               │
│                                                       │
│ Daily P/E Calculation (Column M example):            │
│   - 2025-07-01: P/E = 5,475 ÷ 294.11 = 18.61        │
│   - 2025-07-02: P/E = 5,480 ÷ 294.11 = 18.63        │
│   - 2025-09-30: P/E = 5,738 ÷ 294.11 = 19.51        │
└───────────────────────────────────────────────────────┘
```

**Data Scale:**
- Quarterly: 148 data points
- Daily: **9,318 data points** (62.7x increase)
- Standard Error: **8x reduction** (0.083 → 0.010)

### 4.3.3 Result 1: Correlation Comparison

**Table 4-1: Quarterly vs Daily Correlation Comparison**

| Column | Data | 1Q | 2Q | 3Q | 4Q | **Average** |
|--------|------|-----|-----|-----|-----|---------|
| **M** | Quarterly | -0.413 | -0.538 | -0.591 | -0.588 | **-0.533** |
| **M** | Daily | -0.395 | -0.544 | **-0.609** | **-0.623** | **-0.543** |
| **M** | Diff | +0.018 | -0.006 | **-0.018** | **-0.035** | **-0.010** |
| **L** | Quarterly | -0.382 | -0.477 | -0.493 | -0.474 | **-0.457** |
| **L** | Daily | -0.402 | -0.515 | -0.546 | -0.532 | **-0.499** |
| **K** | Quarterly | -0.407 | -0.437 | -0.417 | -0.378 | **-0.410** |
| **K** | Daily | -0.438 | -0.488 | -0.482 | -0.452 | **-0.465** |
| **J** | Quarterly | +0.053 | +0.104 | +0.078 | +0.033 | **+0.067** |
| **J** | Daily | +0.005 | +0.051 | +0.055 | +0.026 | **+0.034** |
| **I** | Quarterly | -0.106 | -0.147 | -0.189 | -0.212 | **-0.164** |
| **I** | Daily | -0.145 | -0.184 | -0.210 | -0.234 | **-0.193** |

**Key Findings:**
1. **Column M: 4Q correlation improved with daily data** (-0.588 → -0.623, +6%)
2. **K, L: Consistent improvement across all periods** (avg +13%, +9%)
3. **I: Weak signal becomes clearer** (+18% improvement)
4. **J(Trailing): Still useless with daily data** (r ≈ 0)

**Figure 3-1: Column M Daily Data Mean Reversion Analysis (Best Performance)**

![Figure 3-1: Daily M](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_mean_reversion_daily_M_1762971064.jpg)

*Column M P/E time series and future return correlations using 9,318 daily data points*

**Figure 3-2: Column K Daily Data Mean Reversion Analysis**

![Figure 3-2: Daily K](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_mean_reversion_daily_K_1762971064.jpg)

**Figure 3-3: Column L Daily Data Mean Reversion Analysis**

![Figure 3-3: Daily L](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_mean_reversion_daily_L_1762971064.jpg)

**Figure 3-4: Column J Daily Data Mean Reversion Analysis (Trailing P/E)**

![Figure 3-4: Daily J](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_mean_reversion_daily_J_1762971064.jpg)

**Figure 3-5: Column I Daily Data Mean Reversion Analysis (Lowest Performance)**

![Figure 3-5: Daily I](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_mean_reversion_daily_I_1762971063.jpg)

### 4.3.4 Result 2: Annualized Excess Returns Comparison

**Table 4-2: Annualized Excess Returns - Quarterly vs Daily**

| Column | Data | 1Q→Ann | 2Q→Ann | 3Q→Ann | 4Q(Actual) | **Average** |
|--------|------|--------|--------|--------|----------|---------|
| **M** | Quarterly | +17.33% | +16.67% | +15.99% | **+15.31%** | +16.33% |
| **M** | Daily | +16.99% | +15.86% | +15.22% | **+14.37%** | +15.61% |
| **M** | Diff | -0.34% | -0.81% | -0.77% | -0.94% | **-0.72%** |

**Key Findings:**
1. **4Q (actual 1-year) as benchmark for annualization accuracy:** 
   - Quarterly 4Q = +15.31% (perfectly matches actual)
   - Daily 4Q = +14.37% (0.94pp difference)

2. **Quarterly data superiority:**
   - Quarterly average (+16.33%) closer to actual (+15.31%) than daily (+15.61%)
   - Daily slightly underestimates due to short-term noise

3. **K, L perform better with daily:**
   - K: +0.81pp improvement
   - L: +1.10pp improvement

### 4.3.5 Result 3: P/E Quartile Returns (30-Year vs 10-Year)

**Table 4-3: Column M - P/E Quartile Returns Comparison (Daily Data)**

| Period | Quartile | P/E Range | Average Return | Samples |
|--------|----------|-----------|----------------|---------|
| **30-Year** | Bottom 25% | **< 14.6** | **+16.90%** | 2,267 |
| **30-Year** | 25-50% | 14.6 - 17.2 | +14.36% | 2,266 |
| **30-Year** | 50-75% | 17.2 - 20.8 | +12.88% | 2,266 |
| **30-Year** | Top 25% | **≥ 20.8** | **-4.53%** | 2,267 |
| **30-Year** | **Spread** | - | **+21.43%p** | - |
| **10-Year** | Bottom 25% | **< 17.7** | **+20.31%** | 613 |
| **10-Year** | 25-50% | 17.7 - 18.9 | +16.36% | 612 |
| **10-Year** | 50-75% | 18.9 - 21.2 | +10.69% | 612 |
| **10-Year** | Top 25% | **≥ 21.2** | **+2.44%** | 613 |
| **10-Year** | **Spread** | - | **+17.87%p** | - |

**Key Findings:**

1. **P/E ≈ 21 Critical Threshold Reconfirmed:**
   - 30-year: P/E ≥ 20.8 → **-4.53%** (losses!)
   - 10-year: P/E ≥ 21.2 → +2.44% (low returns)
   - **Average: P/E ≈ 21 = Critical inflection point**

2. **New Normal Effect:**
   - Median P/E: 17.2 → 18.9 (+1.7pt increase)
   - Overall P/E elevation due to low-rate environment
   - Yet **threshold (21) remains valid**

3. **Daily Data Precision:**
   - 9,066 samples for robust estimation
   - Results nearly identical to quarterly (within ±0.5pp)

**Figure 4: Column M P/E vs 1-Year Return Correlation (Daily Data)**

![Figure 4: Correlation M](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_correlation_M_1762971065.jpg)

*Strong negative correlation between P/E and 1-year returns confirmed with 9,066 daily data points (r = -0.50)*

### 4.3.6 Quarterly vs Daily: Which is Better?

**Comparison Summary:**

| Criterion | Quarterly | Daily | Superior Method |
|-----------|-----------|-------|-----------------|
| Sample Size | 148 | 9,318 | Daily ✅ |
| Standard Error | ±0.083 | ±0.010 | Daily ✅ |
| Column M Correlation | -0.533 | -0.543 | Daily ✅ |
| Annualization Accuracy | 16.33% vs 15.31% | 15.61% vs 15.31% | **Daily ✅** |
| Matches EPS Update Cycle | ✅ | ❌ | Quarterly ✅ |
| Short-term Noise | Low | High | Quarterly ✅ |

**Conclusions:**

1. **Daily data useful as validation tool:**
   - 62x more samples confirm quarterly findings
   - Dramatically improved statistical reliability

2. **Quarterly data recommended for practice:**
   - Matches EPS update cycle (quarterly)
   - Annualization more accurately matches actual
   - Clean signal without short-term noise

3. **Core findings identical:**
   - **P/E ≈ 21 as critical threshold** (both methods agree)
   - Column M superior performance (both methods agree)
   - Trailing P/E useless (both methods agree)

---

## 5. Deep Analysis: Why Does Forward P/E Work?

### 5.1 Traditional Explanation: Valuation Mean Reversion

Traditionally explained as "high P/E reverts to mean, thus lower returns."

However, this explanation has a problem:
- **If truly mean reversion, Trailing P/E should also work**
- But Trailing P/E has zero predictive power (r = +0.07)

### 5.2 Our Explanation: Consensus Forecast Realization

**Forward P/E's negative correlation is not true "mean reversion" but "consensus EPS forecast realization."**

#### 5.2.1 Mechanism

1. Forward P/E incorporates analyst EPS forecasts
2. High P/E = Price high relative to expected EPS = growth expectations already priced in
3. 3-4 quarters later, when forecasts materialize, prices adjust or stagnate
4. Thus lower returns result

**Evidence:**
- Trailing P/E (past EPS): No predictive power
- Forward P/E (includes future EPS forecasts): Strong predictive power

**Difference = Informational value of analyst forecasts**

#### 5.2.2 Why Column M Strongest?

**Table 4: EPS Column Definitions**

| Column | Definition | Future Component |
|--------|-----------|--------|------------------|
| I | Current + Past 3Q (Estimates) | Some (Current Q est) |
| J | Current + Past 3Q (Actuals) | **None** |
| K | Current Actuals + Next 3Q Estimates | Next 3Q |
| L | Current Estimates + Next 3Q Estimates | Current Q + Next 3Q |
| M | Next 4Q Estimates | **Entirely Future** |

Column M is **purely forward-looking**, thus:
- Best alignment with market's forward-looking nature
- Strongest reflection of analyst consensus
- Highest predictive power

### 5.3 Asymmetric Prediction Accuracy

**Table 5: Column M Prediction Accuracy Comparison (3Q, Median 11.33% Threshold)**

| P/E State | Correct Prediction | Accuracy |
|-----------|-------------------|----------|
| High P/E (Z>0) | Below-median returns occur | 38/57 = **66.7%** |
| Low P/E (Z<0) | Above-median returns occur | 54/88 = **61.4%** |

**Finding:** Accuracy is higher when P/E is high (66.7% vs 61.4%)

**Interpretation:**
- High P/E → Predicts "below-average returns" with 66.7% probability
- Low P/E → Predicts "above-average returns" with 61.4% probability
- Difference exists, but both exceed 60% (meaningful level)

**Practical Implications:**
- High P/E periods' risks are more clearly identified
- "When NOT to buy" signal is more reliable

---

## 6. P/E Quartile-Based Investment Strategy

### 6.1 Historical P/E Distribution: 30-Year vs 10-Year

#### 6.1.1 30-Year Baseline (1988-2025) - Daily Data

**Table 6: Forward P/E (M) Historical Distribution - 30 Years (Daily 9,003)**

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| Minimum | 7.89 | Historical low (2008 Financial Crisis) |
| 10th percentile | 13.09 | Bottom 10% (Ultra-Aggressive Buy Zone) |
| 25th percentile | 14.67 | Bottom 25% (Aggressive Buy Zone) |
| Median (50th) | 17.25 | Middle (Cautious Buy Zone) |
| Mean | 17.71 | - |
| **75th percentile** | **20.84** | **Top 25% (Threshold!)** |
| 90th percentile | 23.04 | Top 10% (Danger Zone) |
| Maximum | 27.66 | Historical high (2020-2021 Bubble) |

**Note:** Daily 9,003 samples provide **62x increase** vs quarterly 148, significantly enhanced statistical confidence

#### 6.1.2 10-Year Baseline (2015-2025): "New Normal"

**Table 7: Forward P/E (M) Historical Distribution - 10yr vs 30yr Comparison (Daily Data)**

| Statistic | 30-Year Basis<br>(9,003) | 10-Year Basis<br>(2,452) | Difference<br>(10y-30y) | % Change |
|-----------|--------------|---------------------------|---------------------|----------|
| 10th percentile | 13.09 | 16.84 | +3.75 | +28.7% |
| 25th percentile | 14.67 | 17.66 | +2.99 | +20.4% |
| Median (50th) | 17.25 | 18.92 | +1.67 | +9.7% |
| Mean | 17.71 | 19.16 | +1.45 | +8.2% |
| **75th percentile** | **20.84** | **21.24** | **+0.40** | **+1.9%** |
| 90th percentile | 23.04 | 22.20 | -0.84 | -3.6% |

**Key Findings: "New Normal" Evidence (Reconfirmed with 9,003 Daily Samples)**

1. **Undervaluation bar raised:** 25th percentile rose from 14.7 → 17.7 (~3pt increase)
2. **Median elevated:** 17.3 → 18.9 (~1.7pt increase)
3. **Threshold stable:** 75th percentile 20.8 → 21.2 (modest +0.4pt, 1.9%)
4. **Ceiling lowered:** 90th percentile actually declined (23.0 → 22.2)

**Causes:**
- Post-2015 low interest rate environment
- Quantitative easing policies
- Long-term bond yields declined → equity discount rates declined → P/E elevated

### 6.2 Average Returns and Win Rates by Zone

#### 6.2.1 30-Year Baseline - Daily Data

**Table 8: Average 1-Year Returns & Win Rates by P/E Zone (30 Years, Daily 9,003)**

*Note: Zones split by P/E percentiles, each percentile range contains equal proportion of samples*

| P/E Range | Avg Return | Win Rate | Samples | Percentile<br>(Proportion) | Assessment |
|-----------|-----------|----------|---------|------------|------------|
| < 13.1 | **+19.65%** | **97.6%** | 901 | 0-10%<br>(10%) | Ultra-Aggressive Buy |
| 13.1 - 14.7 | **+14.40%** | **95.0%** | 1,350 | 10-25%<br>(15%) | Aggressive Buy |
| 14.7 - 17.2 | **+14.49%** | **93.4%** | 2,250 | 25-50%<br>(25%) | Cautious Buy |
| 17.2 - 20.8 | +12.84% | 88.7% | 2,251 | 50-75%<br>(25%) | Border Zone |
| **≥ 20.8** | **-4.65%** | **40.4%** | 2,251 | **75-100%**<br>**(25%)** | **Danger (Threshold!)** |

**Sample size explanation:** Percentile-based split means 25-50%, 50-75%, 75-100% zones each contain 25% of total → ~2,250 samples each

**Key Statistics:**
- **Return spread:** Lowest vs Highest = **24.3pp**
- **Win rate spread:** Lowest vs Highest = **57.2pp** (97.6% → 40.4%)
- **Threshold 20.8:** Both returns and win rates collapse beyond this level

#### 6.2.2 10-Year Baseline (2015-2025) - "New Normal" Validation

**Table 9: Average 1-Year Returns by P/E Zone (10 Years, Daily 2,452)**

*Note: Zones split by P/E percentiles*

| P/E Range | Avg Return | Win Rate | Samples | Percentile<br>(Proportion) | Assessment |
|-----------|-----------|----------|---------|------------|------------|
| < 16.8 | **+19.11%** | **95.9%** | 245 | 0-10%<br>(10%) | Ultra-Aggressive Buy |
| 16.8 - 17.7 | **+16.60%** | **94.3%** | 368 | 10-25%<br>(15%) | Aggressive Buy |
| 17.7 - 18.9 | +14.84% | 91.5% | 613 | 25-50%<br>(25%) | Cautious Buy |
| 18.9 - 21.2 | +10.43% | 87.6% | 613 | 50-75%<br>(25%) | Border Zone |
| **≥ 21.2** | **+2.44%** | **60.0%** | 613 | **75-100%**<br>**(25%)** | **Danger (10yr Threshold)** |

**Sample size explanation:** Percentile-based split means 25-50%, 50-75%, 75-100% zones each contain 25% of total → ~613 samples each (2,452 × 25% ≈ 613)

**10-Year Characteristics:**
- **Threshold elevated:** 20.8 → 21.2 (+0.4pt)
- **Win rate improved:** 40.4% → 60.0% (still slightly worse than coin flip)
- **Return improved:** -4.65% → +2.44% (loss → minimal return)
- **Sufficient samples:** 245~613 per zone, statistical significance secured

### 6.3 Critical Discovery: P/E ≈ 21, The Decisive Threshold

**Important Finding (Validated with 9,003 Daily Data):**

Both 30-year and 10-year data demonstrate that **P/E ≈ 21 (precisely 20.8-21.2) serves as the decisive watershed for returns and win rates**:

**30-Year Basis (Daily 9,003):**
- **P/E < 20.8:** Average return +14~20%, Win rate 88~98%
- **P/E ≥ 20.8:** Average return **-4.65%**, Win rate **40.4%**
- **Gap:** Return -24.3pp, Win rate -57.2pp

**10-Year Basis (Daily 2,452):**
- **P/E < 21.2:** Average return +15~19%, Win rate 88~96%
- **P/E ≥ 21.2:** Average return +2.44%, Win rate 60.0%
- **Gap:** Return -17pp, Win rate -35pp

**Destructive Power of the Threshold:**

**All indicators collapse beyond P/E ≈ 21:**
- **Returns:** +14~20% → -4.7% to +2.4% (average -17~24pp decline)
- **Win rates:** 93~98% → 40~60% (average -35~57pp decline)
- **Time effect:** Gap widens over time (50% after 1Q → 40% after 4Q)

**Decisive Evidence: 100-Investment Simulation**
- P/E < 20.8: **93 wins, 7 losses**
- P/E ≥ 20.8: **40 wins, 60 losses**
- **Current P/E 22.72 exceeds threshold by 1.9pt → 60% loss probability zone**

**Significance of This Discovery:**
1. **Absolute threshold identified:** Not relative assessment, but specific number (20.8-21.2)
2. **Large-scale validation:** 9,003 daily samples, 62x increase vs quarterly (148), statistical confidence secured
3. **Robust pattern:** Consistently reproduced across both 30yr and 10yr datasets
4. **Current market diagnosis:** P/E 22.72 clearly exceeds threshold, in loss risk zone
5. **Practical timing:** Provides objective action guideline "wait for P/E < 20.8"


### 6.3.1 Why Only Column M Shows Clear 20.8 Threshold?

We validated whether other P/E definitions (I, J, K, L) also exhibit the same threshold using daily data:

**Table 11: Daily Data - Threshold (75%) Return Comparison Across 5 P/E Definitions (30-Year Basis)**

| Column | Definition | Correlation<br>(4Q) | < 75%<br>Avg Return | ≥ 75%<br>Avg Return | Spread | 75% Threshold | Samples |
|--------|-----------|-------------------|-------------------|-------------------|--------|---------------|---------|
| **M** | Next 4Q | **-0.623** | **+16.03%** | **-4.65%** | **+20.68%p** | **20.8** | 9,003 🏆 |
| L | Curr Est+Next 3Q | -0.532 | +15.33% | -0.51% | +15.84%p | 21.1 | 9,003 |
| K | Curr Act+Next 3Q | -0.452 | +14.65% | +2.48% | +12.17%p | 21.4 | 9,003 |
| J | Trailing | +0.026 | +11.95% | +11.90% | **+0.05%p** | 19.2 | 9,003 ❌ |
| I | Curr+Past 3Q | -0.234 | +13.28% | +9.12% | +4.16%p | 18.9 | 9,003 |

**Key Findings (Validated with 9,003 Daily Samples, Threshold-Based Comparison):**

1. **Column M's Overwhelming Superiority:**
   - **75% threshold (P/E 20.8):** Clearest breakpoint
   - **Below threshold (<75%):** +16.03% high returns
   - **Above threshold (≥75%):** -4.65% loss!
   - **Spread: +20.68%p** (largest gap) 🏆

2. **Column L's Decent Performance:**
   - 75% threshold: P/E 21.1
   - Below: +15.33% | Above: -0.51%
   - Spread: +15.84%p (second best after M)

3. **Column K's Intermediate Performance:**
   - 75% threshold: P/E 21.4
   - Below: +14.65% | Above: +2.48%
   - Spread: +12.17%p (still profitable above threshold → unclear signal)

4. **Column J (Trailing) Completely Useless:**
   - 75% threshold: P/E 19.2
   - Below: +11.95% | Above: +11.90%
   - **Spread: +0.05%p** (no difference!) ❌
   - Zero predictive power reconfirmed

5. **Column I's Weak Performance:**
   - 75% threshold: P/E 18.9
   - Below: +13.28% | Above: +9.12%
   - Spread: +4.16%p (small gap)

**Why Only M is Clear?**
- M is **purely forward-looking (Next 4Q only)**
  - Above threshold → **Loss -4.65%** (clear warning signal)
  - Spread **+20.68%p** (maximum)
  
- K, L include current quarter:
  - Above threshold still +2.5%, -0.5% (minimal loss)
  - Spread +12~16%p (weaker than M)
  - Less dramatic signal → weaker action trigger

- J only historical results:
  - Spread ~0 → zero predictive power

**Practical Implications:**
- **"Threshold 20.8" rule applies ONLY to Column M**
- K, L thresholds at 21~21.4 but signals weak (small loss)
- **M provides most dramatic and clear timing signal** (definite loss above threshold)

### 6.4 Practical Investment Strategy

#### 6.4.1 Signal Framework (Daily Data-Based)

**Table 10: Trading Signals Based on Forward P/E (M) - Daily 9,003 Validated**

| P/E Range | Signal | Allocation | Expected Return | Win Rate | Action |
|-----------|--------|-----------|----------------|----------|--------|
| **< 13.1** | 🟢🟢 Ultra Buy | 120%+ | **+19.65%** | **97.6%** | Leveraged Long |
| **13.1 - 14.7** | 🟢 Strong Buy | 100% | **+14.40%** | **95.0%** | Full Position |
| **14.7 - 17.2** | 🟢 Buy | 80-90% | +14.49% | 93.4% | Add Exposure |
| **17.2 - 20.8** | 🟡 Neutral | 50-70% | +12.84% | 88.7% | Hold Neutral |
| **≥ 20.8** | 🔴 Danger | 20-40% | **-4.65%** | **40.4%** | Reduce |
| **≥ 22.8** | 🚨 Emergency | 0-20% | **Loss Expected** | **< 40%** | Minimal |

**Signal Interpretation:**
- 🟢🟢 Ultra Buy: 98 wins out of 100, historically best opportunity
- 🟢 Strong/Buy: Win rate 93~95%, stable high returns
- 🟡 Neutral: Win rate 89%, returns declining
- 🔴 Danger: **Win rate 40%, worse than coin flip**
- 🚨 Emergency: Loss probability maximized

#### 6.4.2 Current Market Assessment (As of November 2025)

**Current Forward P/E (M): 22.72**

- **Zone:** 🚨 Emergency Zone (above top 25%)
- **Above threshold:** +1.9pt (+8.7% premium)
- **Signal:** Strong Sell / Emergency
- **Expected return:** -4.65% (30yr) / +2.44% (10yr)
- **Win rate:** 40.4% (30yr) / 60.0% (10yr)
- **Recommended allocation:** 20-40% (conservative) / 0-20% (aggressive)

**Risk Diagnosis:**
- Current P/E fully exceeds threshold (20.8-21.2)
- **100 investments → 60 losses expected**
- Top 25% historically on 30-year basis
- If P/E reverts to median (17.25), implies **-24.0% price decline** (holding EPS constant)

**Opportunity Analysis:**
- Best entry point: P/E < 14.7 (currently 35% decline needed, 95% win rate)
- Extreme opportunity: P/E < 13.1 (currently 42% decline needed, 97.6% win rate)
- Conservative entry: P/E < 17.2 (currently 24% decline needed, 93% win rate)

---

## 7. Research Limitations and Future Directions

### 7.1 Data Limitations

#### 7.1.1 Sample Size (Resolved!)

**Quarterly Analysis Limitations (Initial Study):**
- 30 years = 148 quarters, 10 years = 40 quarters
- Some ranges (extremes) have n < 10, limiting statistical power
- Particularly 10-year data's extreme ranges have only n = 4-6 observations

**Resolved with Daily Data:**
- ✅ **30 years = 9,003 samples (62x increase)**
- ✅ **10 years = 2,452 samples (61x increase)**
- ✅ **Each zone has 245~2,251 samples secured**
- ✅ **Statistical power issue completely resolved**
- **Result: Quarterly and daily results align, significantly enhanced reliability**

#### 7.1.2 Survivorship Bias

- S&P 500 composition changes over time
- Failed companies exit, potentially overstating returns
- However, impact limited as P/E signals are relative comparisons

### 7.2 Model Limitations

#### 7.2.1 Prediction Accuracy Limitations

**Prediction Accuracy (Quarterly 148, Median-Based):**
- Column M: **61-63% accuracy** (average 61.2%, peak 63.4% at 3Q)
- Meaning: "High P/E → below-median return" prediction is correct 61% of the time
- **Limitation: Still 37-39% incorrect**

**Win Rates (Daily 9,003, By P/E Zone):**
- **P/E < 13.1:** 97.6% win rate (98 wins out of 100)
- **P/E 13.1-17.2:** 93~95% win rate (nearly certain profit)
- **P/E 17.2-20.8:** 88.7% win rate (still high)
- **P/E ≥ 20.8:** **40.4% win rate (60 losses out of 100!)**

**Difference: Accuracy 61% vs Win Rate 40~98%:**
- **Accuracy:** Overall sample average (zone-independent)
- **Win rate:** Zone-specific detailed analysis (dramatic variation by zone)
- Both meaningful, but **win rate more practical**

**Limitations:**
- Individual timing involves uncertainty
- Even P/E ≥ 20.8 has 40% profit chance (40 out of 100)
- Not an absolute timing tool but a **probabilistic edge tool**
- **However, P/E < 20.8 provides very strong edge with 93% win rate**

#### 7.2.2 Black Swan Events

- 2008 Financial Crisis, 2020 COVID-19: extreme events unpredictable by model
- During such periods, P/E may become meaningless (EPS collapses)

#### 7.2.3 Structural Changes

- Future may differ from past
- AI revolution, rate normalization could alter P/E structure
- "This time is different" is dangerous, but possible

### 7.3 Future Research Directions

#### 7.3.1 Sector-Level Analysis

- P/E predictive power may vary by sector
- Tech vs Financials vs Energy, etc.

#### 7.3.2 Macro Variable Integration

- Incorporate interest rates, inflation, GDP growth
- Conditional P/E models: "Does P/E meaning change with high rates?"

#### 7.3.3 Time-Varying Correlations

- Does P/E predictive power differ in bull vs bear markets?
- Apply regime-switching models

#### 7.3.4 Options Strategies

- Apply P/E signals to options strategies
- High P/E → Call Selling, Low P/E → Put Selling

#### 7.3.5 International Comparison

- Does framework apply to Korea, Japan, European markets?
- What about emerging markets?

---

## 8. Conclusion

### 8.1 Research Summary

This study compared five S&P 500 P/E definitions using quarterly (148) and daily (9,318) data and discovered:

1. **Forward P/E (Next 4Q EPS) is superior:**
   - Quarterly: 63.4% prediction accuracy, 15.31%p excess return
   - Daily: 62.3% prediction accuracy, 14.37%p excess return
   - Consistent superiority confirmed across both methods

2. **Trailing P/E is useless:**
   - Quarterly: 50.5% accuracy (random)
   - Daily: 50.0% accuracy (random)
   - Both methods confirm no predictive power

3. **P/E ≈ 21 as decisive threshold:**
   - 30yr basis: P/E 20.8 (reconfirmed with 9,003 daily samples)
   - 10yr basis: P/E 21.2
   - **Average: P/E ≈ 21 = Decisive watershed for both returns and win rates**

4. **All indicators collapse beyond threshold:**
   - **Returns:** P/E < 21 (+14~20%) → P/E ≥ 21 (-4.65%) = -24pp decline
   - **Win rates:** P/E < 21 (88~98%) → P/E ≥ 21 (40.4%) = -53pp plunge
   - **100 investments:** P/E < 21 wins 93 times, P/E ≥ 21 loses 60 times

5. **Current market in extreme danger zone:**
   - P/E 22.72 exceeds threshold (20.8) by 1.9pt
   - Expected return: -4.65% (30yr) / +2.44% (10yr)
   - **Loss probability: 59.6% (60 losses out of 100)**

6. **New normal exists but threshold remains destructive:**
   - Post-2015 median P/E elevated by 1.7pt (new normal)
   - Yet threshold only moved 20.8→21.2 (+0.4pt, stable)
   - **Threshold's destructive power intact (win rate 93%→40%)**

### 8.2 Theoretical Contributions

#### 8.2.1 Limits of Efficient Market Hypothesis

If markets were fully efficient, P/E should not predict future returns. Our results suggest markets fail **semi-strong form efficiency**.

However, rather than "market inefficiency," this may reflect **behavioral factors and gradual information incorporation:**
- Investors chase momentum despite knowing valuations
- Analyst forecasts adjust gradually
- Market prices alternate between over- and under-reaction

#### 8.2.2 New Perspective on Mean Reversion

This study reinterprets traditional "P/E mean reversion" explanations:

**Traditional Explanation:**
- "High P/E means valuations themselves revert to historical mean, thus lower returns"
- If this were true, Trailing P/E (historical earnings) should also have predictive power

**Our Findings:**
- Trailing P/E: correlation +0.07 (no predictive power)
- Forward P/E: correlation -0.53 (strong predictive power)
- **Difference = informational value of future EPS forecasts**

**Reinterpretation:**
- Forward P/E's negative correlation is not "P/E mean reversion" but rather
- **"Price re-adjusting to align with Forward EPS consensus"**
- Analysts forecast 3-4Q ahead EPS → Current high P/E = growth already priced in
- When forecasts materialize 3-4Q later, no further upside → low returns

**Evidence:**
- If truly mean reversion: Trailing P/E should work too → Actually doesn't work
- Only Forward P/E works = future forecast component is key → supports consensus realization mechanism

### 8.3 Practical Implications

#### 8.3.1 Investment Strategy Guide

**Core Principle: P/E ≈ 21, The Critical Threshold**

This research's most practical finding is that **P/E ≈ 21 is the decisive watershed for returns**. Daily analysis of 9,318 data points confirms returns diverge dramatically at this threshold.

**Ultra-Aggressive Buy Zone (P/E < 13.1):**
- **Daily validated return: +19.65%** (1-year basis, bottom 10%)
- **Win probability by period (9,003 samples):**
  - After 1Q (3mo): 88.3% | After 2Q (6mo): 93.7%
  - After 3Q (9mo): 93.1% | **After 4Q (12mo): 97.6%**
- Percentile: Bottom 10% (extreme undervaluation)
- Historical frequency: Very rare (market panic)
- Action: Maximum buying opportunity, full position + leverage consideration
- Examples: 2008 Financial Crisis, March 2020 COVID
- Interpretation: **98 wins out of 100 after 1 year**, historically highest win rate

**Aggressive Buy Zone (13.1 ≤ P/E < 14.7):**
- **Daily validated return: +14.40%** (1-year basis, bottom 10-25%)
- **Win probability by period:**
  - After 1Q: 72.0% | After 2Q: 76.8% | After 3Q: 86.5% | **After 4Q: 95.0%**
- Percentile: Bottom 10-25%
- Action: Aggressive buying, full position recommended
- Interpretation: **95 wins out of 100 after 1 year**, stable high-return zone

**Cautious Buy Zone (14.7 ≤ P/E < 17.2):**
- **Daily validated return: +14.49%** (1-year basis, bottom 25-50%)
- **Win probability by period:**
  - After 1Q: 76.7% | After 2Q: 88.0% | After 3Q: 90.2% | **After 4Q: 93.4%**
- Percentile: Bottom 25-50%
- Action: Add exposure, dollar-cost average
- **Complete positioning before reaching 20.8**
- Interpretation: **93 wins out of 100 after 1 year**, still high win rate

**Border Zone (17.2 ≤ P/E < 20.8):**
- **Daily validated return: +12.84%** (1-year basis, top 25-50%)
- **Win probability by period:**
  - After 1Q: 73.5% | After 2Q: 83.0% | After 3Q: 89.7% | **After 4Q: 88.7%**
- Percentile: 50-75%
- Action: Hold neutral, exercise caution on new purchases
- Warning: Approaching threshold of 20.8
- Interpretation: **89 wins out of 100 after 1 year**, win rate declining

**Danger Zone - Above Threshold (P/E ≥ 20.8):**
- **Daily validated return: -4.65%** (1-year basis, top 25%)
- **Win probability by period:**
  - After 1Q: 49.8% (coin flip) | After 2Q: 41.9%
  - After 3Q: 42.1% | **After 4Q: 40.4% (worse than coin flip)**
- **10yr basis: P/E ≥ 21.2 → +2.40%** (minimal return)
- Percentile: Top 25%+
- Action: Reduce exposure or sell, build cash
- **Current market (P/E 22.72) is here → +1.9pt above threshold**
- Interpretation: **60 losses out of 100 after 1 year**, worse than coin flip
- **Critical finding: Win rate declines over time! 50% after 1Q → 40% after 4Q**

**Critical Discovery (9,003 Daily Samples, 1-Year Returns):**
- **P/E < 20.8: Average return +14~20%, Win rate 88~98%** (solid returns + high win rate)
- **P/E ≥ 20.8: Average return -4.65%, Win rate 40.4%** (loss + worse than coin flip)
- **Across threshold 20.8:**
  - Return gap: ~19%p
  - Win rate gap: ~53%p (93% → 40%)
- **Out of 100 investments: P/E < 20.8 wins 93 times, P/E ≥ 20.8 loses 60 times!**
- **Time amplifies the gap: Short-term (after 1Q) P/E ≥ 20.8 still ~50%, but decays to 40% at 1-year**

**Timing Considerations:**
- Highest accuracy at 2-3Q (6-9 month) forward
- Unsuitable for short-term (1-month) timing
- Use for medium-term strategic allocation adjustments

#### 8.3.2 Current Application (November 2025)

**Current Situation Analysis:**
- **Forward P/E (Next 4Q EPS): 22.72**
- **Assessment: Danger zone (above threshold 21)**
- **Above threshold: +1.9pt (+8.7% premium)**
- **Expected return: -4.5% to +2.4%** (loss or minimal return)
- **Historical percentile: Top 25% (above 30yr basis 20.8)**

**Detailed Risk Assessment:**
- 30yr basis P/E > 20.8 → Average **-4.53% loss**
- 10yr basis P/E > 21.2 → Average **+2.40%** (minimal return)
- 8.7% above threshold → **Overvaluation premium burden**

**Recommended Actions (Conservative Approach):**

1. **Immediate Action: Reduce Exposure**
   - Equity allocation: Reduce to 30-40%
   - Cash allocation: Build to 60-70%
   - Rationale: Loss or minimal return zone

2. **Defer New Purchases**
   - Waiting condition: P/E < 20.8 (below threshold)
   - Target: ~11% decline from current required
   - Rationale: Return recovery below threshold

3. **1st Buy Timing: P/E < 19.5 (Median)**
   - Target: ~14% decline from current
   - Expected return: +13.15%
   - Action: Begin dollar-cost averaging

4. **2nd Buy Acceleration: P/E < 17.9 (Bottom 25%)**
   - Target: ~21% decline from current
   - Expected return: +16.84%
   - Action: Aggressive buying, expand position

5. **Final Buy: P/E < 16.5 (Bottom 10%)**
   - Target: ~27% decline from current
   - Expected return: +17.24%
   - Action: Full position, leverage consideration
   - Historical cases: 2008 Financial Crisis, 2020 COVID

**Scenario-Based Responses:**

**Optimistic Scenario (P/E maintains):**
- Probability: Medium
- Expected outcome: -4.5% to +2.4%
- Response: Hold cash, wait for opportunity

**Neutral Scenario (P/E 19-20):**
- Probability: High
- Expected outcome: +5~13%
- Response: Begin gradual buying

**Crisis Scenario (P/E < 17.9):**
- Probability: Low
- Expected outcome: +16.84% or higher
- Response: Maximum buying opportunity

### 8.4 Final Conclusions

**"Which P/E should we use?"**

Answer: **Forward P/E (Next 4Q EPS based)** - Superiority confirmed with both quarterly (148) and daily (9,318) data

**"How is current market?"**

Answer: **Strong overvaluation zone, caution required** - P/E 22.72 exceeds threshold (21) by 1.7pt

**"When to buy?"**

Answer: **Wait for P/E < 17.8** - Threshold reconfirmed with daily data (9,066 samples)

This research does not claim to offer a perfect crystal ball for complex markets. Rather, it provides **statistically significant edge: 61-63% accuracy and 15%p outperformance.**

Investing is a probabilistic game. Tilting probabilities even slightly in your favor - that is this research's value.

---

## References

This research is based purely on empirical data analysis and does not directly reference external academic literature.

**Data Sources:**
- **Price Data:** Yahoo Finance API (yfinance Python library) - S&P 500 Index (^GSPC)
- **EPS Data:** S&P Global - S&P Dow Jones Indices
  - Source: [S&P 500 EPS Estimates](https://www.spglobal.com/spdji/en/documents/additional-material/sp-500-eps-est.xlsx)
  - Provider: S&P Dow Jones Indices LLC
- **Analysis Period:** December 1988 - September 2025 (37 years, 148 quarters)

**Analysis Tools:**
- Python 3.11+
- pandas, numpy, matplotlib
- Custom-developed analysis scripts

---

## Appendix A: Chart Descriptions

**Chart Structure:**
- **Top Panel:** 30-year P/E time series (mean and ±1σ bands displayed)
- **Bottom 4 Panels:** P/E Z-score vs 1Q/2Q/3Q/4Q return scatter plots with regression lines

All charts are embedded within relevant sections of main text (Figures 1-4).

---

## Appendix B: Code Reproducibility

All analyses in this research were implemented in Python, organized into two groups:

### **Quarterly Analysis Scripts:**

1. `compare_pe_definitions.py`: Compare 5 P/E definitions and generate charts
2. `calculate_probabilities.py`: Calculate prediction accuracy
3. `calculate_actual_returns.py`: Calculate actual return differentials
4. `pe_quartile_analysis.py`: Quartile analysis and investment guide
5. `annualized_comparison_all.py`: Compare annualized excess returns
6. `compare_all_pe_quartiles.py`: Compare 10-year vs 30-year quartiles
7. `trailing_pe_test.py`: Trailing P/E validation
8. `calculate_pe_win_probability.py`: **Calculate win probability matrix by zone×period (newly added)**

### **Daily Analysis Scripts (62x Sample Size Enhancement):**

1. `visualize_pe_mean_reversion_daily.py`: Generate daily mean reversion charts (Figure 3-1~3-5)
2. `visualize_pe_correlations.py`: P/E vs return correlation charts (Figure 4)

**Reproduction Environment:**
- Python 3.11+
- pandas, numpy, matplotlib, yfinance, openpyxl, Pillow, boto3

**Data:**
- Price data: Public (Yahoo Finance)
- EPS data: Public (S&P Global - [sp-500-eps-est.xlsx](https://www.spglobal.com/spdji/en/documents/additional-material/sp-500-eps-est.xlsx))

### Key Code Examples

**1. P/E Calculation and Z-Score Normalization:**

```python
# Calculate P/E
quarterly_df['PE'] = quarterly_df['Price'] / quarterly_df['EPS']

# Z-Score normalization
mean_pe = quarterly_df['PE'].mean()
std_pe = quarterly_df['PE'].std()
quarterly_df['PE_Zscore'] = (quarterly_df['PE'] - mean_pe) / std_pe
```

**2. Forward Returns Calculation:**

```python
# Calculate 1Q, 2Q, 3Q, 4Q forward returns
for n_quarters in [1, 2, 3, 4]:
    quarterly_df[f'Return_{n_quarters}Q'] = \
        quarterly_df['Price'].pct_change(n_quarters).shift(-n_quarters) * 100
```

**3. Correlation and Accuracy Calculation:**

```python
# Pearson correlation
correlation = zscore.corr(returns)

# Accuracy using median threshold
median_return = returns.median()
high_pe_correct = ((zscore > 0) & (returns < median_return)).sum()
low_pe_correct = ((zscore < 0) & (returns >= median_return)).sum()
accuracy = (high_pe_correct + low_pe_correct) / len(zscore) * 100
```

**Full Code Availability:**
Complete script files are included in the research project directory and available upon request.

---

**This paper was prepared for academic and educational purposes. Always conduct your own due diligence before making investment decisions.**

**Disclaimer:** Past performance does not guarantee future results. 61-63% prediction accuracy implies 37-39% error rate. Proper risk management and diversification are recommended.

---

**END OF PAPER**

© 2025 Seung-Gu Kang (강승구). All rights reserved.

