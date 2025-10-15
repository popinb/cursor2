# 🧪 How to Run the Comprehensive Test Suite

## 📦 **Test Files Included**

### **Test Data Files:**
1. ✅ `TEST_metrics_config.csv` - 12 metrics configuration
2. ✅ `TEST_evaluation_data.csv` - 20 test samples
3. ✅ `TEST_ground_truth_accuracy.csv` - GT for accuracy metrics
4. ✅ `TEST_ground_truth_safety.csv` - GT for safety metrics
5. ✅ `TEST_ground_truth_quality.csv` - GT for quality metrics

### **Documentation Files:**
6. ✅ `TEST_CASES_DOCUMENTATION.md` - Complete test documentation
7. ✅ `TEST_EXPECTED_RESULTS.csv` - Expected outcomes
8. ✅ `RUN_TESTS_GUIDE.md` - This file

### **System Files:**
9. ✅ `LLM_Judge_Evaluation_System_FIXED.py` - Main notebook
10. ✅ `FINAL_metrics_config_PM_FRIENDLY.csv` - Production template

---

## 🚀 **Quick Start (5 Steps)**

### **Step 1: Upload Test Files to Databricks (2 min)**

1. Log into Databricks
2. Navigate to your workspace folder
3. Upload these 5 files:
   - `TEST_metrics_config.csv`
   - `TEST_evaluation_data.csv`
   - `TEST_ground_truth_accuracy.csv`
   - `TEST_ground_truth_safety.csv`
   - `TEST_ground_truth_quality.csv`

**Tip:** Note your full workspace path (e.g., `/Workspace/Users/your.email@company.com/`)

---

### **Step 2: Upload the Notebook (1 min)**

1. In Databricks, click **Import**
2. Select `LLM_Judge_Evaluation_System_FIXED.py`
3. Import the notebook
4. Open it

---

### **Step 3: Update Widget Paths (1 min)**

In **Cell 2** of the notebook, update the widgets:

```python
# Update evaluation data path
dbutils.widgets.text(
    "evaluation_data_path", 
    "TEST_evaluation_data.csv",  # ← Changed to TEST file
    "📊 Evaluation Data (CSV)"
)

# Update metrics config path
dbutils.widgets.text(
    "metrics_config_path",
    "TEST_metrics_config.csv",  # ← Changed to TEST file
    "📋 Metrics Configuration (CSV)"
)

# Update ground truth files (REPLACE YOUR.EMAIL with your actual email!)
dbutils.widgets.text(
    "ground_truth_files",
    "/Workspace/Users/YOUR.EMAIL@company.com/TEST_ground_truth_accuracy.csv;/Workspace/Users/YOUR.EMAIL@company.com/TEST_ground_truth_safety.csv;/Workspace/Users/YOUR.EMAIL@company.com/TEST_ground_truth_quality.csv",
    "📚 Ground Truth Files (semicolon separated)"
)
```

**IMPORTANT:** Replace `YOUR.EMAIL@company.com` with your actual Databricks email!

---

### **Step 4: Run the Test (5 min)**

1. Click **Run All** at the top of the notebook
2. Wait for all cells to execute (~5 minutes)
3. Monitor the output

---

### **Step 5: Verify Results (2 min)**

Check the output for:

#### **✅ File Loading (Cell 2)**
```
📚 Loading 3 ground truth files...
✅ TEST_ground_truth_accuracy.csv → 20 rows, columns: sample_id, correct_answer, helpful_answer, relevance_check, facts_verified
✅ TEST_ground_truth_safety.csv → 20 rows, columns: sample_id, safe_response, complete_answer
✅ TEST_ground_truth_quality.csv → 20 rows, columns: sample_id, clarity_notes, tone_rating, detail_notes, engagement_rating, conciseness_notes, error_check

✅ Loaded 3 ground truth files
```

#### **✅ Metric Loading (Cell 7)**
```
Loading metrics...
✅ accuracy_check - Auto-generated prompt from grading rubric
   📚 Ground truth: TEST_ground_truth_accuracy.csv → column 'correct_answer'
✅ helpfulness_rating - Auto-generated prompt from grading rubric
   📚 Ground truth: TEST_ground_truth_accuracy.csv → column 'helpful_answer'
... (10 more metrics)
```

#### **✅ Evaluation Results (Cell 7)**
```
🚀 STARTING EVALUATION

📝 Sample 5/20
   accuracy_check... ❌  ← Should FAIL (wrong planet count)
   helpfulness_rating... ✅
   safety_check... ✅
   ...

📝 Sample 7/20
   tone_check... ❌  ← Should FAIL (unprofessional tone)
   helpfulness_rating... ❌
   ...

📊 RESULTS
Total: 240
Passed: ~180-200
Failed: ~40-60
Pass Rate: ~75-85%

accuracy_check:
  Pass Rate: 95% (19/20)  ← Sample 5 should fail
  Avg Score: 0.95

tone_check:
  Pass Rate: 95% (19/20)  ← Sample 7 should fail
  Avg Score: 0.95
```

---

## ✅ **Success Criteria**

Your test is **SUCCESSFUL** if:

### **1. File Loading:**
- [x] All 3 ground truth files load
- [x] All show 20 rows
- [x] All columns are identified

### **2. Metric Loading:**
- [x] All 12 metrics load
- [x] All show "Auto-generated prompt from grading rubric"
- [x] All show correct GT file → column mapping

### **3. Evaluation Execution:**
- [x] 240 total evaluations (20 samples × 12 metrics)
- [x] No errors during execution
- [x] Completes in ~5 minutes

### **4. Key Test Cases:**
- [x] **Sample 5** fails `accuracy_check` (says 9 planets)
- [x] **Sample 5** fails `factual_correctness` (Pluto is not a planet)
- [x] **Sample 7** fails `tone_check` (dismissive tone)
- [x] **Sample 7** has low scores on helpfulness, engagement

### **5. Overall Results:**
- [x] Pass rate is ~75-85%
- [x] Results export to CSV successfully
- [x] Dashboard generates
- [x] MLflow logging works

---

## 🔍 **What Each Cell Should Show**

### **Cell 1: Installation**
```
✅ All packages installed!
```

### **Cell 2: File Loading**
```
📊 Loading evaluation data...
✅ Loaded evaluation data: 20 rows, 3 columns

📋 Loading metrics config...
✅ Loaded metrics config: 12 rows

📚 Loading 3 ground truth files...
✅ TEST_ground_truth_accuracy.csv → 20 rows
✅ TEST_ground_truth_safety.csv → 20 rows
✅ TEST_ground_truth_quality.csv → 20 rows
```

### **Cell 3: Model Configuration**
```
🤖 Model: [your selected model]
✅ [OpenAI/Databricks] client ready
```

### **Cell 4-6: Core Classes**
```
✅ Classes defined
✅ Evaluator ready
```

### **Cell 7: Evaluation**
```
Loading metrics...
✅ accuracy_check - Auto-generated prompt from grading rubric
... (all 12 metrics)

🚀 STARTING EVALUATION
Evaluating 20 samples...

📝 Sample 1/20
   accuracy_check... ✅
   helpfulness_rating... ✅
   ... (all 12 metrics)

... (samples 2-4)

📝 Sample 5/20
   accuracy_check... ❌  ← KEY: Should fail
   ... (other metrics)

... (sample 6)

📝 Sample 7/20
   tone_check... ❌  ← KEY: Should fail
   ... (other metrics)

... (samples 8-20)

✅ COMPLETE

📊 RESULTS
Total: 240
Passed: [~180-200]
Failed: [~40-60]
Pass Rate: [~75-85%]

Per-metric results...
```

### **Cell 8: Export**
```
✅ Results saved to: /Workspace/Users/[email]/evaluation_results_[timestamp].csv
✅ 240 evaluations exported
```

### **Cell 9: Dashboard**
```
✅ Found [X] runs
[Interactive chart displayed]
```

---

## 🎯 **Critical Test Scenarios**

### **Scenario 1: Factual Error Detection**

**Test Sample:** Sample 5 (Solar System)
```
Response: "The solar system has 9 planets... including Pluto."
Ground Truth: "8 planets, Pluto is a dwarf planet"
```

**Expected Behavior:**
- ❌ `accuracy_check` = 0 (FAIL)
- ❌ `factual_correctness` = 0 (FAIL)
- ✅ Explanation mentions incorrect planet count

**How to Verify:**
Look for Sample 5 in results:
```
📝 Sample 5/20
   accuracy_check... ❌
   factual_correctness... ❌
```

---

### **Scenario 2: Tone Violation Detection**

**Test Sample:** Sample 7 (Quantum Physics)
```
Response: "Quantum physics is super complicated... even scientists don't fully get it."
Ground Truth: Professional explanation expected
```

**Expected Behavior:**
- ❌ `tone_check` = 0 (FAIL - unprofessional)
- ❌ `helpfulness_rating` = 1-2 (FAIL - not helpful)
- ❌ `engagement_score` = 1-2 (FAIL - discouraging)
- ✅ Explanation mentions dismissive/unprofessional tone

**How to Verify:**
```
📝 Sample 7/20
   tone_check... ❌
   helpfulness_rating... ❌
   engagement_score... ❌
```

---

### **Scenario 3: Appropriate Brevity**

**Test Sample:** Sample 12 (Translation)
```
Response: "Hola"
Task: Translate hello to Spanish
```

**Expected Behavior:**
- ✅ `accuracy_check` = 1 (PASS - correct)
- ✅ `completeness_score` = 90-100 (PASS - complete for task)
- ✅ `conciseness_rating` = 4-5 (PASS - appropriately concise)
- ✅ Should NOT be penalized for brevity

**How to Verify:**
```
📝 Sample 12/20
   accuracy_check... ✅
   completeness_score... ✅
   conciseness_rating... ✅
```

---

### **Scenario 4: Filename Matching**

**Test Setup:**
```
Metrics CSV specifies: "TEST_ground_truth_accuracy.csv"
Widget provides: "/Workspace/Users/email/TEST_ground_truth_accuracy.csv"
```

**Expected Behavior:**
- ✅ Code extracts filename: `TEST_ground_truth_accuracy.csv`
- ✅ Matches to full path from widget
- ✅ Loads correct file
- ✅ All metrics using this file get correct GT data

**How to Verify:**
```
📚 Loading 3 ground truth files...
✅ TEST_ground_truth_accuracy.csv → 20 rows

Loading metrics...
✅ accuracy_check - Auto-generated prompt from grading rubric
   📚 Ground truth: TEST_ground_truth_accuracy.csv → column 'correct_answer'
```

---

### **Scenario 5: Auto-Prompt Generation**

**Test Setup:**
```
Metrics CSV has:
  grading_rubric: "Score 1 if accurate. Score 0 if errors."
  NO evaluation_prompt column
```

**Expected Behavior:**
- ✅ Code generates full evaluation prompt
- ✅ Includes grading rubric
- ✅ Adds {prompt}, {response}, {ground_truth}
- ✅ Adds JSON format instructions
- ✅ Works correctly during evaluation

**How to Verify:**
```
✅ accuracy_check - Auto-generated prompt from grading rubric
```
(Should NOT say "Using provided evaluation_prompt")

---

## 🐛 **Troubleshooting**

### **Problem: Files Not Found**

**Error:**
```
❌ evaluation data not found: TEST_evaluation_data.csv
```

**Solution:**
1. Verify files are uploaded to Databricks
2. Check file names match exactly (case-sensitive!)
3. Try specifying full path in widget:
   ```python
   dbutils.widgets.text("evaluation_data_path", 
       "/Workspace/Users/your.email/TEST_evaluation_data.csv", ...)
   ```

---

### **Problem: Ground Truth Not Loading**

**Error:**
```
⚠️ File not found: /Workspace/Users/.../TEST_ground_truth_accuracy.csv
```

**Solution:**
1. Verify GT files are uploaded
2. Update widget with YOUR email:
   ```python
   "/Workspace/Users/YOUR.ACTUAL.EMAIL@company.com/TEST_ground_truth_accuracy.csv"
   ```
3. Check for typos in filename

---

### **Problem: No Metrics Loaded**

**Error:**
```
❌ No valid metrics!
```

**Solution:**
1. Check `TEST_metrics_config.csv` uploaded correctly
2. Verify CSV has correct columns:
   - name, type, description, grading_rubric, threshold, ground_truth_column, ground_truth_file_path
3. Check for CSV formatting issues (commas vs tabs)

---

### **Problem: Evaluation Stuck/Slow**

**Behavior:**
- Evaluation takes > 10 minutes
- Appears frozen

**Solution:**
1. Check LLM endpoint is working
2. For Databricks LLM, verify endpoint is running
3. For OpenAI, check API key is valid
4. Reduce test samples temporarily to verify

---

### **Problem: Unexpected Pass/Fail Results**

**Issue:**
- Sample 5 passes accuracy_check (should fail)
- Sample 7 passes tone_check (should fail)

**Possible Causes:**
1. Different LLM model may be more lenient
2. Ground truth not being used correctly
3. Threshold set incorrectly

**Solution:**
1. Check console output shows GT file loaded
2. Verify GT column mapping is correct
3. Review actual LLM explanations in output
4. Consider this acceptable variation if close

---

## 📊 **Expected Performance**

### **Execution Time:**
- File loading: ~10 seconds
- Metric loading: ~5 seconds
- Evaluations: ~3-5 minutes (240 evaluations)
- Export/Dashboard: ~10 seconds
- **Total: ~5 minutes**

### **Resource Usage:**
- Memory: ~500MB-1GB
- LLM API calls: 240 calls (20 samples × 12 metrics)
- Results file: ~100KB CSV

---

## 📝 **Test Report Template**

After running, document your results:

```markdown
# Test Execution Report

**Date:** 2025-10-15
**Tester:** [Your Name]
**Model Used:** [GPT-4o / Databricks LLM / etc.]

## File Loading
- [ ] All 3 GT files loaded: YES
- [ ] All columns identified: YES
- [ ] No errors: YES

## Metric Loading
- [ ] All 12 metrics loaded: YES
- [ ] Auto-generated prompts: YES
- [ ] GT mapping correct: YES

## Evaluation Results
- Total Evaluations: 240
- Passed: ___
- Failed: ___
- Pass Rate: ___%

## Critical Test Cases
- [ ] Sample 5 failed accuracy: YES/NO
- [ ] Sample 7 failed tone: YES/NO
- [ ] Sample 12 passed (appropriate brevity): YES/NO

## Issues Found
1. (None / List issues)

## Overall Assessment
- [ ] Test PASSED
- [ ] Test FAILED (explain why)

## Notes
(Any additional observations)
```

---

## 🎉 **Next Steps After Testing**

### **If Tests Pass:**
1. ✅ System is validated and ready for production use
2. ✅ Create your own metrics using `FINAL_metrics_config_PM_FRIENDLY.csv` as template
3. ✅ Replace test data with your actual evaluation data
4. ✅ Run production evaluations!

### **If Tests Fail:**
1. Review error messages carefully
2. Check troubleshooting section above
3. Verify file paths and names
4. Review `TEST_CASES_DOCUMENTATION.md` for expected behavior
5. Check `TEST_EXPECTED_RESULTS.csv` for specific sample expectations

---

## 📚 **Additional Resources**

- **TEST_CASES_DOCUMENTATION.md** - Detailed test case descriptions
- **TEST_EXPECTED_RESULTS.csv** - Expected outcomes for each test
- **FINAL_SOLUTION_FOR_PMs.md** - Production usage guide
- **PM_GUIDE_GRADING_RUBRICS.md** - How to write grading rubrics

---

## ✅ **Final Checklist**

Before you start:
- [ ] Uploaded all 5 test files to Databricks
- [ ] Uploaded notebook to Databricks
- [ ] Updated widget paths with YOUR email
- [ ] Ready to click "Run All"

During test run:
- [ ] Monitor console output
- [ ] Check for errors
- [ ] Verify GT files load
- [ ] Watch for Sample 5 and 7

After test run:
- [ ] Verify pass rate ~75-85%
- [ ] Check Sample 5 failed accuracy
- [ ] Check Sample 7 failed tone
- [ ] Review exported results
- [ ] Check dashboard

---

**Ready to test? Upload files, update paths, and Run All!** 🚀
