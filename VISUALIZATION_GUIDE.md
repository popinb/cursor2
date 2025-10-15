# 📊 **Advanced Visualizations Guide**

## 🎨 **Beautiful, Scalable Charts for Any Number of Metrics**

Cell 10 generates **8 comprehensive visualizations** that automatically scale to any number of metrics, samples, and metric types.

---

## 📈 **Visualizations Created**

### **1. 🔥 Sample vs Metric Performance Heatmap**

**What it shows:**
- Score for each sample-metric combination
- Color-coded: Red (low) → Yellow (medium) → Green (high)
- Exact score values displayed in each cell

**How to read:**
- **Rows:** Individual samples (1, 2, 3, 4...)
- **Columns:** Metrics (accuracy_check, helpfulness_rating, etc.)
- **Color intensity:** Darker green = better performance
- **Hover:** See exact scores

**Insights to look for:**
- ✅ Which samples perform well across all metrics (full green row)
- ❌ Which samples struggle (red row)
- 📊 Which metrics are consistently hard/easy (column patterns)
- 🔍 Clusters of red areas = systematic issues

**Scales automatically:** Works with 2-1000 samples, 2-50 metrics

---

### **2. 📈 Metric Performance Dashboard**

**Two charts side-by-side:**

#### **Left: Pass Rate by Metric**
- Bar chart showing % of samples passing each metric
- Color gradient: Red (0%) → Yellow (50%) → Green (100%)
- Percentages labeled on bars

**Insights:**
- Which metrics have highest failure rates
- Which metrics are too easy (100% pass) or too hard (0% pass)
- Ideal: 60-90% pass rate (discriminating but achievable)

#### **Right: Average Score by Metric**
- Bar chart with error bars showing score variability
- Higher bars = better average performance
- Error bars = consistency (small = consistent, large = variable)

**Insights:**
- Overall metric difficulty
- Score variability (consistent vs. inconsistent performance)
- Metrics needing threshold adjustment

**Scales automatically:** 1-100 metrics

---

### **3. 🎻 Score Distribution (Violin Plots)**

**What it shows:**
- Complete distribution of scores for each metric
- Shape shows where scores cluster
- Box plot inside shows quartiles
- Individual points displayed

**How to read:**
- **Width:** How many scores at that level (wider = more common)
- **Box:** Middle 50% of scores (interquartile range)
- **Line through box:** Median score
- **Dots:** Individual sample scores

**Insights to look for:**
- **Bimodal distribution:** Two peaks = metric splits samples into two groups
- **Narrow violin:** All scores similar (low variance)
- **Wide violin:** Scores spread out (high variance)
- **Bottom-heavy:** Most scores low (hard metric)
- **Top-heavy:** Most scores high (easy metric)

**Example interpretations:**
- Narrow at top = all samples score well (good!)
- Wide spread = metric distinguishes quality levels (good!)
- Cluster at bottom = metric too hard or samples uniformly bad

**Scales automatically:** 1-100 metrics

---

### **4. 📋 Sample Performance Scorecard**

**What it shows:**
- Horizontal bar chart of pass rate per sample
- Sorted from worst (top) to best (bottom)
- Color gradient showing performance level

**How to read:**
- **Length of bar:** Pass rate percentage
- **Color:** Red (poor) → Yellow (okay) → Green (good)
- **Hover:** Shows both pass rate and average score

**Insights to look for:**
- **Top samples (red/short bars):** Problem cases needing attention
- **Bottom samples (green/long bars):** High-quality examples
- **Gaps:** Big difference between best and worst samples
- **Clustering:** Many samples at similar performance level

**Use cases:**
- Identify samples for manual review
- Find examples of good vs bad responses
- Prioritize sample improvements

**Scales automatically:** 1-10,000 samples

---

### **5. 🔗 Metric Correlation Matrix**

**What it shows:**
- How metric scores correlate with each other
- Blue = negative correlation, Red = positive correlation
- Values from -1 to +1

**How to read:**
- **+1 (dark red):** Perfect positive correlation (metrics always agree)
- **0 (white):** No correlation (metrics independent)
- **-1 (dark blue):** Perfect negative correlation (metrics oppose each other)
- **Diagonal:** Always 1.0 (metric correlates perfectly with itself)

**Insights to look for:**
- **High positive correlation (>0.8):** Metrics may be redundant
  - Example: clarity_score + helpfulness_rating often correlated
  - Action: Consider combining or removing one

- **Low correlation (<0.3):** Metrics measure different aspects (good!)
  - Example: accuracy_check + tone_professionalism independent
  - Action: Keep both - they provide unique value

- **Negative correlation:** Unusual, investigate why
  - Example: If completeness negatively correlates with clarity
  - Possible interpretation: Verbose responses score high on completeness, low on clarity

**Use cases:**
- Optimize metric set (remove redundant metrics)
- Validate metrics measure different aspects
- Discover unexpected relationships

**Scales automatically:** 2-50 metrics

---

### **6. ✅❌ Pass/Fail Breakdown**

**What it shows:**
- Stacked bar chart with pass (green) and fail (red) counts
- Shows absolute numbers, not percentages

**How to read:**
- **Green section:** Number of samples passing
- **Red section:** Number of samples failing
- **Total bar height:** Total samples evaluated
- **Hover:** Exact counts

**Insights to look for:**
- **All green:** Metric too easy or samples too good
- **All red:** Metric too hard or samples too bad
- **Mixed:** Good discrimination (metric is working)
- **Compare bar heights:** Relative difficulty across metrics

**Use cases:**
- Quick visual assessment of metric effectiveness
- Identify metrics needing threshold adjustment
- Compare metric strictness

**Scales automatically:** 1-100 metrics

---

### **7. 📊 Metric Type Analysis**

**Two charts:**

#### **Left: Pie Chart - Evaluations by Metric Type**
- Shows proportion of evaluations by type (binary/scale/percentage)
- Helps understand metric mix

**Right: Bar Chart - Pass Rate by Type**
- Compares performance across metric types
- Color gradient based on pass rate

**Insights to look for:**
- **Metric type balance:** Are most metrics one type?
  - Ideal: Mix of types for comprehensive evaluation
  
- **Type performance differences:**
  - Binary metrics pass rate >> Scale metrics = thresholds misaligned
  - Percentage metrics fail more = may need lower thresholds

**Use cases:**
- Balance your metric portfolio
- Adjust thresholds by metric type
- Understand evaluation approach

**Scales automatically:** Works with any mix of metric types

---

### **8. 📈 Summary Statistics Table**

**What it shows:**
- Text-based comprehensive statistics
- Overall performance
- Per-metric breakdown
- Per-sample breakdown

**Sections:**

#### **Overall Performance:**
```
Total Evaluations: 20
Passed: 13 (65%)
Failed: 7 (35%)
Average Score: 3.45
Score Std Dev: 1.23
```

#### **By Metric:**
```
✅ accuracy_check              - Pass: 3/4 (75.0%) | Avg: 0.75
⚠️ completeness_percentage     - Pass: 2/4 (50.0%) | Avg: 62.5
❌ helpfulness_rating          - Pass: 1/4 (25.0%) | Avg: 2.25
```

Icons:
- ✅ Pass rate ≥70% (good)
- ⚠️ Pass rate 50-69% (okay)
- ❌ Pass rate <50% (needs attention)

#### **By Sample:**
```
✅ Sample 1         - Pass: 5/5 (100%)
⚠️ Sample 2         - Pass: 3/5 (60%)
❌ Sample 4         - Pass: 0/5 (0%)
```

**Use cases:**
- Quick numerical summary
- Copy/paste into reports
- Identify problem areas at a glance

---

## 🎯 **How to Use These Visualizations**

### **For Product Managers:**

**Weekly Review:**
1. Check **Sample Performance Scorecard** - identify problem responses
2. Review **Pass/Fail Breakdown** - which metrics failing most
3. Look at **Metric Type Analysis** - is evaluation balanced?

**Monthly Strategy:**
1. Analyze **Metric Correlation Matrix** - remove redundant metrics
2. Study **Violin Plots** - adjust thresholds for better discrimination
3. Review **Heatmap** - identify systematic patterns

### **For Data Scientists:**

**Model Evaluation:**
1. **Heatmap:** Quick overview of model strengths/weaknesses
2. **Violin Plots:** Understand score distributions
3. **Correlation Matrix:** Validate metric independence

**Metric Optimization:**
1. **Pass Rate charts:** Identify metrics needing threshold adjustment
2. **Distribution plots:** Ensure metrics discriminate effectively
3. **Summary stats:** Track improvements over time

### **For QA/Testing:**

**Issue Identification:**
1. **Sample Scorecard:** Prioritize samples for manual review
2. **Pass/Fail Breakdown:** Focus on metrics with high failure rates
3. **Heatmap:** Find clusters of failures

**Trend Analysis:**
1. Run evaluations regularly
2. Compare visualizations across runs
3. Track improvement over time

---

## 💡 **Interpretation Guide**

### **Good Patterns to See:**

✅ **Heatmap:**
- Gradient from red (bad samples) to green (good samples)
- Clear separation between high and low performers

✅ **Violin Plots:**
- Smooth distributions covering full score range
- Some variance but not extreme

✅ **Correlation Matrix:**
- Low to moderate correlations (0.3-0.7)
- Indicates metrics measure different aspects

✅ **Pass Rates:**
- 60-80% pass rate (good discrimination)
- Consistent across similar metrics

---

### **Red Flags to Watch:**

❌ **All metrics 100% pass:**
- Metrics too easy OR samples too good
- Action: Increase thresholds or add harder metrics

❌ **All metrics 0% pass:**
- Metrics too hard OR samples too bad
- Action: Decrease thresholds or improve samples

❌ **Very high correlation (>0.95):**
- Redundant metrics
- Action: Remove one or combine

❌ **Bimodal distributions:**
- May indicate two distinct sample types
- Action: Investigate what splits samples

❌ **All scores at extremes (0 or max):**
- Metric not discriminating effectively
- Action: Refine metric or adjust scale

---

## 🔧 **Customization Options**

### **Colors:**
All color schemes can be customized in the code:
- **Heatmaps:** RdYlGn (Red-Yellow-Green)
- **Correlations:** RdBu (Red-Blue)
- **Gradients:** Viridis, RdYlGn, etc.

### **Size:**
Charts auto-scale but can be adjusted:
```python
height=max(400, len(data) * 40)  # Scales with data size
```

### **Thresholds:**
Adjust color breakpoints:
```python
colorscale=[
    [0.0, '#d73027'],   # Red threshold
    [0.5, '#fee090'],   # Yellow threshold
    [1.0, '#1a9850']    # Green threshold
]
```

---

## 📊 **When to Use Each Chart**

| Question | Best Chart |
|----------|-----------|
| Which samples need review? | Sample Scorecard (#4) |
| Which metrics are failing? | Pass/Fail Breakdown (#6) |
| Are metrics redundant? | Correlation Matrix (#5) |
| How are scores distributed? | Violin Plots (#3) |
| What's the overall pattern? | Heatmap (#1) |
| How difficult are metrics? | Metric Dashboard (#2) |
| Is my metric mix balanced? | Type Analysis (#7) |
| What are the exact numbers? | Summary Table (#8) |

---

## 🎨 **Example Insights**

### **Scenario 1: New Evaluation Run**

**Start with:**
1. Summary Table (#8) - overall pass rate
2. Heatmap (#1) - visual overview
3. Sample Scorecard (#4) - identify worst samples

**Then:**
4. Pass/Fail Breakdown (#6) - which metrics failing

**Deep dive:**
5. Violin Plots (#3) - why metrics failing
6. Correlation Matrix (#5) - are metrics valid

### **Scenario 2: Metric Optimization**

**Analyze:**
1. Violin Plots (#3) - score distributions
2. Metric Dashboard (#2) - pass rates + averages
3. Correlation Matrix (#5) - redundancy

**Adjust:**
- Thresholds based on distributions
- Remove highly correlated metrics (>0.85)
- Add new metrics for gaps

### **Scenario 3: Sample Quality Assessment**

**Focus on:**
1. Sample Scorecard (#4) - rank samples
2. Heatmap (#1) - sample × metric patterns
3. Summary Table (#8) - exact sample scores

**Actions:**
- Manual review of bottom 20% samples
- Analyze top 20% for patterns
- Adjust samples based on findings

---

## ✅ **Best Practices**

1. **Run after every evaluation** - Cell 10 runs automatically after Cell 7

2. **Save visualizations** - Right-click → Save as PNG for reports

3. **Track over time** - Compare visualizations across runs to see trends

4. **Share with team** - Export as HTML or PNG for presentations

5. **Iterate on metrics** - Use insights to refine your metric set

6. **Document findings** - Note patterns and action items

7. **Regular review** - Weekly quick check, monthly deep dive

---

## 🎉 **Summary**

**8 Charts. Any number of metrics. Beautiful insights.**

All visualizations are:
- ✅ **Scalable:** Work with 2-1000 samples, 2-50 metrics
- ✅ **Interactive:** Hover for details, zoom, pan
- ✅ **Beautiful:** Professional quality for presentations
- ✅ **Informative:** Each chart answers specific questions
- ✅ **Automatic:** Generated from your results_df

**No configuration needed - just run Cell 10!** 🚀
