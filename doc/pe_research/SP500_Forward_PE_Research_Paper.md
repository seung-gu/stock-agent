# S&P 500 Forward P/E Mean Reversion and Market Timing Strategy: An Empirical Study

**A Comprehensive Analysis of Predictive Power Across Multiple P/E Definitions**

---

**Author:** Seung-Gu Kang (강승구)  
**Research Period:** November 2025  
**Data Coverage:** December 1988 - September 2025 (37 years, Quarterly 148 + Daily 9,003)  
**Last Updated:** November 13, 2025

---

## Abstract

This study examines the predictive power of S&P 500 Forward P/E ratios in forecasting future returns and proposes a practical investment strategy based on these findings. Analyzing 37 years (1988-2025) of data, we compare three Operating Earnings-based P/E definitions (TTM Operating, Mixed Operating, Forward Operating) using quarterly data (148 points) for primary analysis, then validate with daily data (9,003 points, 60x sample size).

First, comparing Operating vs As Reported Earnings revealed Operating's superior predictive power across all periods (12-month correlation: -0.620 vs -0.590). As Reported shows significant distortion from one-time items, particularly during the 2000 Dot-com Bubble, 2008 Financial Crisis, and 2020 COVID-19 Pandemic.

Using quarterly data (148 points, 1988-2025, 37 years) for primary analysis and validating with daily data (9,003 points, same period, 60x increase), results show that Forward Operating [Q'(1)+Q'(2)+Q'(3)+Q'(4)] delivers 63.4% prediction accuracy, with Low P/E outperforming High P/E by 15.31 percentage points.

Key findings include:
1. **Operating Earnings selection critical:** Consistently higher predictive power than As Reported (correlation difference 0.03~0.08)
2. **Forward Operating is best:** 3x predictive power vs Trailing (correlation -0.533 vs -0.163)
3. Bottom 25% P/E delivers 15.91% annual return vs 0.60% for Top 25% (25x difference)
4. **Daily data validation (9,003 samples) confirms quarterly findings:** Correlation -0.62, Low P/E outperforms High P/E by 15.61%p annualized
5. **P/E ≈ 21 as critical threshold:** 37yr basis 20.8, 10yr basis 21.2, reconfirmed with daily data
6. **Returns drop sharply beyond threshold:** P/E < 21: +13~17%, P/E ≥ 21: -4.5%  (loss)
7. Current market (P/E 22.72) exceeds threshold by 1.9pt, in loss risk zone
8. **Trailing-like Operating P/E as market bottom indicator:** Trailing-like Operating [Q(-3)+Q(-2)+Q(-1)+Q(0)] P/E falling below -1.5σ effectively identifies major market bottoms (differs from backtesting's TTM Operating, as Q(0) may be an estimate)

The true significance of this research is to empirically demonstrate that **P/E ratios that showed strong predictive power in backtesting decrease to nearly meaningless levels when using actual estimates in a real-world environment**. This suggests that the simple logic of "high P/E means overvalued and risky, low P/E means undervalued opportunity" may not work in actual investment environments, and warns of the risks of relying on a single indicator for investment decisions, which has both academic and practical significance (see Sections 6 and 7 for details).

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
- 2.4 EPS Definitions and Notation
- 2.5 Operating vs As Reported Earnings
- 2.6 Selection of Analysis Variables

### **3. Methodology**
- 3.1 Backtesting Methodology (Actuals-based)
- 3.2 Real-world Estimates Validation Methodology
- 3.3 Evaluation Metrics

### **4. Backtesting Results: Actuals-based Analysis**
- 4.1 Quarterly Analysis Results
- 4.2 Daily Analysis Results
- 4.3 Key Findings

### **5. Real-world Validation: Estimates-based Analysis**
- 5.1 Methodology and Data
- 5.2 Analysis Results
- 5.3 Percentile Analysis
- 5.4 Market Timing Signal Analysis: P/E Sigma Bands and Market Bottoms

### **6. Key Discovery: Backtesting vs Real-world Environment**
- 6.1 Correlation Comparison
- 6.2 Spread Comparison
- 6.3 Analysis of Predictive Power Differences
- 6.4 What This Means

### **7. Research Limitations and Implications**
- 7.1 Limitations of Backtesting
- 7.2 Implications for Real-world Investment Environment
- 7.3 Risks of Simple P/E-based Judgment

### **8. Conclusion: The True Significance of This Research**

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

**Data Exploration Process:**

1. **Discovered EPS Definition Diversity:**
   - Operating Earnings vs As Reported Earnings
   - Trailing (historical) vs Forward (future)
   - Various time range combinations

2. **Selected Operating Earnings:**
   - As Reported shows significant distortion from one-time items
   - Particularly distorts statistics during crises (2000 Dot-com Bubble, 2008 Financial Crisis, 2020 Pandemic)
   - Operating Earnings demonstrates consistently superior predictive power

3. **Constructed 3 Variables:**
   - **TTM Operating** = Q(-3) + Q(-2) + Q(-1) + Q(0): Trailing 4Q actuals
   - **Mixed Operating** = Q(0) + Q'(1) + Q'(2) + Q'(3): Actual 1Q + Estimate 3Q
   - **Forward Operating** = Q'(1) + Q'(2) + Q'(3) + Q'(4): Estimate 4Q

This enabled systematic comparison of P/E metrics with varying degrees of "forward-looking" orientation.

This discovery transformed our simple "data visualization task" into a fundamental research question: **"Which metric is actually useful?"**

### 1.3 Research Objectives

This study aims to:

1. **EPS Definition Selection:** Select optimal standard through Operating vs As Reported Earnings comparison
2. **Comparative Analysis:** Quantitatively compare predictive power across three Operating P/E definitions
3. **Mechanism Identification:** Theoretically explain why Forward Operating outperforms others
4. **Practical Application:** Establish concrete P/E-based trading strategies by quartile
5. **Current Assessment:** Evaluate market valuation as of November 2025

### 1.4 Research Novelty

This study differentiates itself from existing literature through:

1. **EPS Accounting Standard Comparison:** Empirically analyzes predictive power difference between Operating vs As Reported
2. **One-time Item Distortion Analysis:** Identifies distortion mechanisms during crises (2000 Dot-com Bubble, 2008 Financial Crisis, 2020 Pandemic)
3. **Multi-Definition Comparison:** Systematic comparison of 3 Operating definitions rather than single metric
4. **Probabilistic Approach:** Calculating actual prediction accuracy (%) and return differentials, beyond simple correlation
5. **New Normal Analysis:** Comparing 30-year vs 10-year baselines to capture low-rate era valuation shifts
6. **Transparent Methodology:** All analysis processes and code disclosed for reproducibility

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
- Which has higher predictive power: Operating vs As Reported?
- Which shows stronger relationship with future returns: Trailing vs Forward?
- Does traditional "valuation mean reversion" explanation work?
- Or does a different mechanism exist?

The answer is provided in Section 5.2.

### 2.4 EPS Definitions and Notation

For clarity, this research employs the following notation system:

**Quarter Notation:**
- **Q(n)**: Function-style quarter notation
  - n < 0: Past quarters (e.g., Q(-3), Q(-2), Q(-1))
  - n = 0: Current quarter (Q(0))
  - n > 0: Future quarters (e.g., Q(1), Q(2), Q(3), Q(4))

**Actuals vs Estimates:**
- **Q(n)**: Actuals - Already reported actual results
- **Q'(n)**: Estimates - Analyst consensus forecasts

**Examples:**
- Q(-3) + Q(-2) + Q(-1) + Q(0) = Past 3 quarters actuals + Current quarter actuals
- Q'(1) + Q'(2) + Q'(3) + Q'(4) = Next 4 quarters estimates
- Q(0) + Q'(1) + Q'(2) + Q'(3) = Current quarter actuals + Next 3 quarters estimates

### 2.5 Operating vs As Reported Earnings

S&P 500 EPS is reported under two accounting standards:

#### 2.5.1 Definitions

**Operating Earnings:**
- **Excludes** one-time items
- Removes restructuring costs, asset impairments, legal settlements, etc.
- Measures **sustainable core earning power**
- Analysts' preferred "normalized" EPS

**As Reported Earnings:**
- GAAP-based **actual reported net income**
- **Includes** one-time items
- More conservative and realistic figure

#### 2.5.2 Empirical Analysis of Differences

Forward 4Q EPS comparison over 1988-2025 period (37 years):

```
Operating (M):   Average 93.44, Range 19.30 ~ 294.11
As Reported (N): Average 82.25, Range 6.86 ~ 271.82
Difference (M-N): Average 11.18 (12.0%)
```

**Key Findings:**
- Operating EPS **12% higher** than As Reported on average
- Implies one-time items were predominantly **losses**
- Difference maximizes during special situations (financial crisis, pandemic)

#### 2.5.3 Distortion Effects: Crisis Period Analysis

As Reported Earnings show significant distortion during special situations:

**Figure 1: Operating vs As Reported Earnings (1988-2025)**

![Operating vs As Reported](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_operating_vs_reported_full_en_1763033439.jpg)

The chart shows 37 years (1988-2025) comparison of Operating and As Reported Earnings. Shaded regions indicate crisis periods.

**Major Distortion Cases:**

**1. Dot-com Bubble Collapse (2000-2002, Red Shading):**
- Massive asset impairments, restructuring costs
- As Reported EPS plunged (low $7)
- Operating EPS relatively stable (low $30s)
- EPS difference (M-N) significantly widened

**2. Financial Crisis (2008-2009, Orange Shading):**
- Financial institution losses, bad asset write-offs
- EPS difference (M-N) reached **$36, historical maximum**
- **As Reported-based P/E spiked above 200** (extreme distortion)
- Operating-based analysis provided more reliable signals

**3. COVID-19 Pandemic (2020, Purple Shading):**
- Unexpected massive expenses
- Lockdowns, inventory losses, travel/hospitality impact
- As Reported EPS temporarily declined
- Rapid recovery normalized Operating/As Reported difference quickly

**Conclusion:**
During crises, As Reported falls excessively due to one-time losses, abnormally elevating P/E, while Operating more accurately reflects sustainable earning power.

#### 2.5.4 Predictive Power Comparison

Forward 4Q correlation with future returns:

| Period | Operating (M) | As Reported (N) | Winner |
|--------|---------------|-----------------|--------|
| 1Q (3mo) | -0.3976 | -0.3166 | **M** (diff 0.081) |
| 2Q (6mo) | -0.5416 | -0.4979 | **M** (diff 0.044) |
| 3Q (9mo) | -0.6067 | -0.6013 | **M** (diff 0.005) |
| 4Q (12mo) | -0.6195 | -0.5903 | **M** (diff 0.029) |

**Conclusion:**
- **Operating Earnings superior predictive power across all periods**
- Excluding one-time items better reflects sustainable earning power
- As Reported suffers reduced predictive power from crisis-period noise

### 2.6 Selection of Analysis Variables

Based on above analysis, **this research analyzes only Operating Earnings-based EPS:**

**Selected Variables (3):**

1. **TTM Operating** (Trailing Twelve Months - Operating)
   - Composition: Q(-3) + Q(-2) + Q(-1) + Q(0) (all actuals)
   - Characteristics: Historical basis, most objective
   - Disadvantage: Lagging, fails to capture future changes

2. **Mixed Operating** (Hybrid - Operating)
   - Composition: Q(0) + Q'(1) + Q'(2) + Q'(3) (1 actual + 3 estimates)
   - Characteristics: Blend of past and future
   - Expected: Moderate predictive power

3. **Forward Operating** (Pure Forward - Operating)
   - Composition: Q'(1) + Q'(2) + Q'(3) + Q'(4) (all estimates)
   - Characteristics: Completely forward-looking
   - Advantage: Aligns with market's forward-looking nature

**Excluded Variables:**
- TTM As Reported (Q(-3) + Q(-2) + Q(-1) + Q(0), As Reported): One-time item distortion
- Forward As Reported (Q'(1) + Q'(2) + Q'(3) + Q'(4), As Reported): Referenced briefly only

**All subsequent analysis focuses on these 3 Operating Earnings variables.**

---

## 3. Methodology

### 3.1 Backtesting Methodology (Actuals-based)

#### 3.1.1 Data Collection and Preprocessing

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
- **Row Range:** 132-278 (December 1988 - September 2025, full 37-year period)

**Analysis Target EPS (All Operating Earnings Basis):**

1. **TTM Operating** = Q(-3) + Q(-2) + Q(-1) + Q(0)
   - Provided by S&P Global
   - Trailing 4Q actuals

2. **Mixed Operating** = Q(0) + Q'(1) + Q'(2) + Q'(3)
   - Constructed in this research
   - Actual 1Q + Estimate 3Q

3. **Forward Operating** = Q'(1) + Q'(2) + Q'(3) + Q'(4)
   - Constructed in this research
   - Estimate 4Q (fully forward-looking)

Mixed and Forward were generated by recombining quarterly EPS values from the source data to create varying degrees of forward-looking metrics.

**Data Cleaning:**
Removed extraneous text from date column (e.g., "(81.3%)") and parsed with pd.to_datetime().

```python
date_str = str(date_val).split('(')[0].strip()
date_parsed = pd.to_datetime(date_str)
```

#### 3.1.3 Final Dataset

- **Analysis Period:** December 1988 - September 2025 (37 years)
- **Total Observations:** 148 quarters
- **Valid Data per EPS Column:** 148 observations (no missing values)

#### 3.1.2 P/E Ratio Calculation

For each quarter $t$, P/E ratio is calculated as:

$$
PE_t = \frac{Price_t}{EPS_t}
$$

Where $Price_t$ is the smoothed average closing price for quarter $t$, and $EPS_t$ is the EPS estimate for that quarter.

#### 3.1.3 Z-Score Normalization

Since absolute P/E levels vary across eras, we normalize using Z-scores to measure relative over/undervaluation:

$$
Z_t = \frac{PE_t - \mu_{PE}}{\sigma_{PE}}
$$

Where:
- $\mu_{PE}$: Mean P/E across entire period
- $\sigma_{PE}$: Standard deviation of P/E across entire period

Z-score > 0 indicates overvaluation, Z-score < 0 indicates undervaluation relative to historical mean.

#### 3.1.4 Forward Returns Calculation

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
- High/Low groups classified by Z-score across entire 37 years (148 quarters)

**Significance of This Method:**
- Removes period effect
- Standardizes P/E signal's pure predictive power to annual basis
- Enables fair comparison across different time horizons

### 3.2 Real-world Estimates Validation Methodology

#### 3.2.1 Data Collection

**Estimates Data:**
- Source: Actual estimates extracted from FactSet PDFs
- Period: December 2016 - November 2025 (approximately 8 years)
- Report Frequency: Weekly (approximately 345 report dates)
- Feature: Uses actual future estimates (*)

**Price Data:**
- Source: Yahoo Finance API (yfinance library)
- Uses actual daily closing prices
- Total trading days: approximately 22,358

#### 3.2.2 P/E Calculation Method

For each report date's EPS estimates, calculate daily P/E from that report date until the next report date:

- Fix EPS estimates from the report date
- Calculate P/E using actual daily prices
- Use the same EPS until the next report arrives

This mirrors the actual investment environment.

#### 3.2.3 Future Returns Calculation

For each date, calculate returns using actual prices exactly 63 days (1Q), 126 days (2Q), 189 days (3Q), and 252 days (4Q) later:

$$
Return_{t,nQ} = \frac{Price_{t+nQ} - Price_t}{Price_t} \times 100\%
$$

Where $nQ$ is the date $n$ quarters later (1Q = 63 days, 4Q = 252 days).

### 3.3 Evaluation Metrics

#### 3.3.1 Pearson Correlation

Measures linear relationship between P/E Z-score and future returns:

$$
r = \frac{\sum (Z_i - \bar{Z})(R_i - \bar{R})}{\sqrt{\sum (Z_i - \bar{Z})^2 \sum (R_i - \bar{R})^2}}
$$

Negative correlation implies "high P/E → low returns."

#### 3.3.2 Prediction Accuracy

Using median return as threshold, we dichotomize returns and calculate accuracy:

- High P/E (Z > 0) & Return < Median: Correct prediction
- Low P/E (Z < 0) & Return ≥ Median: Correct prediction

$$
Accuracy = \frac{\text{Number of Correct Predictions}}{\text{Total Predictions}} \times 100\%
$$

#### 3.3.3 Average Return Differential (Spread)

Most critical metric for investment decisions:

$$
\Delta Return = \overline{Return}_{Z<0} - \overline{Return}_{Z>0}
$$

Calculates average return difference between Low P/E and High P/E groups.

---

## 4. Backtesting Results: Actuals-based Analysis

### 4.1 Quarterly Analysis Results

#### 4.1.1 Comparative Analysis of Three Operating P/E Definitions

**Correlation Analysis**

**Table 1: Pearson Correlation Between P/E Z-score and Future Returns**

| EPS Definition | Composition | 1Q (3mo) | 2Q (6mo) | 3Q (9mo) | 4Q (12mo) | **Avg** |
|----------------|-------------|----------|----------|----------|-----------|---------|
| **Forward Operating** | Q'(1)+Q'(2)+Q'(3)+Q'(4) | -0.413 | -0.538 | **-0.591** | -0.588 | **-0.533** ✅ |
| **Mixed Operating** | Q(0)+Q'(1)+Q'(2)+Q'(3) | -0.382 | -0.477 | -0.493 | -0.474 | **-0.457** |
| **TTM Operating** | Q(-3)+Q(-2)+Q(-1)+Q(0) | -0.106 | -0.147 | -0.189 | -0.212 | **-0.163** |

**Key Findings:**
1. **Forward Operating exhibits strongest negative correlation** (average -0.533)
2. **Peak at 3-4 quarters forward: -0.59**
3. **TTM Operating (Trailing) shows very weak correlation** (average -0.163)
4. More forward-looking → better predictive power
5. Sample size of n=145-148 provides sufficient observations

**Prediction Accuracy Analysis**

**Table 2: P/E-Based Return Prediction Accuracy (Median Threshold)**

| EPS Definition | Composition | 1Q | 2Q | 3Q | 4Q | **Avg** | Interpretation |
|----------------|-------------|-----|-----|-----|-----|---------|----------------|
| **Forward Operating** | Q'(1)+Q'(2)+Q'(3)+Q'(4) | 56.5% | 62.3% | **63.4%** | 62.5% | **61.2%** | Strong ✅ |
| **Mixed Operating** | Q(0)+Q'(1)+Q'(2)+Q'(3) | 57.8% | 59.6% | 59.3% | 55.6% | **58.1%** | Moderate |
| **TTM Operating** | Q(-3)+Q(-2)+Q(-1)+Q(0) | 46.9% | 48.6% | 52.4% | 51.4% | **49.8%** | Useless ❌ |

**Interpretation:**
- 50% = coin flip level
- **Forward Operating achieves 61-63% accuracy**, statistically significant
- **TTM Operating (Trailing) at 49.8% = no better than random**

**Actual Return Differential Analysis (Most Important)**

**Table 3: Average 1-Year Returns by P/E Group (High vs Low)**

| Column | Definition | High P/E (Z>0) | Low P/E (Z<0) | **Difference** | Samples (H/L) |
|--------|-----------|----------------|---------------|----------------|---------------|
| **Forward Operating** | Q'(1)+Q'(2)+Q'(3)+Q'(4) | +0.60% | +15.91% | **+15.31%p** ✅ | 56 / 88 |
| **Mixed Operating** | Q(0)+Q'(1)+Q'(2)+Q'(3) | +4.60% | +14.00% | **+9.39%p** | 62 / 82 |
| **TTM Operating** | Q(-3)+Q(-2)+Q(-1)+Q(0) | +7.69% | +11.57% | **+3.87%p** | 60 / 84 |

**Critical Findings:**
1. **Forward Operating shows 25x return differential** (15.91% vs 0.60%)
2. High P/E periods deliver cash-equivalent returns (0.60%)
3. Low P/E periods deliver strong ~16% annual returns
4. **TTM Operating (Trailing) shows weak discrimination (3.87%p), 1/4 of Forward**

**Annualized Analysis: Removing Period Effect**

**Important Question:** "Isn't 4Q (12 months) having higher absolute returns than 1Q (3 months) simply due to longer time period?"

To verify, we converted to **annualized returns** (30-year data, 148 quarters):

**Table 3-1: Forward Operating [Q'(1)+Q'(2)+Q'(3)+Q'(4)] - Return Differentials by Period & Annualized (37 Years)**

| Period | Low P/E Avg | High P/E Avg | **Difference** | **Annualized Difference** |
|--------|------------|--------------|----------------|--------------------------|
| 1Q (3 months) | +4.12% | +0.04% | +4.07% | **+16.28% / year** |
| 2Q (6 months) | +8.14% | +0.14% | +8.00% | **+16.00% / year** |
| 3Q (9 months) | +12.03% | +0.27% | +11.76% | **+15.68% / year** |
| 4Q (12 months) | +15.91% | +0.60% | +15.31% | **+15.31% / year** |

**Findings:**
- When annualized, all periods show **Low P/E outperforming High P/E by ~15-16%p / year** consistently
- Absolute returns increasing with period = **time effect**
- P/E's true predictive power = **Low vs High return differential of 15-16%p annually**
- **Key proof: This remains constant whether 1Q or 4Q horizon → Quarterly return differential is nearly identical**

**What This Means:**
- P/E signal's effect is **stable regardless of time horizon**
- Whether 3 months or 12 months ahead, **Low P/E beats High P/E by ~4%p per quarter** (15-16%p/year ÷ 4 quarters)
- Longer holding periods simply accumulate differential, not strengthen P/E signal
- **Quarterly consistency = proof of predictive power reliability**

**Do other P/E definitions also show consistency?**

**Table 3-2: Annualized Excess Returns Comparison Across 3 Operating P/E Definitions (37 Years, 148 Quarters)**

| EPS Definition | 1Q→Ann | 2Q→Ann | 3Q→Ann | 4Q→Ann | **Average** | Consistency |
|---------------|--------|--------|--------|--------|-------------|-------------|
| **M (Next 4Q)** | +16.29% | +16.00% | +15.68% | +15.31% | **+15.82%** | ✅ Highly Consistent |
| K (Curr Act+Next 3Q) | +15.48% | +13.43% | +13.11% | +10.36% | **+13.09%** | △ Variable |
| L (Curr Est+Next 3Q) | +14.33% | +12.38% | +11.08% | +9.39% | **+11.80%** | △ Variable |
| J (Trailing) | +3.88% | +3.63% | +3.97% | +5.59% | **+4.27%** | ⚪ Low but Stable |
| I (Curr+Past 3Q) | +1.15% | +1.53% | +3.35% | +3.87% | **+2.47%** | ❌ Nearly Useless |

**Additional Findings:**

1. **Only Forward Operating shows perfect consistency:**
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
- **Forward Operating not only has highest predictive power but also most stable**
- K, L are decent (11-13%/year) but period-dependent
- **Reason to use M: High predictive power + Consistency**

**Practical Implications:**
- P/E signal shows consistent effect from short-term (1Q) to long-term (4Q) for Forward Operating
- However, accuracy is highest at 2-3Q forward (correlation -0.54 ~ -0.59)

**Figures 2-6: Individual P/E Definition Analysis**

**Figure 2-1: Forward Operating - Mean Reversion Analysis (Best Performance)**

![Figure 2-1: Forward Operating](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_mean_reversion_M_1762956822.jpg)

**Figure 2-2: Mixed Operating - Mean Reversion Analysis**

![Figure 2-2: Mixed Operating](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_mean_reversion_L_1762956822.jpg)

**Figure 2-3: TTM Operating - Mean Reversion Analysis (Trailing)**

![Figure 2-3: TTM Operating](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_mean_reversion_I_1762956823.jpg)


### 4.2 Daily Analysis Results

#### 4.2.1 Research Motivation

The previous quarterly analysis used 148 observations. To enhance statistical reliability, we performed **validation analysis using daily (daily) price data**.

**Key Questions:**
- If we increase sample size 60x (148 → 9,003), do results change?
- Does daily data noise dilute signals, or enable more precise estimation?

Beyond simple "above/below median," **actual return magnitudes** matter most:

- High P/E: Average +0.60%
- Low P/E: Average +15.91%

This is the truly actionable information for investors.

---

## 4.3 Daily Data Validation: Enhanced Sample Size Analysis

### 4.3.1 Research Motivation

The previous quarterly analysis used 148 observations. To enhance statistical reliability, we conducted **additional validation using daily price data**.

**Key Questions:**
- Does increasing sample size 60x (148 → 9,003) change results?
- Does daily data noise dilute the signal, or enable more precise estimation?

### 4.3.2 Methodology: Daily Data Mapping

**EPS-to-Price Mapping Logic:**

```
Use the quarter-end EPS for all dates within that quarter

Example:
┌──────────────────────────────────────────────────────────┐
│ Period: 2025-07-01 ~ 2025-09-30 (Q3)                     │
│ EPS Used: Values from 2025-09-30 row                     │
│                                                          │
│ EPS Composition by Variable (Q' = Est, Q = Actual):      │
│   - Forward Operating:  294.11 = Q'(1)+Q'(2)+Q'(3)+Q'(4) │
│                                   (Q4'+2026Q1'+Q2'+Q3')  │
│   - Mixed Operating:    288.10 = Q(0)+Q'(1)+Q'(2)+Q'(3)  │
│                                   (Q3'+Q4'+2026Q1'+Q2')  │
│   - TTM Operating:      255.80 = Q(-3)+Q(-2)+Q(-1)+Q(0)  │
│                                   (2024Q4+Q1+Q2+Q3')     │
│                                                          │
│ Daily P/E Calculation (Forward Operating example):       │
│   - 2025-07-01: P/E = 5,475 ÷ 294.11 = 18.61             │
│   - 2025-07-02: P/E = 5,480 ÷ 294.11 = 18.63             │
│   - 2025-09-30: P/E = 5,738 ÷ 294.11 = 19.51             │
└──────────────────────────────────────────────────────────┘
```

**Data Scale:**
- Quarterly: 148 data points
- Daily: **9,003 data points** (60.8x increase)
- Standard Error: **8x reduction** (0.083 → 0.010)

#### 4.3.3 Result 1: Correlation Comparison

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
1. **Forward Operating: 4Q correlation improved with daily data** (-0.588 → -0.623, +6%)
2. **K, L: Consistent improvement across all periods** (avg +13%, +9%)
3. **I: Weak signal becomes clearer** (+18% improvement)
4. **J(Trailing): Still useless with daily data** (r ≈ 0)

**Figure 3: Forward Operating Daily Data Mean Reversion Analysis (9,003 analysis samples)**

![Figure 3: Daily Forward Operating](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_mean_reversion_daily_M_1762971064.jpg)

*Forward Operating P/E time series and future return correlations using 9,003 daily data points. Mixed Operating and TTM Operating charts show similar patterns but lower correlations, thus omitted.*


#### 4.3.4 Result 2: Annualized Return Differential Comparison

**Table 4-2: Annualized Return Differential (Low P/E - High P/E) - Quarterly vs Daily**

| Variable | Data | 1Q→Ann | 2Q→Ann | 3Q→Ann | 4Q(Actual) | **Average** |
|----------|------|--------|--------|--------|----------|---------|
| **Forward Operating** | Quarterly | +17.33% | +16.67% | +15.99% | **+15.31%** | +16.33% |
| **Forward Operating** | Daily | +16.99% | +15.86% | +15.22% | **+14.37%** | +15.61% |
| **Forward Operating** | Diff | -0.34% | -0.81% | -0.77% | -0.94% | **-0.72%** |

**Key Findings:**
1. **4Q (actual 1-year) as benchmark for annualization accuracy:** 
   - Quarterly 4Q = +15.31% (actual value)
   - Daily 4Q = +14.37% (0.94pp difference)

2. **Quarterly data superiority:**
   - Quarterly average (+16.33%) closer to actual (+15.31%) than daily (+15.61%)
   - Daily slightly underestimates due to short-term noise

3. **K, L perform better with daily:**
   - K: +0.81pp improvement
   - L: +1.10pp improvement

#### 4.3.5 Result 3: P/E Quartile Returns (37-Year vs 10-Year)

**Table 4-3: Forward Operating - P/E Quartile Returns Comparison (Daily Data)**

| Period | Quartile | P/E Range | Average Return | Samples |
|--------|----------|-----------|----------------|---------|
| **37-Year** | Bottom 25% | **< 14.6** | **+16.90%** | 2,267 |
| **37-Year** | 25-50% | 14.6 - 17.2 | +14.36% | 2,266 |
| **37-Year** | 50-75% | 17.2 - 20.8 | +12.88% | 2,266 |
| **37-Year** | Top 25% | **≥ 20.8** | **-4.53%** | 2,267 |
| **37-Year** | **Spread** | - | **+21.43%p** | - |
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
   - 9,003 samples for robust estimation
   - Results nearly identical to quarterly (within ±0.5pp)

**Figure 4: Forward Operating P/E vs 1-Year Return Correlation (Daily Data, 9,003 analysis samples)**

![Figure 4: Correlation M](https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/charts/pe_correlation_M_1762971065.jpg)

*Strong negative correlation between P/E and 1-year returns confirmed with 9,003 daily data points (r = -0.62)*

### 4.3 Key Findings

Summarizing the backtesting results:

1. **Forward Operating P/E shows superior predictive power**
   - Correlation: -0.533 (quarterly), -0.623 (daily 4Q)
   - Prediction accuracy: 61-63%
   - Spread: +15.31%p (quarterly), +14.37%p (daily)

2. **P/E ≈ 21 is a critical threshold**
   - 37-year basis: P/E 20.8
   - 10-year basis: P/E 21.2
   - Returns drop sharply beyond threshold (-4.65% ~ +2.44%)

3. **Daily data confirms quarterly findings**
   - Sample size increased 60x (148 → 9,003)
   - Results remain consistent

---

## 5. Real-world Validation: Estimates-based Analysis

### 5.1 Methodology and Data

#### 5.1.1 Data Collection

**Estimates Data:**
- Source: Actual estimates extracted from FactSet PDFs
- Period: December 2016 - November 2025 (approximately 8 years)
- Report Frequency: Weekly (approximately 345 report dates)
- Feature: Uses actual future estimates (*)

**Price Data:**
- Source: Yahoo Finance API (yfinance library)
- Uses actual daily closing prices
- Total trading days: approximately 22,358

#### 5.1.2 P/E Calculation Method

For each report date's EPS estimates, calculate daily P/E from that report date until the next report date:

- Fix EPS estimates from the report date
- Calculate P/E using actual daily prices
- Use the same EPS until the next report arrives

This mirrors the actual investment environment.

#### 5.1.3 Future Returns Calculation

For each date, calculate returns using actual prices exactly 63 days (1Q), 126 days (2Q), 189 days (3Q), and 252 days (4Q) later:

$$
Return_{t,nQ} = \frac{Price_{t+nQ} - Price_t}{Price_t} \times 100\%
$$

Where $nQ$ is the date $n$ quarters later (1Q = 63 days, 4Q = 252 days).

### 5.2 Analysis Results

#### 5.2.1 Correlation Analysis

**Table 5-1: Real-world Estimates-based P/E vs Future Returns Correlation (2016-2025, 8 years)**

| P/E Type | 1Q | 2Q | 3Q | 4Q | Sample Size |
|---------|-----|-----|-----|-----|-------------|
| **Forward Operating** | -0.080 | -0.068 | -0.081 | **-0.132** | 20,177 |
| **Mixed Operating** | -0.053 | -0.036 | -0.040 | **-0.086** | 20,177 |
| **TTM Operating** | -0.041 | -0.017 | -0.026 | **-0.087** | 20,177 |

**Key Findings:**
- Using actual estimates, correlations **decrease dramatically**
- Forward Operating: -0.132 (backtesting: -0.623, approximately 79% decrease)
- Mixed Operating: -0.086 (backtesting: -0.532, approximately 84% decrease)
- TTM Operating: -0.087 (backtesting: -0.234, approximately 63% decrease)

### 5.3 Percentile Analysis

**Table 5-2: Real-world Estimates-based Percentile Returns (Forward Operating PE, 4Q basis)**

| Percentile Range | P/E Range | 1Q Return | 2Q Return | 3Q Return | 4Q Return |
|------------------|-----------|------------|------------|------------|------------|
| Bottom 25% | 12.37 - 17.76 | 2.78% | 5.07% | 6.95% | 9.99% |
| 25-50% | 17.76 - 20.27 | 2.39% | 5.48% | 9.73% | 12.32% |
| 50-75% | 20.27 - 21.76 | 3.35% | 5.96% | 7.49% | 8.16% |
| Top 25% | 21.76 - 24.79 | 1.44% | 3.71% | 5.51% | 8.00% |
| **Spread (Bottom-Top)** | - | **+1.34%p** | **+1.35%p** | **+1.44%p** | **+1.99%p** |

**Table 5-3: Real-world Estimates-based Percentile Returns (Mixed Operating PE, 4Q basis)**

| Percentile Range | P/E Range | 1Q Return | 2Q Return | 3Q Return | 4Q Return |
|------------------|-----------|------------|------------|------------|------------|
| Bottom 25% | 12.73 - 18.23 | 2.63% | 4.89% | 6.75% | 9.75% |
| 25-50% | 18.23 - 20.98 | 2.44% | 5.46% | 9.68% | 12.23% |
| 50-75% | 20.98 - 22.63 | 3.01% | 5.50% | 6.47% | 6.71% |
| Top 25% | 22.63 - 27.73 | 1.90% | 4.46% | 7.01% | 9.92% |
| **Spread (Bottom-Top)** | - | **+0.73%p** | **+0.43%p** | **-0.26%p** | **-0.16%p** |

**Table 5-4: Real-world Estimates-based Percentile Returns (TTM Operating PE, 4Q basis)**

| Percentile Range | P/E Range | 1Q Return | 2Q Return | 3Q Return | 4Q Return |
|------------------|-----------|------------|------------|------------|------------|
| Bottom 25% | 13.54 - 19.24 | 3.13% | 5.19% | 6.82% | 10.38% |
| 25-50% | 19.24 - 22.44 | 1.74% | 4.49% | 8.98% | 11.50% |
| 50-75% | 22.44 - 24.72 | 3.28% | 6.14% | 7.25% | 6.19% |
| Top 25% | 24.72 - 29.11 | 1.83% | 4.49% | 6.87% | 10.35% |
| **Spread (Bottom-Top)** | - | **+1.30%p** | **+0.70%p** | **-0.05%p** | **+0.02%p** |

**Table 5-5: Real-world Estimates-based Spread Summary (Bottom 25% - Top 25%)**

| P/E Type | 1Q Spread | 2Q Spread | 3Q Spread | 4Q Spread |
|---------|-----------|-----------|-----------|-----------|
| Forward Operating | +1.34%p | +1.35%p | +1.44%p | +1.99%p |
| Mixed Operating | +0.73%p | +0.43%p | -0.26%p | -0.16%p |
| TTM Operating | +1.30%p | +0.70%p | -0.05%p | +0.02%p |

**Key Findings:**
- Using actual estimates, spreads **decrease dramatically**
- Forward Operating: +1.99%p (backtesting: +20.68%p, approximately 90% decrease)
- Mixed Operating: -0.16%p (negative, reversal phenomenon)
- TTM Operating: +0.02%p (nearly meaningless)

### 5.4 Market Timing Signal Analysis: P/E Sigma Bands and Market Bottoms

#### 5.4.1 Methodology

Using actual estimates-based daily data, we visualized the time series of three P/E definitions (Mixed Operating [Q(0)+Q'(1)+Q'(2)+Q'(3)], Trailing-like Operating [Q(-3)+Q(-2)+Q(-1)+Q(0)], Forward Operating [Q'(1)+Q'(2)+Q'(3)+Q'(4)]) alongside S&P 500 prices, highlighting periods where each P/E ratio falls outside ±1σ and ±1.5σ ranges based on their respective means and standard deviations.

**Note:** The Trailing-like Operating [Q(-3)+Q(-2)+Q(-1)+Q(0)] used here differs from the TTM Operating used in backtesting. In backtesting, TTM Operating consisted entirely of actuals (Q(-3), Q(-2), Q(-1), Q(0) were all actuals), but in actual estimates-based analysis, Q(0) is the current quarter in progress and may be an estimate. Therefore, it is not completely backward-looking; it is a hybrid of actuals and estimates.

**Analysis Period:** December 2016 - November 2025 (approximately 9 years)
**Data Points:** Daily trading days (approximately 2,200-2,400 points)

#### 5.4.2 Visual Analysis Results

**Figure 5: S&P 500 Price with All P/E Ratios (Highlighting periods outside ±1σ range)**

![Figure 5: S&P 500 Price with All P/E Ratios (±1σ)](output/sp500_price_with_all_pe_sigma.png)

*Three P/E definitions (Mixed Operating [Q(0)+Q'(1)+Q'(2)+Q'(3)], Trailing-like Operating [Q(-3)+Q(-2)+Q(-1)+Q(0)], Forward Operating [Q'(1)+Q'(2)+Q'(3)+Q'(4)]) displayed in separate subplots. Each subplot shows S&P 500 Price (black line) and the corresponding P/E ratio (color-coded line), with periods where P/E falls outside ±1σ range highlighted in red (upper) and blue (lower) shading.*

**Figure 6: S&P 500 Price with All P/E Ratios (Highlighting periods outside ±1.5σ range)**

![Figure 6: S&P 500 Price with All P/E Ratios (±1.5σ)](output/sp500_price_with_all_pe_sigma_1_5.png)

*Same structure highlighting periods outside ±1.5σ range. More stringent criteria for identifying extreme valuation periods.*

#### 5.4.3 Key Finding: Trailing-like Operating P/E's Market Bottom Identification Capability

**Core Discovery:**

Comparing the three P/E definitions, **Trailing-like Operating [Q(-3)+Q(-2)+Q(-1)+Q(0)] P/E falling below -1.5σ effectively identifies major market bottoms**.

**Observed Patterns:**

1. **Late 2018 - Early 2019 Bottom:**
   - Trailing-like Operating P/E fell below -1.5σ
   - Coincided with major S&P 500 price bottom

2. **Early 2020 COVID-19 Bottom:**
   - Trailing-like Operating P/E fell below -1.5σ
   - Coincided with market's sharp decline and subsequent rebound point

3. **Mid-2022 Bottom:**
   - Trailing-like Operating P/E fell below -1.5σ
   - Coincided with market adjustment bottom due to inflation concerns

**Characteristics of Trailing-like Operating P/E:**

- **Composition:** Q(-3) + Q(-2) + Q(-1) + Q(0) = Past 3 quarters actuals + Current quarter estimate
- **Difference from Backtesting's TTM Operating:**
  - Backtesting's TTM Operating: Q(-3), Q(-2), Q(-1), Q(0) were all actuals (completely backward-looking)
  - Actual estimates-based Trailing-like Operating: Q(-3), Q(-2), Q(-1) are actuals, but Q(0) is the current quarter in progress and may be an estimate
- **Features:**
  - Not completely backward-looking; it is a hybrid of actuals and estimates
  - Relatively less affected by estimate errors compared to estimates-based P/E ratios (since past 3 quarters are actuals)
- **Advantage:** Primarily reflects past performance while also incorporating current quarter estimates, favorable for capturing market's excessive pessimism

**Comparison with Other P/E Definitions:**

Quantitative analysis (based on MDD local minima in periods where MDD < -8% before next new high) shows that all three P/E definitions demonstrate alignment with MDD bottoms, but each has different characteristics:

**Table 5-6: P/E -1.5σ Periods and MDD Local Minima Match Rate (±3-day window)**

| P/E Definition | -1.5σ Periods | MDD Minima | Matching Periods | Match Rate |
|----------------|---------------|------------|------------------|------------|
| **Mixed Operating** | 28 | 7 | 6 | **21.4%** |
| **Trailing-like Operating** | 21 | 7 | 7 | **33.3%** |
| **Forward Operating** | 28 | 7 | 6 | **21.4%** |

- **Mixed Operating [Q(0)+Q'(1)+Q'(2)+Q'(3)]:**
  - Match rate: 21.4% (6 out of 28 -1.5σ periods match MDD minima)
  - Composed of current quarter estimate + future 3 quarters estimates, captures bottoms relatively well but has more noise due to more -1.5σ periods

- **Trailing-like Operating [Q(-3)+Q(-2)+Q(-1)+Q(0)]:**
  - Match rate: **33.3%** (7 out of 21 -1.5σ periods match MDD minima, **best performance**)
  - Has the fewest -1.5σ periods (21) and **all MDD minima (7) match with -1.5σ periods**
  - Least noise, most clearly identifies important market bottoms
  - Higher proportion of past actuals makes it relatively less affected by estimate errors

- **Forward Operating [Q'(1)+Q'(2)+Q'(3)+Q'(4)]:**
  - Match rate: 21.4% (6 out of 28 -1.5σ periods match MDD minima)
  - Same match rate as Mixed Operating but has more noise due to more -1.5σ periods
  - Uses only future 4 quarters estimates, making analysis impossible in some periods due to data availability issues

**Practical Implications:**

Periods where Trailing-like Operating P/E falls below -1.5σ represent extreme market pessimism and historically coincide with major bottoms. This suggests the following practical applications:

1. **Market Bottom Identification:** Consider market bottom possibility when Trailing-like Operating P/E falls below -1.5σ
2. **Buying Opportunities:** Explore buying opportunities during extreme undervaluation periods
3. **Risk Management:** Comprehensively evaluate investment opportunities during excessive pessimism periods alongside other indicators

**Caveats:**

- Should not rely on a single indicator but make comprehensive judgments with other indicators
- Falling below -1.5σ does not always mean immediate rebound
- Patterns may break during structural market changes or black swan events

---

## 6. Key Discovery: Backtesting vs Real-world Environment

### 6.1 Correlation Comparison

**Table 6-1: Backtesting vs Real-world Correlation Comparison (Forward Operating, 4Q basis)**

| Environment | Correlation | Sample Size | Data Period |
|-------------|------------|-------------|-------------|
| **Backtesting (Actuals)** | **-0.623** | 9,003 | 1988-2025 (37 years) |
| **Real-world (Estimates)** | **-0.132** | 20,177 | 2016-2025 (8 years) |
| **Difference** | **-0.491** | - | - |
| **Decrease Rate** | **Approximately 79% decrease** | - | - |

**Table 6-2: Backtesting vs Real-world Correlation Comparison (All P/E Types, 4Q basis)**

| P/E Type | Backtesting | Real-world | Difference | Decrease Rate |
|---------|------------|------------|-----------|---------------|
| **Forward Operating** | -0.623 | -0.132 | -0.491 | 79% |
| **Mixed Operating** | -0.532 | -0.086 | -0.446 | 84% |
| **TTM Operating** | -0.234 | -0.087 | -0.147 | 63% |

**Key Findings:**
- All P/E types show **dramatic correlation decrease** in real-world environment
- Forward Operating shows largest decrease rate but still highest absolute value
- In real-world environment, relationship between P/E and future returns becomes nearly meaningless

### 6.2 Spread Comparison

**Table 6-3: Backtesting vs Real-world Spread Comparison (Bottom 25% - Top 25%, 4Q basis)**

| P/E Type | Backtesting | Real-world | Difference | Decrease Rate |
|---------|------------|------------|-----------|---------------|
| **Forward Operating** | +20.68%p | +1.99%p | -18.69%p | 90% |
| **Mixed Operating** | +15.84%p | -0.16%p | -16.00%p | 101% (reversal) |
| **TTM Operating** | +4.16%p | +0.02%p | -4.14%p | 100% |

**Key Findings:**
- Spreads **decrease by 90-100%**
- Mixed Operating and TTM Operating turn negative, showing **reverse effects**
- Forward Operating remains positive but decreases by 90% compared to backtesting

### 6.3 Analysis of Predictive Power Differences

#### 6.3.1 Impact of Estimate Errors

Backtesting uses already-realized actuals, assuming "perfect prediction," but in real-world environment:

1. **Estimate errors affect P/E calculation**
   - If estimates are inaccurate, P/E calculation becomes inaccurate
   - Inaccurate P/E distorts relationship with future returns

2. **Larger estimate errors → greater distortion**
   - If estimates are higher than actual, P/E calculated lower
   - If estimates are lower than actual, P/E calculated higher
   - This distortion weakens predictive power

3. **Result: P/E-based predictive power decreases dramatically**
   - Correlation: -0.623 → -0.132 (79% decrease)
   - Spread: +20.68%p → +1.99%p (90% decrease)

#### 6.3.2 Limitations of Backtesting

Backtesting has the following limitations:

1. **"Perfect prediction" assumption**
   - Uses already-realized actuals
   - Impossible in actual investment environment

2. **Overly optimistic results**
   - Does not consider estimate errors
   - Shows higher predictive power than reality

3. **Difficulty in practical application**
   - Strategies showing good performance in backtesting may differ in real-world environment

### 6.4 What This Means

#### 6.4.1 Risks of Simple P/E-based Judgment

Results using actual estimates have the following implications:

**❌ Approaches to Avoid:**
- "P/E of 25 means overvalued, so sell"
- "P/E of 15 means undervalued, so buy"
- Making investment decisions based solely on P/E numbers

**✅ Recommended Approaches:**
- P/E is only a reference indicator, not an absolute judgment criterion
- Consider estimate accuracy and reliability together
- Judge comprehensively with other indicators (company growth, industry trends, macro environment, etc.)
- High P/E does not necessarily mean risky, and low P/E does not necessarily mean opportunity

#### 6.4.2 Recognizing Limitations of Backtesting Results

This research provides the following important lessons:

1. **Do not blindly trust backtesting results**
   - Strategies showing good performance in backtesting may differ in real-world environment
   - Backtesting that does not consider estimate errors may show overly optimistic results

2. **Importance of multi-faceted analysis**
   - Do not rely solely on a single indicator (P/E), but consider various indicators and information comprehensively
   - Evaluate estimate accuracy and reliability together

3. **Re-examination of investment philosophy**
   - Limitations of simple dichotomous thinking of "overvalued/undervalued"
   - Markets are complex, and a single indicator cannot explain everything

---

## 7. Research Limitations and Implications

### 7.1 Limitations of Backtesting

#### 7.1.1 Limitations of Backtesting Data: Actuals vs Estimates

**Core Problem:**

This research was based on **backtesting using past actuals (Actuals)**. While this was a necessary methodological approach, it contains a fundamental limitation: **in actual investment environments, future estimates (Estimates) must be used**.

**Backtesting Results (Actuals-based):**
- Forward Operating P/E vs 4Q forward return correlation: **-0.623** (37-year data, 9,003 daily samples)
- Bottom 25% vs Top 25% spread: **+20.68%p** (37-year basis)
- P/E < 21 range average return: **+16.03%**
- P/E ≥ 21 range average return: **-4.65%** (loss)

**Real-world Estimates-based Analysis Results (2016-2025, 8 years):**
- Forward Operating P/E vs 4Q forward return correlation: **-0.132** (20,177 daily samples)
- Bottom 25% vs Top 25% spread: **+1.99%p** (4Q basis)
- Mixed Operating P/E spread: **-0.16%p** (negative, reversal phenomenon)
- TTM Operating P/E spread: **+0.02%p** (nearly meaningless)

**Conclusion:**

Using actual estimates, the strong negative correlation (-0.623) and large spread (+20.68%p) found in backtesting **decrease to nearly meaningless levels** in actual investment environments. Specifically:

1. **Correlation decrease:** -0.623 → -0.132 (approximately 79% decrease)
2. **Spread decrease:** +20.68%p → +1.99%p (approximately 90% decrease)
3. **Loss of predictive power:** Mixed Operating and TTM Operating show spreads turning negative, causing reverse effects

This is because **estimate errors** affect P/E calculation, distorting the relationship between P/E and future returns. Backtesting uses already-realized actuals, assuming "perfect prediction," but in real-world environments, estimate uncertainty significantly weakens predictive power.

#### 7.1.2 Sample Size

**Comparison Summary:**

| Criterion | Quarterly | Daily | Superior Method |
|-----------|-----------|-------|-----------------|
| Sample Size | 148 | 9,003 | Daily ✅ |
| Standard Error | ±0.083 | ±0.010 | Daily ✅ |
| Forward Operating Correlation | -0.533 | -0.543 | Daily ✅ |
| Annualization Accuracy | 16.33% vs 15.31% | 15.61% vs 15.31% | **Daily ✅** |
| Matches EPS Update Cycle | ✅ | ❌ | Quarterly ✅ |
| Short-term Noise | Low | High | Quarterly ✅ |

**Conclusions:**

1. **Daily data useful as validation tool:**
   - 60x more samples confirm quarterly findings
   - Dramatically improved statistical reliability

2. **Quarterly data recommended for practice:**
   - Matches EPS update cycle (quarterly)
   - Annualization more accurately matches actual
   - Clean signal without short-term noise

3. **Core findings identical:**
   - **P/E ≈ 21 as critical threshold** (both methods agree)
   - Forward Operating superior performance (both methods agree)
   - Trailing P/E useless (both methods agree)

### 7.2 Implications for Real-world Investment Environment

#### 7.2.1 Estimate Accuracy Dependency

The "superior predictive power of Forward Operating P/E" and "P/E ≈ 21 threshold" presented in this research are **valid only in backtesting environments**, and have the following limitations in actual investment:

1. **Estimate accuracy dependency:** Predictive power increases with estimate accuracy, but decreases dramatically with large estimate errors
2. **Difficulty in practical application:** Strong signals found in backtesting decrease to nearly meaningless levels in real-world environments
3. **Limitation of differentiation:** The "superiority of Forward Operating" emphasized in this research is valid only in actuals environments, and shows little difference from Mixed Operating and TTM Operating in estimates environments

#### 7.2.2 Model Limitations

**Prediction Accuracy Limitations:**
- Even in backtesting, accuracy is only 61-63% (37-39% error rate)
- Expected to be even lower in real-world environments

**Black Swan Events:**
- Extreme events like 2008 Financial Crisis, 2020 COVID-19 cannot be captured by models
- During such periods, P/E may become meaningless (EPS drops sharply)

**Structural Changes:**
- Future may differ from past
- AI revolution, rate normalization could alter P/E structure

### 7.3 Risks of Simple P/E-based Judgment

#### 7.3.1 Academic Significance of This Research

This research makes the following academic contributions:

1. **Empirically demonstrates differences between backtesting and real-world investment environments**
   - Proves that strong signals found in backtesting may weaken in real-world environments
   - Quantifies the impact of estimate errors on predictive model performance

2. **Clearly presents limitations of P/E indicators**
   - Shows limitations when P/E is used alone
   - Proves that estimates-based P/E has significantly lower predictive power than actuals-based

3. **Warns about investment decision-making**
   - Risks of relying on a single indicator for investment decisions
   - Emphasizes not to blindly trust backtesting results

#### 7.3.2 Practical Significance of This Research

This research provides the following important lessons for practical investors:

1. **Recognizing limitations of backtesting results**
   - Strategies showing good performance in backtesting may differ in real-world environments
   - Backtesting that does not consider estimate errors may show overly optimistic results

2. **Importance of multi-faceted analysis**
   - Do not rely solely on a single indicator (P/E), but consider various indicators and information comprehensively
   - Evaluate estimate accuracy and reliability together

3. **Re-examination of investment philosophy**
   - Limitations of simple dichotomous thinking of "overvalued/undervalued"
   - Markets are complex, and a single indicator cannot explain everything

4. **Exception: Trailing-like Operating P/E as market bottom indicator**
   - Despite overall limitations, Trailing-like Operating [Q(-3)+Q(-2)+Q(-1)+Q(0)] P/E falling below -1.5σ effectively identifies market bottoms
   - Trailing-like Operating is a hybrid of past 3 quarters actuals and current quarter estimate, not completely backward-looking while being relatively less affected by estimate errors compared to estimates-based P/E (differs from backtesting's TTM Operating)
   - Useful as a reference indicator for capturing extreme market pessimism periods
   - However, should not rely on a single indicator but make comprehensive judgments with other indicators

### 7.4 Future Research Directions

1. **Estimate accuracy analysis:** Quantify the impact of estimate errors on P/E predictive power
2. **Estimate correction models:** Explore ways to improve predictive power by correcting systematic errors in estimates
3. **Real-time validation:** Re-evaluate predictive power through long-term real-world validation using actual estimates

---


## 8. Conclusion: The True Significance of This Research

### 8.1 Research Summary

This study compared three Operating Earnings-based P/E definitions using quarterly (148) and daily (9,003) data and discovered:

1. **Operating vs As Reported selection matters:**
   - Operating Earnings shows superior predictive power across all periods
   - 12-month correlation: -0.620 vs -0.590 (difference 0.03)
   - One-time items distort statistics (especially 2000 Dot-com Bubble, 2008 Financial Crisis, 2020 Pandemic)

2. **Backtesting shows Forward Operating [Q'(1)+Q'(2)+Q'(3)+Q'(4)] is superior:**
   - Quarterly: 63.4% prediction accuracy, Low P/E beats High P/E by 15.31%p
   - Daily: 62.3% prediction accuracy, Low P/E beats High P/E by 14.37%p
   - Consistent superiority confirmed across both methods

3. **Real-world estimates environment shows predictive power decreases dramatically:**
   - Correlation: -0.623 → -0.132 (79% decrease)
   - Spread: +20.68%p → +1.99%p (90% decrease)
   - Mixed Operating and TTM Operating show negative spreads (reverse effects)

4. **Trailing-like Operating P/E shows potential as market bottom indicator:**
   - When Trailing-like Operating [Q(-3)+Q(-2)+Q(-1)+Q(0)] P/E falls below -1.5σ, it effectively identifies major market bottoms
   - Trailing-like Operating is a hybrid of past 3 quarters actuals and current quarter estimate, not completely backward-looking while being relatively less affected by estimate errors compared to estimates-based P/E (differs from backtesting's TTM Operating)
   - Useful as a reference indicator for capturing extreme market pessimism periods

### 8.2 The True Significance of This Research

This research does not prove that **market timing using P/E is possible**, but rather demonstrates **the risks of simple P/E-based judgment**.

**Key Discovery:**

The finding that P/E ratios showing strong predictive power in backtesting decrease to nearly meaningless levels when using actual estimates in a real-world environment suggests that investors should not rely on a single indicator but take a more cautious and comprehensive approach.

**Important Warning:**

The backtesting results of this research are from an **ideal environment using past actuals**. Analysis using actual estimates shows correlations decreasing dramatically from -0.623 to -0.132, and spreads decreasing from +20.68%p to +1.99%p, becoming nearly meaningless.

Therefore, blindly trusting the backtesting results of this research and making investment decisions based on the simple logic that "high P/E means overvalued and risky, low P/E means undervalued opportunity" is dangerous. P/E is only a reference indicator, and estimate accuracy and reliability must be considered together, along with other indicators, for comprehensive judgment.

**Exception:**

However, one notable exception is **Trailing-like Operating [Q(-3)+Q(-2)+Q(-1)+Q(0)] P/E's ability to identify market bottoms when falling below -1.5σ**. Trailing-like Operating is a hybrid of past 3 quarters actuals and current quarter estimate, not completely backward-looking while being relatively less affected by estimate errors compared to estimates-based P/E (differs from backtesting's TTM Operating). This suggests that despite overall limitations, specific P/E definitions may have specific use cases (market bottom identification). However, this should also not be relied upon as a single indicator but used comprehensively with other indicators.

**The true value of this research is to demonstrate the differences between backtesting and real-world investment environments and to warn of the risks of relying on a single indicator for investment decisions.**

---

## References

This research is based purely on empirical data analysis and does not directly reference external academic literature.

**Data Sources:**
- **Price Data:** Yahoo Finance API (yfinance Python library) - S&P 500 Index (^GSPC)
- **EPS Data:** S&P Global - S&P Dow Jones Indices
  - Source: [S&P 500 EPS Estimates](https://www.spglobal.com/spdji/en/documents/additional-material/sp-500-eps-est.xlsx)
  - Provider: S&P Dow Jones Indices LLC
- **Estimates Data:** Actual estimates data extracted from FactSet PDFs (2016-2025)
- **Analysis Period:** December 1988 - September 2025 (37 years, 148 quarters)

**Analysis Tools:**
- Python 3.11+
- pandas, numpy, matplotlib
- Custom-developed analysis scripts

---

## Appendix A: Chart Descriptions

This paper includes 6 main charts:

**Figure 1: Operating vs As Reported Earnings (1988-2025)**
- 4 panels: Forward 4Q EPS, Forward P/E, EPS difference (M-N), P/E difference (M-N)
- Crisis periods shaded (2000 Dot-com Bubble, 2008 Financial Crisis, 2020 Pandemic)
- Purpose: Visualize importance of Operating Earnings selection
- Location: Section 2.5.3

**Figures 2-1, 2-2, 2-3: 3 Operating P/E Quarterly Mean Reversion Analysis**
- Top panel: 30-year P/E time series (mean and ±1σ bands)
- Bottom 4 panels: P/E Z-score vs 1Q/2Q/3Q/4Q return scatter plots + regression lines
- Purpose: Confirm basic patterns with quarterly data (148 observations)
- Comparison: Forward Operating (best) > Mixed Operating > TTM Operating
- Location: Section 4.1.4

**Figure 3: Forward Operating Daily Mean Reversion Analysis**
- Structure: Same as Figure 2-1
- Purpose: Validation with daily data (9,003 analysis samples, 60x increase)
- Location: Section 4.3.3

**Figure 4: Forward Operating Correlation (Daily Data)**
- P/E vs 1-year return correlation visualization
- Purpose: Reconfirm strong negative correlation with 9,003 samples
- Location: Section 4.3.5

**Figure 5: S&P 500 Price with All P/E Ratios (Highlighting periods outside ±1σ range)**
- 3 subplots: Each displays Mixed Operating [Q(0)+Q'(1)+Q'(2)+Q'(3)], Trailing-like Operating [Q(-3)+Q(-2)+Q(-1)+Q(0)], Forward Operating [Q'(1)+Q'(2)+Q'(3)+Q'(4)] P/E alongside S&P 500 Price
- Each subplot highlights periods where P/E falls outside ±1σ range in red (upper) and blue (lower) shading
- Purpose: Visualize time-series patterns of three P/E definitions and their relationship with market prices
- Location: Section 5.4.2

**Figure 6: S&P 500 Price with All P/E Ratios (Highlighting periods outside ±1.5σ range)**
- Same structure as Figure 5 highlighting periods outside ±1.5σ range
- Purpose: Identify extreme valuation periods with more stringent criteria, particularly confirming Trailing-like Operating P/E's market bottom identification capability
- Location: Section 5.4.2

---

## Appendix B: Code Reproducibility

All analyses in this research were implemented in Python, organized into two groups:

### **Quarterly Analysis Scripts:**

1. `compare_pe_definitions.py`: Compare 3 Operating P/E definitions and generate charts
2. `calculate_probabilities.py`: Calculate prediction accuracy
3. `calculate_actual_returns.py`: Calculate actual return differentials
4. `pe_quartile_analysis.py`: Quartile analysis and investment guide
5. `annualized_comparison_all.py`: Compare annualized return differentials
6. `compare_all_pe_quartiles.py`: Compare 10-year vs 37-year quartiles
7. `trailing_pe_test.py`: TTM Operating validation
8. `calculate_pe_win_probability.py`: Calculate win probability matrix by zone×period

### **Daily Analysis Scripts (60x Sample Size Enhancement):**

1. `visualize_pe_mean_reversion_daily.py`: Generate daily mean reversion charts (Figure 3)
2. `visualize_pe_correlations.py`: P/E vs return correlation charts (Figure 4)

### **Operating vs As Reported Comparison Scripts:**

1. `create_operating_vs_reported_chart.py`: Generate Figure 1 (37-year full comparison)

### **Real-world Estimates Validation Scripts:**

1. `create_true_daily_pe.py`: Calculate daily P/E based on actual estimates
2. `recalculate_performance_daily.py`: Performance analysis based on actual estimates
3. `analyze_pe_flexible.py`: Flexible quarter range P/E calculation (Q[0:4], Q[1:5], Q[-3:1], etc., generates Section 5.4 data)

### **Market Timing Signal Analysis Scripts (Section 5.4.3):**

1. `calculate_pe_mdd_match_rate.py`: Calculate match rate between P/E -1.5σ periods and MDD local minima (±3-day window, generates Table 5-6 data)
2. `visualize_pe_mdd_alignment.py`: Generate visualization charts for MDD bottoms and P/E -1.5σ periods

**Reproduction Environment:**
- Python 3.11+
- pandas, numpy, matplotlib, yfinance, scipy, openpyxl, Pillow, boto3

**Data:**
- Price data: Public (Yahoo Finance)
- EPS data: Public (S&P Global - [sp-500-eps-est.xlsx](https://www.spglobal.com/spdji/en/documents/additional-material/sp-500-eps-est.xlsx))
- Estimates data: Extracted from FactSet PDFs

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

**Disclaimer:** Past performance does not guarantee future results. Backtesting results may differ from real-world investment environments, and predictive power decreases significantly when using actual estimates in analysis. Proper risk management and diversification are recommended.

---

**END OF PAPER**

© 2025 Seung-Gu Kang (강승구). All rights reserved.

