# 📊 **MLflow Dashboard Guide**

## 🎨 **Beautiful Experiment Tracking for Any Number of Custom Metrics**

Cell 9 creates a comprehensive MLflow dashboard that tracks your evaluations over time with gorgeous visualizations that automatically scale to any number of custom metrics!

---

## 🎯 **What It Does**

**Tracks your evaluation experiments:**
- ✅ Run-to-run comparisons
- ✅ Performance trends over time
- ✅ Latest vs best performance
- ✅ Model comparisons
- ✅ Improvement tracking
- ✅ Historical analysis

**Works with ANY number of custom metrics:**
- Automatically detects all your metrics
- Scales visualizations dynamically
- No configuration needed!

---

## 📈 **The 7 Visualizations**

### **1. 🔥 Run-to-Run Performance Heatmap**

**What it shows:**
- Matrix with runs (rows) × metrics (columns)
- Each cell = pass rate for that run + metric
- Color-coded: Red (0%) → Yellow (50%) → Green (100%)
- Latest run at top

**How to read:**
- **Vertical patterns:** How a single metric performs across runs
- **Horizontal patterns:** How all metrics perform in one run
- **Color trends:** Green spreading = improvement over time
- **Red clusters:** Consistent problem areas

**Insights:**
- Track which metrics are getting better/worse
- Identify consistently difficult metrics
- See if latest run improved across the board
- Spot anomalies (one run much worse/better)

**Example:**
```
                accuracy  helpfulness  completeness  tone  clarity
10/15 08:30     🟢 85%    🟢 80%       🟡 65%       🟢 75%  🟢 90%
10/14 14:20     🟢 80%    🟡 75%       🔴 45%       🟢 70%  🟢 85%
10/13 09:15     🟡 70%    🟡 65%       🔴 40%       🟡 60%  🟢 80%
```

**Scalability:** Works with 2-100 runs, 2-50 metrics

---

### **2. 📈 Metric Evolution Over Time**

**What it shows:**
- Line chart with time on X-axis
- One line per metric showing pass rate trend
- Markers at each run
- Reference lines at 70% (good) and 50% (okay)

**How to read:**
- **Upward trend:** Metric improving over time ✅
- **Downward trend:** Metric declining ⚠️
- **Flat line:** Consistent performance
- **Spikes:** Anomalies or experiments to investigate
- **Lines above 70%:** Good performance
- **Lines below 50%:** Needs attention

**Insights:**
- **All lines trending up:** System improving! 🎉
- **One line declining while others improve:** Specific metric issue
- **Volatile line:** Inconsistent metric or varying sample quality
- **Converging lines:** Metrics becoming more similar

**Use cases:**
- Weekly progress tracking
- A/B test analysis (compare before/after)
- Identify which improvements worked
- Spot regressions quickly

**Scalability:** 2-100 runs, 2-50 metrics (color-coded lines)

---

### **3. 🏆 Latest vs Best Performance Comparison**

**What it shows:**
- Grouped bar chart with 2 bars per metric
- Blue = Latest run
- Green = Best historical run
- Shows both pass rate and average score

**How to read:**
- **Blue = Green:** Latest run matches best (excellent!)
- **Blue < Green:** Latest run worse than historical best (regression?)
- **Blue > Green:** Latest run is new best! (celebration!)

**Insights:**
- **Latest matches best across all metrics:** Consistent quality ✅
- **Latest below best on all metrics:** Something changed (investigate)
- **Mixed results:** Some metrics improved, others declined
- **New bests:** Identify what changed to replicate success

**Use cases:**
- Validate that improvements stick
- Catch regressions before deployment
- Celebrate new records
- Understand if you're at a plateau

**Scalability:** Any number of metrics (side-by-side bars)

---

### **4. 🤖 Model Comparison**

**What it shows:**
- Grouped bars comparing different LLM models
- Average pass rate per metric per model
- Only appears if you've tested multiple models

**How to read:**
- **One model consistently higher:** Better overall judge
- **Mixed results:** Some models better at specific metric types
- **Small differences (<5%):** Models roughly equivalent

**Insights:**
- **GPT-4 vs Claude comparison**
- **Databricks vs OpenAI models**
- **Cost vs quality tradeoff** (GPT-4o-mini vs GPT-4o)
- **Metric-specific strengths** (e.g., GPT-4 better at accuracy, Claude better at tone)

**Example:**
```
Metric: accuracy_check
  GPT-4o:      85% 🟢
  GPT-4o-mini: 78% 🟡
  Claude:      82% 🟢
  
Metric: tone_professionalism
  GPT-4o:      75% 🟡
  GPT-4o-mini: 70% 🟡
  Claude:      88% 🟢  ← Claude best for tone!
```

**Scalability:** 2-10 models, any number of metrics

---

### **5. 📊 Improvement Tracking**

**What it shows:**
- Bar chart showing change from first run to latest run
- Green bars = improvement (positive change)
- Red bars = decline (negative change)
- Shows exact percentage point change

**How to read:**
- **All green:** System has improved across the board! 🎉
- **All red:** System has declined (investigate why!)
- **Mixed:** Some metrics improved, others need work
- **Large green bars:** Biggest improvements (what did you do right?)
- **Large red bars:** Biggest declines (what changed?)

**Insights:**
- Track long-term progress (first run vs now)
- Identify which metrics are hardest to improve
- Celebrate wins (metrics with +20% improvement!)
- Prioritize work (focus on red bars)

**Example:**
```
completeness:      +25% 🟢 (40% → 65%)  ← Great improvement!
accuracy:          +15% 🟢 (70% → 85%)
helpfulness:       +10% 🟢 (65% → 75%)
clarity:            +5% 🟢 (80% → 85%)
tone:               -3% 🔴 (75% → 72%)  ← Slight decline
```

**Use cases:**
- Monthly reviews (show stakeholders progress)
- Validate that changes are working
- Identify stagnant metrics
- Celebrate team wins!

**Requires:** At least 3 runs

**Scalability:** Any number of metrics

---

### **6. Latest Run Summary (Text)**

**What it shows:**
- Detailed statistics for the most recent run
- Run ID, model used, sample count
- Timestamp and duration
- Overall pass rate
- Per-metric breakdown with icons

**How to read:**
```
🆔 Run ID: a1b2c3d4...
🤖 Model: gpt-4o
📊 Samples: 20
📅 Time: 2025-10-15 14:30:15
⏱️ Duration: 145.2s

🎯 Overall Pass Rate: 72.5%

📊 Metric Performance:
   ✅ accuracy_check              - Pass: 85.0% | Avg: 0.85
   ✅ clarity_score               - Pass: 80.0% | Avg: 4.20
   ⚠️ completeness_percentage     - Pass: 65.0% | Avg: 67.50
   ❌ tone_professionalism        - Pass: 45.0% | Avg: 0.45
```

**Icons:**
- ✅ ≥70% pass rate (good)
- ⚠️ 50-69% pass rate (needs attention)
- ❌ <50% pass rate (critical)

**Use cases:**
- Quick health check after run
- Copy/paste into reports
- Identify immediate issues

---

### **7. Experiment Summary Statistics (Text)**

**What it shows:**
- Overall experiment metadata
- Total number of runs
- Date range (first to latest)
- Number of metrics tracked
- Best and average performance

**Example:**
```
📊 MLFLOW EXPERIMENT SUMMARY
====================================
🆔 Experiment: /Users/name@company.com/llm_evaluation_experiment
📁 Experiment ID: 123456789
📊 Total Runs: 15
📅 First Run: 2025-10-01 09:00:00
📅 Latest Run: 2025-10-15 14:30:15
📊 Metrics Tracked: 5

🏆 Best Overall Pass Rate: 85.2%
📊 Average Overall Pass Rate: 72.4%
```

**Use cases:**
- Understand experiment history
- Track long-term trends
- Report total testing effort

---

## 🎯 **How to Use the Dashboard**

### **First Run:**
When you first run Cell 9:
- Shows summary of single run
- Limited visualizations (need multiple runs for trends)
- Baseline established!

### **After 2-3 Runs:**
- Run-to-run heatmap appears
- Evolution chart shows trends
- Latest vs best comparison available
- Can start seeing patterns

### **After 5+ Runs:**
- Full dashboard with all charts
- Clear trends visible
- Statistical significance
- Rich historical analysis

### **After 10+ Runs:**
- Comprehensive tracking
- Model comparisons (if used multiple models)
- Long-term improvement visible
- Data-driven optimization

---

## 💡 **Interpretation Guide**

### **Healthy Patterns:**

✅ **Heatmap:**
- Gradual greening from bottom (old) to top (new)
- Few red areas
- Consistent or improving performance

✅ **Evolution Chart:**
- Lines trending upward
- Reduced volatility over time
- Most metrics above 70% line

✅ **Improvement Tracking:**
- Mostly green bars
- Positive overall trend
- No major red bars

---

### **Warning Signs:**

⚠️ **Heatmap:**
- Red spreading from bottom to top (declining!)
- Latest run (top) has more red than previous runs
- One column entirely red (metric always fails)

⚠️ **Evolution Chart:**
- Lines trending downward (regression!)
- Increasing volatility (inconsistency)
- All lines below 50% (system not working)

⚠️ **Improvement Tracking:**
- All or mostly red bars (system declined)
- Large negative changes (something broke)

---

## 🔧 **Optimization Workflows**

### **Workflow 1: Metric Tuning**

**Goal:** Adjust thresholds for optimal discrimination

**Steps:**
1. Run evaluation → Check pass rates in Latest Run Summary
2. Look at Evolution Chart:
   - Metrics at 100%? → Increase threshold
   - Metrics at 0%? → Decrease threshold
   - Metrics at 60-80%? → Perfect! ✅
3. Adjust thresholds in CSV
4. Run again and compare

**Look for:** Metrics settling into 60-80% range over multiple runs

---

### **Workflow 2: Model Selection**

**Goal:** Choose best LLM judge for your use case

**Steps:**
1. Run same samples with different models (GPT-4o, Claude, etc.)
2. Check Model Comparison chart
3. Analyze:
   - Overall best model
   - Metric-specific strengths
   - Cost vs quality tradeoff
4. Select model based on priorities

**Look for:**
- Consistent winner across metrics
- Cost-effective option with acceptable quality
- Model strengths matching your priority metrics

---

### **Workflow 3: Sample Quality Improvement**

**Goal:** Improve low-performing samples

**Steps:**
1. Run evaluation
2. Check Cell 10 Sample Scorecard (current run detail)
3. Note worst-performing samples
4. Improve those samples
5. Run again
6. Check Improvement Tracking chart
7. Confirm improvements in Latest vs Best chart

**Look for:**
- Green bars in Improvement Tracking
- Latest matching or exceeding Best
- Upward trend in Evolution Chart

---

### **Workflow 4: A/B Testing Changes**

**Goal:** Test if a change improved results

**Steps:**
1. Establish baseline (run 2-3 times for consistency)
2. Make your change (new rubrics, different GT, etc.)
3. Run 2-3 times with change
4. Compare in Evolution Chart:
   - Clear jump after change? → Success! ✅
   - Decline after change? → Revert
   - No change? → Inconclusive
5. Validate with Improvement Tracking

**Look for:**
- Step-change in Evolution Chart at change point
- Sustained improvement (not just one-time spike)
- Improvement across multiple metrics (not just one)

---

## 📊 **Real-World Examples**

### **Example 1: Weekly Progress Tracking**

**Scenario:** PM wants weekly update on system quality

**Use:**
1. Check Latest Run Summary → Overall pass rate
2. Check Improvement Tracking → Change from last week
3. Check Evolution Chart → Trend direction
4. Screenshot and add to report

**Report:**
```
Week of Oct 15:
- Overall Pass Rate: 78% (up from 72% last week)
- Improvements: completeness (+15%), clarity (+10%)
- Declines: tone (-5%, needs investigation)
- Trend: Upward across 4/5 metrics ✅
```

---

### **Example 2: Model Cost Optimization**

**Scenario:** Need to reduce costs, considering GPT-4o-mini instead of GPT-4o

**Use:**
1. Run same samples with both models
2. Check Model Comparison chart
3. Calculate acceptable quality loss
4. Make decision

**Analysis:**
```
GPT-4o:
  Cost: $0.10/evaluation
  Avg Pass Rate: 82%

GPT-4o-mini:
  Cost: $0.02/evaluation (80% cheaper!)
  Avg Pass Rate: 76% (6% lower)

Decision: Switch to mini for weekly checks,
         Use GPT-4o for final validation
         Savings: 70% cost reduction ✅
```

---

### **Example 3: Identifying Regressions**

**Scenario:** Latest run performed worse than expected

**Use:**
1. Check Latest vs Best chart → All metrics below best
2. Check Evolution Chart → Downward spike
3. Investigate what changed
4. Rollback or fix
5. Re-run to confirm fix

**Root Cause:**
- Heatmap shows sudden red in latest run (top row)
- Evolution chart shows spike downward
- Investigation reveals: New GT file had errors
- Fix: Correct GT file
- Re-run: Performance restored ✅

---

## ✅ **Best Practices**

### **1. Run Regularly**
- Weekly at minimum
- After any system changes
- Before major releases
- Establish baseline first (3-5 runs)

### **2. Track Consistently**
- Use same samples across runs (for comparison)
- Keep ground truth stable (or version it)
- Document changes between runs
- Tag runs in MLflow (if making experiments)

### **3. Look for Trends, Not Single Runs**
- One bad run ≠ system broken
- Need 2-3 runs to confirm trend
- Outliers happen (investigate but don't overreact)

### **4. Use Multiple Visualizations**
- Heatmap: Quick overview
- Evolution: Trend validation
- Latest vs Best: Regression check
- Improvement: Long-term progress

### **5. Save and Share**
- Right-click charts → Save as PNG
- Include in presentations
- Share with stakeholders
- Track in documentation

---

## 🎨 **Customization**

### **Adjust Time Range:**
```python
# In Cell 9, change max_results
max_results=100  # Last 100 runs (default)
max_results=20   # Last 20 runs (faster)
max_results=500  # Last 500 runs (comprehensive)
```

### **Filter by Model:**
```python
# Add filter to search_runs
filter_string="attributes.status = 'FINISHED' and params.model = 'gpt-4o'"
```

### **Change Color Scheme:**
```python
# In heatmap colorscale
colorscale=[
    [0.0, '#your_red'],
    [0.5, '#your_yellow'],
    [1.0, '#your_green']
]
```

---

## 🎉 **Summary**

**MLflow Dashboard Features:**
- ✅ 7 comprehensive visualizations
- ✅ Tracks any number of custom metrics
- ✅ Automatic scaling
- ✅ Historical analysis
- ✅ Model comparisons
- ✅ Improvement tracking
- ✅ Zero configuration

**When to Use:**
- After every evaluation run
- Weekly progress reviews
- A/B testing changes
- Model selection
- Stakeholder reporting
- Regression detection

**Value:**
- See trends you'd miss in single runs
- Make data-driven optimization decisions
- Catch regressions early
- Celebrate improvements
- Track ROI of changes

**Just run Cell 9 after Cell 7 - everything else is automatic!** 📊🔥✨
