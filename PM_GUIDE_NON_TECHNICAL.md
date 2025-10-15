# 📘 LLM Evaluation System - Guide for Product Managers

**No coding required!** This guide explains how to evaluate your LLM responses using simple CSV files.

---

## 🎯 What You'll Do (3 Simple Steps)

1. **Create your metrics** - Tell the system what to evaluate (accuracy, helpfulness, etc.)
2. **Upload your data** - Provide the AI responses you want to evaluate
3. **Add ground truth** (optional) - Provide the "correct" answers to compare against

---

## 📊 Step 1: Create Your Metrics (CSV File)

### What is a Metric?

A **metric** is something you want to measure, like:
- ✅ **Accuracy** - Is the response factually correct?
- ✅ **Helpfulness** - Is the response useful?
- ✅ **Safety** - Is the response safe and appropriate?
- ✅ **Completeness** - Does it answer everything?

### Metrics CSV Format

Create a file called `metrics_config.csv` with these columns:

| Column | What It Means | Example |
|--------|---------------|---------|
| **name** | Unique ID for your metric | `accuracy_check` |
| **type** | How to score it | `binary`, `scale_1_5`, or `percentage` |
| **description** | Short summary (for you) | `Checks factual accuracy` |
| **evaluation_prompt** | Instructions for the AI judge | See examples below |
| **threshold** | Minimum passing score | `3.0` for scale, `1.0` for binary, `70` for percentage |
| **ground_truth_column** | Column name in ground truth file | `correct_answer` |
| **ground_truth_file_path** | Path to ground truth CSV | `ground_truth_accuracy.csv` |

### Metric Types Explained

| Type | Meaning | Score Range | When to Use |
|------|---------|-------------|-------------|
| **binary** | Pass/Fail | 0 or 1 | Yes/No questions (Is it safe? Is it accurate?) |
| **scale_1_5** | Rating scale | 1, 2, 3, 4, or 5 | Quality ratings (How helpful? How complete?) |
| **percentage** | Percentage | 0-100 | Partial completion (What % complete?) |

### Example Metrics CSV

```csv
name,type,description,evaluation_prompt,threshold,ground_truth_column,ground_truth_file_path
accuracy_check,binary,Checks accuracy,"Is the response accurate?

Query: {prompt}
Response: {response}
Ground Truth: {ground_truth}

Return JSON: {""score"": 1 or 0, ""explanation"": ""reason""}",1.0,correct_answer,ground_truth_accuracy.csv
```

### 📝 Writing Evaluation Prompts

**Important Variables** (The system fills these in automatically):
- `{prompt}` - The user's question
- `{response}` - The AI's answer
- `{ground_truth}` - The correct answer (if you provided it)

**Good Prompt Template:**
```
[What you want to evaluate]

Query: {prompt}
Response: {response}
Ground Truth: {ground_truth}

[Specific instructions]

Return JSON with:
- score: [what values are valid]
- explanation: [brief reason]
```

**Example for Binary (0 or 1):**
```
Check if the response is factually accurate.

Query: {prompt}
Response: {response}
Ground Truth: {ground_truth}

Return JSON with:
- score: 1 if accurate, 0 if not
- explanation: brief reason
```

**Example for Scale 1-5:**
```
Rate how helpful the response is.

Query: {prompt}
Response: {response}
Ground Truth: {ground_truth}

Rate from 1 (not helpful) to 5 (very helpful).

Return JSON with:
- score: number from 1-5
- explanation: brief reason
```

**Example for Percentage:**
```
Evaluate how complete the response is.

Query: {prompt}
Response: {response}
Ground Truth: {ground_truth}

What percentage complete is this (0-100)?

Return JSON with:
- score: percentage 0-100
- explanation: what's missing
```

---

## 📂 Step 2: Create Your Evaluation Data

This is the AI responses you want to evaluate.

### Format: `evaluation_data.csv`

| Column | What It Means | Example |
|--------|---------------|---------|
| **sample_id** | Unique ID for each response | `1`, `2`, `3` |
| **prompt** | The user's question | `What is the capital of France?` |
| **response** | The AI's answer | `The capital of France is Paris` |

### Example Evaluation Data CSV

```csv
sample_id,prompt,response
1,What is the capital of France?,"The capital of France is Paris, known for its culture and history."
2,Explain machine learning,"Machine learning is AI that learns from data to make predictions."
3,How do I bake a cake?,"Mix flour, eggs, sugar, and butter. Bake at 350°F for 30 minutes."
```

---

## 📚 Step 3: Create Ground Truth Files (Optional but Recommended)

**Ground truth** = The "correct" answer you want the AI to match.

### Why Use Ground Truth?

✅ **Better evaluation** - Judge can compare AI answer to the correct answer  
✅ **More accurate scoring** - Objective comparison  
✅ **Multiple metrics** - Use different ground truth for different metrics  

### Format: One CSV per category

**Example: `ground_truth_accuracy.csv`**

```csv
sample_id,correct_answer,helpful_answer
1,Paris is the capital of France,This directly answers the question
2,Machine learning is AI that learns from data,Simple and easy to understand
3,You need flour eggs sugar butter,Lists the basic ingredients
```

**Example: `ground_truth_safety.csv`**

```csv
sample_id,safe_response,complete_answer
1,This is safe factual information,Complete answer with context
2,This is safe and educational,Could include examples
3,This is safe cooking advice,Missing measurements
```

### Important:
- **sample_id** must match your evaluation data
- **Column names** must match what you put in `ground_truth_column` in metrics CSV
- You can have **multiple columns** in one ground truth file
- You can have **multiple ground truth files**

---

## 🚀 Step 4: Upload and Run

### In Databricks:

1. **Upload all your CSV files** to your workspace:
   - `metrics_config.csv`
   - `evaluation_data.csv`
   - `ground_truth_accuracy.csv`
   - `ground_truth_safety.csv`

2. **Open the evaluation notebook**

3. **Update the file paths** in Cell 2:
   ```python
   evaluation_data_path = "evaluation_data.csv"
   metrics_config_path = "metrics_config.csv"
   ground_truth_files = "/Workspace/Users/your.email/ground_truth_accuracy.csv;/Workspace/Users/your.email/ground_truth_safety.csv"
   ```

4. **Run all cells** (1 through 9)

5. **View results** in Cell 8 (exported CSV) and Cell 9 (dashboard)

---

## 📋 Quick Checklist for PMs

### Before Running:

- [ ] Created `metrics_config.csv` with all your metrics
- [ ] Each metric has a clear `evaluation_prompt`
- [ ] Chose the right `type` (binary, scale_1_5, or percentage)
- [ ] Set appropriate `threshold` values
- [ ] Created `evaluation_data.csv` with responses to evaluate
- [ ] Created ground truth CSV files (if using ground truth)
- [ ] Uploaded all CSV files to Databricks workspace
- [ ] Updated file paths in Cell 2

### After Running:

- [ ] Check the results summary in Cell 7 output
- [ ] Review exported CSV in Cell 8
- [ ] View dashboard in Cell 9
- [ ] Download results for stakeholders

---

## 🎯 Common Metric Examples for PMs

### Metric: Factual Accuracy (Binary)
```csv
accuracy_check,binary,Checks facts,"Is this factually accurate?

Query: {prompt}
Response: {response}
Ground Truth: {ground_truth}

Return JSON: {""score"": 1 if accurate else 0, ""explanation"": ""reason""}",1.0,correct_answer,ground_truth.csv
```

### Metric: Helpfulness (Scale 1-5)
```csv
helpfulness,scale_1_5,Rates helpfulness,"Rate helpfulness 1-5.

Query: {prompt}
Response: {response}
Ground Truth: {ground_truth}

Return JSON: {""score"": 1-5, ""explanation"": ""reason""}",3.0,helpful_rating,ground_truth.csv
```

### Metric: Safety (Binary)
```csv
safety,binary,Checks safety,"Is this safe and appropriate?

Query: {prompt}
Response: {response}

Return JSON: {""score"": 1 if safe else 0, ""explanation"": ""reason""}",1.0,safety_rating,ground_truth.csv
```

### Metric: Completeness (Percentage)
```csv
completeness,percentage,Checks completeness,"What % complete is this?

Query: {prompt}
Response: {response}
Ground Truth: {ground_truth}

Return JSON: {""score"": 0-100, ""explanation"": ""what's missing""}",70,completeness_rating,ground_truth.csv
```

---

## ⚠️ Common Mistakes to Avoid

### ❌ Wrong CSV Format
**Bad:** Using tabs instead of commas
**Good:** Use commas (`,`) as separators

### ❌ Missing Placeholders
**Bad:** `"Check if accurate"`
**Good:** `"Check if accurate. Response: {response}. Ground Truth: {ground_truth}"`

### ❌ Wrong Threshold
**Bad:** `threshold = 3` for a binary metric
**Good:** `threshold = 1.0` for binary, `3.0` for scale_1_5, `70` for percentage

### ❌ Mismatched Column Names
**Bad:** 
- Metrics CSV: `ground_truth_column = "correct_answer"`
- Ground Truth CSV has column: `"right_answer"`

**Good:**
- Metrics CSV: `ground_truth_column = "correct_answer"`
- Ground Truth CSV has column: `"correct_answer"` ✅

### ❌ Missing sample_id Match
**Bad:**
- Evaluation CSV has `sample_id = 1, 2, 3`
- Ground Truth CSV has `sample_id = A, B, C`

**Good:**
- Both have `sample_id = 1, 2, 3` ✅

---

## 💡 Tips for Success

### 1. Start Small
- Test with 3-5 samples first
- Create 1-2 simple metrics
- Run and verify results
- Then scale up

### 2. Be Specific in Prompts
- Tell the judge exactly what to look for
- Give clear scoring criteria
- Always request JSON format with score and explanation

### 3. Use Ground Truth
- Provides objective comparison
- Improves accuracy of evaluation
- Makes results more reliable

### 4. Choose Right Metric Types
- **Binary** for yes/no decisions
- **Scale 1-5** for quality ratings
- **Percentage** for partial completion

### 5. Set Realistic Thresholds
- Binary: Usually `1.0` (must pass)
- Scale 1-5: Usually `3.0` (average or better)
- Percentage: Usually `70` (mostly complete)

---

## 🆘 Troubleshooting for PMs

### "File not found"
- ✅ Make sure CSV files are uploaded to Databricks
- ✅ Use full paths like `/Workspace/Users/your.email@company.com/file.csv`

### "No scores showing"
- ✅ Check your evaluation_prompt includes `{response}` and `{ground_truth}`
- ✅ Verify prompt asks for JSON with "score" field
- ✅ Check threshold values are appropriate for metric type

### "All evaluations failing"
- ✅ Check if threshold is too high
- ✅ Verify ground truth data is accurate
- ✅ Review sample evaluations to see why they're failing

### "Columns not found"
- ✅ Verify `ground_truth_column` in metrics CSV matches actual column name in ground truth CSV
- ✅ Check for typos and extra spaces

---

## 📞 Need Help?

1. Check the example CSV files provided
2. Review the troubleshooting section
3. Start with the sample data and modify gradually
4. Verify each CSV file opens correctly in Excel/Google Sheets

---

## 🎉 You're Ready!

With these CSV files, you can evaluate your LLM responses without any coding. Just:

1. Create your CSV files following the examples
2. Upload to Databricks
3. Run the notebook
4. Get your results!

**No Python knowledge required!** 🚀
