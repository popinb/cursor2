# ⚡ Quick Start Guide for Product Managers

**Get results in 10 minutes with zero coding!**

---

## ✅ Your Checklist

### Step 1: Download Sample Files (1 min)
Download these files to see examples:
- [ ] `sample_metrics_config_FOR_PMs.csv` - Example metrics
- [ ] `sample_evaluation_data.csv` - Example data to evaluate
- [ ] `sample_ground_truth_accuracy.csv` - Example ground truth
- [ ] `sample_ground_truth_safety.csv` - Example ground truth

### Step 2: Edit for Your Needs (5 min)
- [ ] Open `sample_metrics_config_FOR_PMs.csv` in Excel/Google Sheets
- [ ] Modify the metrics for what you want to test
- [ ] Save as `metrics_config.csv`

- [ ] Open `sample_evaluation_data.csv`
- [ ] Replace with your actual AI responses
- [ ] Save as `evaluation_data.csv`

- [ ] Open ground truth files
- [ ] Add your "correct answers"
- [ ] Save as `ground_truth_accuracy.csv` and `ground_truth_safety.csv`

### Step 3: Upload to Databricks (2 min)
- [ ] Log into Databricks
- [ ] Go to **Workspace** → **Your User Folder**
- [ ] Click **⋮** menu → **Import**
- [ ] Upload all 3 CSV files:
  - `metrics_config.csv`
  - `evaluation_data.csv`
  - `ground_truth_accuracy.csv`
  - `ground_truth_safety.csv`

### Step 4: Upload Notebook (1 min)
- [ ] Click **⋮** menu → **Import**
- [ ] Upload `LLM_Judge_Evaluation_System_FIXED.py`
- [ ] Open the notebook

### Step 5: Update File Paths (1 min)
In **Cell 2**, update the file paths:

```python
# Change "your.email@company.com" to YOUR email
dbutils.widgets.text(
    "ground_truth_files",
    "/Workspace/Users/YOUR.EMAIL@company.com/ground_truth_accuracy.csv;/Workspace/Users/YOUR.EMAIL@company.com/ground_truth_safety.csv",
    "📚 Ground Truth Files"
)
```

### Step 6: Run the Notebook (5 min)
- [ ] Click **Run All** at the top
- [ ] Wait for all cells to complete (about 5 minutes)
- [ ] Results will appear automatically!

### Step 7: View Results (1 min)
- [ ] **Cell 7**: See summary in console output
- [ ] **Cell 8**: Download detailed CSV results
- [ ] **Cell 9**: View interactive dashboard

---

## 🎯 What Each File Does

| File | Purpose | You Need To... |
|------|---------|----------------|
| **metrics_config.csv** | Defines what to evaluate | Define your metrics (accuracy, safety, etc.) |
| **evaluation_data.csv** | AI responses to test | Provide the responses you want to evaluate |
| **ground_truth_*.csv** | Correct answers | Provide the "right" answers to compare against |

---

## 📊 Example: Evaluating Customer Service Responses

### Your Metrics (`metrics_config.csv`):
```csv
name,type,description,evaluation_prompt,threshold,ground_truth_column,ground_truth_file_path
politeness,scale_1_5,Checks politeness,"Rate politeness 1-5. Response: {response}. Return JSON.",3.0,polite_rating,ground_truth.csv
accuracy,binary,Checks accuracy,"Is this accurate? Response: {response}. Ground Truth: {ground_truth}. Return JSON with score 0 or 1.",1.0,correct_answer,ground_truth.csv
```

### Your Evaluation Data (`evaluation_data.csv`):
```csv
sample_id,prompt,response
1,What are your hours?,We're open 9-5 Monday-Friday. How can I help you today?
2,Do you offer refunds?,Yes! We offer 30-day refunds on all products.
```

### Your Ground Truth (`ground_truth.csv`):
```csv
sample_id,polite_rating,correct_answer
1,Should be friendly and professional,Business hours are 9am-5pm weekdays
2,Should offer help,30-day refund policy on all items
```

### Results You'll Get:
```
📊 RESULTS SUMMARY
Total Evaluations: 4
Passed: 3
Failed: 1
Pass Rate: 75%

🔹 politeness:
   Pass Rate: 100% (2/2)
   Avg Score: 4.5

🔹 accuracy:
   Pass Rate: 50% (1/2)
   Avg Score: 0.5
```

---

## 🎨 Customization Examples

### Example 1: E-commerce Product Descriptions

**Metrics:**
- `clarity` - Is the description clear? (scale 1-5)
- `completeness` - Does it include all details? (percentage)
- `accuracy` - Are specs correct? (binary)

### Example 2: Educational Content

**Metrics:**
- `age_appropriate` - Right for target age? (binary)
- `engagement` - How engaging? (scale 1-5)
- `educational_value` - How much do they learn? (percentage)

### Example 3: Marketing Copy

**Metrics:**
- `brand_alignment` - Matches brand voice? (scale 1-5)
- `call_to_action` - Has clear CTA? (binary)
- `persuasiveness` - How persuasive? (scale 1-5)

---

## ⚠️ Common First-Time Mistakes

### ❌ Mistake 1: Wrong file paths
**Problem:** File not found error  
**Fix:** Use full path like `/Workspace/Users/your.email@company.com/file.csv`

### ❌ Mistake 2: Tabs instead of commas
**Problem:** CSV parsing errors  
**Fix:** Save as CSV (comma-separated), not TSV (tab-separated)

### ❌ Mistake 3: Missing {response} placeholder
**Problem:** No scores generated  
**Fix:** Make sure evaluation_prompt includes `{response}` and `{ground_truth}`

### ❌ Mistake 4: Wrong threshold
**Problem:** Everything fails  
**Fix:** 
- Binary: use `1.0`
- Scale 1-5: use `3.0`
- Percentage: use `70`

### ❌ Mistake 5: Mismatched column names
**Problem:** Ground truth not found  
**Fix:** Column name in metrics CSV must exactly match column in ground truth CSV

---

## 💡 Pro Tips

### Tip 1: Test with 3 samples first
Don't evaluate 1000 responses on your first run. Test with 3-5 samples to verify everything works.

### Tip 2: Use descriptive metric names
Good: `customer_service_politeness`  
Bad: `metric1`

### Tip 3: Be specific in prompts
Good: "Rate politeness from 1-5 based on tone, word choice, and friendliness"  
Bad: "Is this good?"

### Tip 4: Always request JSON
Your evaluation_prompt should end with:
```
Return JSON with:
- score: [value]
- explanation: [reason]
```

### Tip 5: Check the dashboard
Cell 9 creates a beautiful interactive dashboard showing trends over time. Use this to track improvements!

---

## 📞 Need Help?

### If you see an error:
1. Read the error message carefully
2. Check the "Common Mistakes" section above
3. Verify your CSV files open correctly in Excel
4. Make sure file paths are correct
5. Review the PM Guide (PM_GUIDE_NON_TECHNICAL.md)

### If results look wrong:
1. Check your threshold values
2. Verify ground truth data is correct
3. Review the evaluation_prompt for each metric
4. Look at individual explanations in the output

---

## 🎉 Success!

Once you see results in Cell 7, you're done! You can:

✅ Download the CSV from Cell 8  
✅ View the dashboard in Cell 9  
✅ Share results with stakeholders  
✅ Modify metrics and run again  
✅ Scale up to thousands of evaluations  

**Congratulations - you're now evaluating LLMs like a pro!** 🚀

---

## 📚 Additional Resources

- **PM_GUIDE_NON_TECHNICAL.md** - Comprehensive guide with examples
- **sample_*.csv files** - Copy these and modify for your needs
- **BULLETPROOF_SOLUTION_EXPLAINED.md** - Technical details (optional reading)

---

**Estimated Total Time:** 15 minutes from download to results! ⏱️
