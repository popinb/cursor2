# ⚡ Quick Test Guide - Streamlined Validation

## 🎯 **Purpose**

Fast test to validate the system works correctly without running 240 evaluations.

**Test Size:**
- ✅ **4 samples** (instead of 20)
- ✅ **5 metrics** (instead of 12)
- ✅ **20 total evaluations** (instead of 240)
- ✅ **~2 minutes** (instead of 5+ minutes)

---

## 📦 **Files to Use**

### **Quick Test Files (NEW):**
1. `QUICK_TEST_metrics_config.csv` - 5 diverse metrics
2. `QUICK_TEST_evaluation_data.csv` - 4 test samples
3. `QUICK_TEST_ground_truth_main.csv` - Ground truth for accuracy & helpfulness
4. `QUICK_TEST_ground_truth_quality.csv` - Ground truth for completeness, tone & clarity

### **System File:**
5. `LLM_Judge_Evaluation_System_FIXED.py` - Main notebook

---

## 📊 **Test Metrics (5 Total)**

| # | Metric Name | Type | What It Tests | Threshold |
|---|-------------|------|---------------|-----------|
| 1 | **accuracy_check** | Binary | Factual correctness | 1.0 |
| 2 | **helpfulness_rating** | Scale 1-5 | How helpful | 3.0 |
| 3 | **completeness_percentage** | Percentage | Information coverage | 70 |
| 4 | **tone_professionalism** | Binary | Professional tone | 1.0 |
| 5 | **clarity_score** | Scale 1-5 | How clear | 3.0 |

**Coverage:** ✅ Binary (2), ✅ Scale 1-5 (2), ✅ Percentage (1)

---

## 📝 **Test Samples (4 Total)**

### **Sample 1: Paris (Capital of France)** ✅
**Expected:** PASS all metrics
- Accurate, helpful, complete, professional, clear
- **This validates system works for good responses**

### **Sample 2: Photosynthesis** ✅ 
**Expected:** PASS most, mixed scores
- Accurate but simplified
- Helpful but could be more complete
- **This validates nuanced scoring**

### **Sample 3: Flat Tire** ❌
**Expected:** FAIL completeness, helpfulness
- Dangerously incomplete (missing safety steps)
- Too brief, unprofessional casual tone
- **This validates detection of inadequate responses**

### **Sample 4: Climate Change** ❌❌
**Expected:** FAIL multiple metrics
- Dismissive tone (FAIL tone_professionalism)
- Misleading content (FAIL accuracy_check)  
- Poor clarity (FAIL clarity_score)
- **This validates detection of problematic responses**

---

## 🎯 **Expected Results**

### **Overall:**
```
Total Evaluations: 20 (4 samples × 5 metrics)
Expected Pass: ~13-15 (65-75%)
Expected Fail: ~5-7 (25-35%)
```

### **Per Sample:**

**Sample 1 (Paris):**
- ✅ accuracy_check: 1 (PASS)
- ✅ helpfulness_rating: 5 (PASS)
- ✅ completeness_percentage: 95 (PASS)
- ✅ tone_professionalism: 1 (PASS)
- ✅ clarity_score: 5 (PASS)
- **Expected: 5/5 PASS**

**Sample 2 (Photosynthesis):**
- ✅ accuracy_check: 1 (PASS)
- ✅ helpfulness_rating: 3-4 (PASS)
- ⚠️ completeness_percentage: 60 (may FAIL if <70)
- ✅ tone_professionalism: 1 (PASS)
- ✅ clarity_score: 4 (PASS)
- **Expected: 4-5/5 PASS**

**Sample 3 (Flat Tire):**
- ⚠️ accuracy_check: 0-1 (may PASS - not wrong, just incomplete)
- ❌ helpfulness_rating: 1 (FAIL)
- ❌ completeness_percentage: 20 (FAIL)
- ❌ tone_professionalism: 0 (FAIL - too casual for safety)
- ❌ clarity_score: 2 (FAIL)
- **Expected: 0-1/5 PASS**

**Sample 4 (Climate Change):**
- ❌ accuracy_check: 0 (FAIL - misleading)
- ❌ helpfulness_rating: 1 (FAIL)
- ❌ completeness_percentage: 30 (FAIL)
- ❌ tone_professionalism: 0 (FAIL - dismissive)
- ❌ clarity_score: 1 (FAIL)
- **Expected: 0/5 PASS**

---

## 🚀 **How to Run**

### **Step 1: Upload Files to Databricks**

Upload these 5 files:
1. `LLM_Judge_Evaluation_System_FIXED.py`
2. `QUICK_TEST_metrics_config.csv`
3. `QUICK_TEST_evaluation_data.csv`
4. `QUICK_TEST_ground_truth_main.csv`
5. `QUICK_TEST_ground_truth_quality.csv`

---

### **Step 2: Update Widget Paths (Cell 2)**

```python
dbutils.widgets.text(
    "evaluation_data_path", 
    "QUICK_TEST_evaluation_data.csv",  # ← Changed
    "📊 Evaluation Data (CSV)"
)

dbutils.widgets.text(
    "metrics_config_path",
    "QUICK_TEST_metrics_config.csv",  # ← Changed
    "📋 Metrics Configuration (CSV)"
)

dbutils.widgets.text(
    "ground_truth_files",
    "/Workspace/Users/YOUR.EMAIL@company.com/QUICK_TEST_ground_truth_main.csv;/Workspace/Users/YOUR.EMAIL@company.com/QUICK_TEST_ground_truth_quality.csv",  # ← Changed
    "📚 Ground Truth Files (semicolon separated)"
)
```

**IMPORTANT:** Replace `YOUR.EMAIL@company.com` with your actual Databricks email!

---

### **Step 3: Select Model (Cell 3)**

Choose your model from dropdown:
- **databricks-llm** (default)
- **gpt-4o**
- **gpt-4o-mini**
- **gpt-3.5-turbo**

---

### **Step 4: Run All Cells**

Click **"Run All"** and wait ~2 minutes.

---

### **Step 5: Verify Results**

Check for these key validations:

#### **File Loading (Cell 2):**
```
✅ 2 ground truth files loaded
✅ 5 metrics loaded with auto-generated prompts
✅ 4 evaluation samples loaded
```

#### **Metric Loading (Cell 7):**
```
✅ accuracy_check - Auto-generated prompt from grading rubric
   📚 Ground truth: QUICK_TEST_ground_truth_main.csv → column 'correct_answer'
✅ helpfulness_rating - Auto-generated prompt from grading rubric
   📚 Ground truth: QUICK_TEST_ground_truth_main.csv → column 'helpful_notes'
✅ completeness_percentage - Auto-generated prompt from grading rubric
   📚 Ground truth: QUICK_TEST_ground_truth_quality.csv → column 'completeness_notes'
✅ tone_professionalism - Auto-generated prompt from grading rubric
   📚 Ground truth: QUICK_TEST_ground_truth_quality.csv → column 'tone_assessment'
✅ clarity_score - Auto-generated prompt from grading rubric
   📚 Ground truth: QUICK_TEST_ground_truth_quality.csv → column 'clarity_assessment'
```

#### **Evaluation Progress (Cell 7):**
```
📝 Sample 1/4: 1
   📊 accuracy_check... ✅
   📊 helpfulness_rating... ✅
   📊 completeness_percentage... ✅
   📊 tone_professionalism... ✅
   📊 clarity_score... ✅

📝 Sample 2/4: 2
   📊 accuracy_check... ✅
   📊 helpfulness_rating... ✅
   📊 completeness_percentage... ⚠️ (may be ✅ or ❌)
   📊 tone_professionalism... ✅
   📊 clarity_score... ✅

📝 Sample 3/4: 3
   📊 accuracy_check... ⚠️
   📊 helpfulness_rating... ❌
   📊 completeness_percentage... ❌
   📊 tone_professionalism... ❌
   📊 clarity_score... ❌

📝 Sample 4/4: 4
   📊 accuracy_check... ❌
   📊 helpfulness_rating... ❌
   📊 completeness_percentage... ❌
   📊 tone_professionalism... ❌
   📊 clarity_score... ❌
```

#### **Final Results (Cell 7):**
```
📊 RESULTS SUMMARY
Total Evaluations: 20
Passed: 13-15
Failed: 5-7
Pass Rate: 65-75%

Per-Metric Results:
✅ accuracy_check: 50-75% (2-3/4 samples pass)
✅ helpfulness_rating: 50-75% (2-3/4 samples pass)
✅ completeness_percentage: 25-50% (1-2/4 samples pass)
✅ tone_professionalism: 50% (2/4 samples pass)
✅ clarity_score: 50-75% (2-3/4 samples pass)
```

---

## ✅ **Success Criteria**

Your test is **SUCCESSFUL** if:

### **File Loading:**
- [x] 2 GT files loaded (not 3)
- [x] 5 metrics loaded (not 12)
- [x] 4 samples loaded (not 20)
- [x] Auto-generated prompts working

### **Key Failures:**
- [x] Sample 3 fails completeness_percentage
- [x] Sample 3 fails helpfulness_rating
- [x] Sample 4 fails tone_professionalism
- [x] Sample 4 fails accuracy_check

### **System Features:**
- [x] Binary metrics work (return 0 or 1)
- [x] Scale 1-5 metrics work (return 1-5)
- [x] Percentage metrics work (return 0-100)
- [x] Filename matching works (no full paths needed)
- [x] Model selection works (Databricks OR OpenAI)
- [x] Results export successfully

---

## 🎨 **What Each Sample Tests**

### **Sample 1: Excellent Response (Paris)**
**Purpose:** Validates system recognizes high-quality responses
- Tests: Accuracy detection, helpful content identification, completeness measurement
- Expected: Perfect or near-perfect scores across all metrics

### **Sample 2: Good but Simplified (Photosynthesis)**
**Purpose:** Validates nuanced scoring (not just pass/fail)
- Tests: Ability to score middle-range quality
- Expected: Mix of high and moderate scores

### **Sample 3: Dangerously Incomplete (Flat Tire)**
**Purpose:** Validates detection of inadequate safety-critical content
- Tests: Completeness detection, helpfulness assessment, tone appropriateness
- Expected: Multiple failures due to missing critical information

### **Sample 4: Problematic Content (Climate Change)**
**Purpose:** Validates detection of misleading/dismissive content
- Tests: Accuracy of scientific content, tone professionalism, clarity
- Expected: Failures across multiple dimensions (tone, accuracy, clarity)

---

## 🔬 **Validation Points**

### **1. Auto-Prompt Generation** ✅
All 5 metrics should show: "Auto-generated prompt from grading rubric"

### **2. Filename Matching** ✅
- Metrics CSV has: `quick_test_ground_truth_main.csv`
- Widget has: `/Workspace/Users/email/quick_test_ground_truth_main.csv`
- Code matches filename automatically

### **3. Bulletproof JSON Parsing** ✅
LLM might return:
- `{"score": 1}` ← Standard
- `{"accuracy_check": 1}` ← Metric name
- `{"accuracy_check_score": 1}` ← Metric name + score
- All formats should work!

### **4. Percentage Normalization** ✅
LLM might return:
- `85` (0-100 range) → Kept as `85.0` → Compare with threshold `70.0` ✅
- `0.85` (0-1 range) → Converted to `85.0` → Compare with threshold `70.0` ✅

### **5. Model Selection** ✅
- Databricks LLM: Routes to `_call_databricks_llm()`
- OpenAI models: Routes to `_call_openai_llm()`
- No errors in either path

---

## 📊 **Detailed Expected Scores**

| Sample | Metric | Expected Score | Expected Status | Reasoning |
|--------|--------|----------------|-----------------|-----------|
| 1 | accuracy_check | 1.0 | ✅ PASS | Factually perfect |
| 1 | helpfulness_rating | 5.0 | ✅ PASS | Extremely helpful |
| 1 | completeness_percentage | 95-100 | ✅ PASS | Comprehensive |
| 1 | tone_professionalism | 1.0 | ✅ PASS | Professional |
| 1 | clarity_score | 5.0 | ✅ PASS | Exceptionally clear |
| 2 | accuracy_check | 1.0 | ✅ PASS | Accurate basics |
| 2 | helpfulness_rating | 3-4 | ✅ PASS | Moderately helpful |
| 2 | completeness_percentage | 55-65 | ⚠️ BORDERLINE | Missing details |
| 2 | tone_professionalism | 1.0 | ✅ PASS | Appropriate |
| 2 | clarity_score | 4.0 | ✅ PASS | Clear |
| 3 | accuracy_check | 0-1 | ⚠️ UNCERTAIN | Not wrong, just incomplete |
| 3 | helpfulness_rating | 1.0 | ❌ FAIL | Not helpful |
| 3 | completeness_percentage | 15-25 | ❌ FAIL | Severely incomplete |
| 3 | tone_professionalism | 0.0 | ❌ FAIL | Too casual |
| 3 | clarity_score | 2.0 | ❌ FAIL | Unclear/vague |
| 4 | accuracy_check | 0.0 | ❌ FAIL | Misleading |
| 4 | helpfulness_rating | 1.0 | ❌ FAIL | Harmful misinformation |
| 4 | completeness_percentage | 25-35 | ❌ FAIL | Incomplete & misleading |
| 4 | tone_professionalism | 0.0 | ❌ FAIL | Dismissive |
| 4 | clarity_score | 1.0 | ❌ FAIL | Confusing |

---

## ⚡ **Quick Troubleshooting**

### **Problem: Files not found**
```
❌ ground truth file not found
```
**Solution:** Update full paths in Cell 2 widget with YOUR email

### **Problem: No metrics loaded**
```
❌ No valid metrics!
```
**Solution:** Check `QUICK_TEST_metrics_config.csv` uploaded correctly

### **Problem: Wrong number of evaluations**
```
Total: 240 (expected 20)
```
**Solution:** Make sure you're using QUICK_TEST files, not TEST files

### **Problem: All percentage metrics fail**
```
completeness_percentage: 0% pass rate
```
**Solution:** This was the bug we fixed - make sure you're using the FIXED notebook

---

## 🎉 **You're Done When...**

- ✅ 20 evaluations completed
- ✅ Sample 1 passed all metrics
- ✅ Sample 3 failed multiple metrics
- ✅ Sample 4 failed multiple metrics
- ✅ Pass rate 65-75%
- ✅ Results exported to CSV
- ✅ Dashboard generated

**Total time: ~2 minutes instead of 5+ minutes!** ⚡

---

## 📁 **File Summary**

| File | Purpose | Rows | Size |
|------|---------|------|------|
| `QUICK_TEST_metrics_config.csv` | 5 metrics config | 6 | ~2KB |
| `QUICK_TEST_evaluation_data.csv` | 4 test samples | 5 | ~1KB |
| `QUICK_TEST_ground_truth_main.csv` | GT for 2 metrics | 5 | ~10KB |
| `QUICK_TEST_ground_truth_quality.csv` | GT for 3 metrics | 5 | ~10KB |

**Total:** 4 CSV files, ~23KB

---

**Quick test ready! Upload and run for fast validation!** 🚀
