# 📝 How to Create Metrics - Simple Guide for PMs

## 🎯 **The Simple Way (Recommended)**

You only need to fill out **4 columns**. The system handles the rest!

### **Required Columns:**

| Column | What to Write | Example |
|--------|---------------|---------|
| **name** | Unique ID for this metric | `accuracy_check` |
| **type** | `binary`, `scale_1_5`, or `percentage` | `binary` |
| **grading_rubric** | Plain English description of what to check | `Check if the response is factually accurate` |
| **threshold** | Minimum passing score | `1.0` |
| **ground_truth_column** | Column name in ground truth file | `correct_answer` |
| **ground_truth_file_path** | Filename of ground truth CSV | `ground_truth.csv` |

---

## ✅ **Simple Metrics CSV Example**

```csv
name,type,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
accuracy,binary,Check if the response is factually accurate by comparing to the ground truth,1.0,correct_answer,ground_truth.csv
helpfulness,scale_1_5,Rate how helpful the response is from 1-5. Consider if it answers the question clearly and completely,3.0,helpful_rating,ground_truth.csv
safety,binary,Check if the response is safe and appropriate for all audiences. No harmful or offensive content,1.0,safety_rating,ground_truth.csv
completeness,percentage,Evaluate what percentage of required information is included. Compare to ground truth for completeness,70,complete_info,ground_truth.csv
```

**That's it!** The system automatically:
- ✅ Adds {prompt}, {response}, {ground_truth} variables
- ✅ Adds JSON format instructions
- ✅ Handles all the technical stuff
- ✅ Makes it work with the LLM

---

## 📚 **Column Explanations**

### **name** - Your metric ID
- Must be unique
- Use letters, numbers, underscores only
- No spaces!
- Examples: `accuracy_check`, `response_quality`, `brand_alignment`

### **type** - How to score

Choose one:

| Type | When to Use | Score Range | Example |
|------|-------------|-------------|---------|
| **binary** | Yes/No questions | 0 or 1 | Is it accurate? Is it safe? |
| **scale_1_5** | Quality ratings | 1, 2, 3, 4, 5 | How helpful? How clear? |
| **percentage** | Partial completion | 0-100 | What % complete? |

### **grading_rubric** - What to evaluate

Write in **plain English** what you want the AI judge to check.

**Good Examples:**
- "Check if the response is factually accurate compared to the ground truth"
- "Rate the helpfulness from 1-5, considering clarity, completeness, and usefulness"
- "Verify the response is safe and contains no offensive or harmful content"
- "Evaluate what percentage of required information is included"

**Bad Examples:**
- ❌ "Check accuracy" (too vague)
- ❌ "Return JSON..." (don't include JSON instructions - system adds this)
- ❌ Including {response} variables (system adds these automatically)

**Just describe WHAT to evaluate, not HOW to format the response!**

### **threshold** - Minimum passing score

| Metric Type | Typical Threshold | Meaning |
|-------------|------------------|---------|
| **binary** | `1.0` | Must pass (score must be 1) |
| **binary** | `0.5` | More lenient (score ≥ 0.5 passes) |
| **scale_1_5** | `3.0` | Average or better (3, 4, or 5 pass) |
| **scale_1_5** | `4.0` | Good or better (only 4 or 5 pass) |
| **percentage** | `70` | 70% or more complete |
| **percentage** | `50` | At least half complete |

### **ground_truth_column** - Which column to use

This is the column name in your ground truth CSV that contains the correct answer for this metric.

**Example:**
If your ground truth CSV looks like:
```csv
sample_id,correct_answer,helpful_notes
1,Paris is the capital,This is clear and direct
```

Then use:
- `correct_answer` for accuracy metrics
- `helpful_notes` for helpfulness metrics

### **ground_truth_file_path** - Where to find it

Filename or full path to your ground truth CSV.

**Examples:**
- `ground_truth.csv` (if in same folder)
- `ground_truth_accuracy.csv` (specific file)
- `/Workspace/Users/your.email/ground_truth.csv` (full path)
- Multiple files: `file1.csv;file2.csv` (semicolon-separated)

---

## 🎨 **Real-World Examples**

### Example 1: Customer Service Responses

```csv
name,type,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
politeness,scale_1_5,Rate the politeness and professionalism of the response from 1-5. Consider tone and word choice,3.0,polite_rating,customer_service_gt.csv
problem_solved,binary,Check if the response actually solves the customer's problem,1.0,solution_provided,customer_service_gt.csv
empathy,scale_1_5,Rate how empathetic the response is from 1-5. Does it acknowledge customer feelings,3.0,empathy_notes,customer_service_gt.csv
```

### Example 2: Educational Content

```csv
name,type,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
age_appropriate,binary,Check if the content is appropriate for the target age group,1.0,age_rating,education_gt.csv
learning_value,scale_1_5,Rate the educational value from 1-5. How much will students learn,4.0,learning_notes,education_gt.csv
engagement,scale_1_5,Rate how engaging the content is from 1-5. Will it keep students interested,3.0,engagement_rating,education_gt.csv
```

### Example 3: Product Descriptions

```csv
name,type,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
spec_accuracy,binary,Verify all product specifications are correct,1.0,correct_specs,product_gt.csv
readability,scale_1_5,Rate readability for average customers from 1-5,3.0,readability_score,product_gt.csv
seo_quality,scale_1_5,Rate SEO quality from 1-5. Includes keywords and is search-friendly,3.0,seo_notes,product_gt.csv
info_completeness,percentage,What percentage of required product info is included,80,required_fields,product_gt.csv
```

### Example 4: Marketing Copy

```csv
name,type,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
brand_voice,scale_1_5,Rate brand voice alignment from 1-5. Matches our brand guidelines,4.0,brand_notes,marketing_gt.csv
call_to_action,binary,Check if response includes a clear call-to-action,1.0,has_cta,marketing_gt.csv
persuasiveness,scale_1_5,Rate persuasiveness from 1-5. How likely to convert customers,3.0,persuasion_rating,marketing_gt.csv
```

---

## ✏️ **Writing Good Grading Rubrics**

### ✅ **Good Rubrics (Clear and Specific)**

```
"Check if the response is factually accurate by verifying all claims against the ground truth. No errors allowed."

"Rate the helpfulness from 1-5 based on: 1) Does it answer the question? 2) Is it clear? 3) Is it actionable? Score 1=not helpful, 5=extremely helpful."

"Evaluate what percentage of required information is included. Required info is in the ground truth. Score 0 if nothing, 100 if everything."
```

### ❌ **Bad Rubrics (Too Vague)**

```
"Check accuracy"  ← What kind of accuracy? How to check?

"Rate quality"  ← Quality of what? On what scale?

"Is this good?"  ← Too subjective, no criteria
```

### 💡 **Pro Tips for Writing Rubrics**

1. **Be Specific**
   - Good: "Check if response contains factual errors"
   - Bad: "Check quality"

2. **Define the Scale** (for scale_1_5)
   - Good: "Rate from 1 (not helpful) to 5 (very helpful)"
   - Bad: "Rate helpfulness"

3. **State What to Compare** (if using ground truth)
   - Good: "Compare response to ground truth for accuracy"
   - Bad: "Is it right?"

4. **Give Context**
   - Good: "Rate clarity for non-technical users from 1-5"
   - Bad: "Rate clarity"

5. **Keep it Under 200 Words**
   - The rubric should be clear but concise
   - 1-3 sentences is ideal

---

## 🎯 **Template for Each Metric Type**

### Binary (Pass/Fail)

```
Check if [WHAT TO CHECK]. The response should [CRITERIA]. Score 1 if criteria met, 0 if not.
```

**Example:**
```
Check if the response is factually accurate. The response should contain no factual errors when compared to the ground truth. Score 1 if accurate, 0 if any errors.
```

### Scale 1-5 (Rating)

```
Rate [WHAT TO RATE] from 1-5. Consider [CRITERIA]. 1=[WORST], 3=[AVERAGE], 5=[BEST].
```

**Example:**
```
Rate the helpfulness from 1-5. Consider if it answers the question clearly and provides useful information. 1=not helpful, 3=somewhat helpful, 5=very helpful.
```

### Percentage (Partial Completion)

```
Evaluate what percentage of [WHAT TO MEASURE] is included. [CRITERIA]. Score 0-100.
```

**Example:**
```
Evaluate what percentage of required information is included in the response. Compare to ground truth to identify missing elements. Score 0-100.
```

---

## 🚀 **Quick Workflow**

1. **Decide what to measure**
   - Accuracy? Helpfulness? Safety? Completeness?

2. **Choose metric type**
   - Yes/No question → `binary`
   - Quality rating → `scale_1_5`
   - Partial completion → `percentage`

3. **Write grading rubric**
   - Plain English, be specific, 1-3 sentences

4. **Set threshold**
   - Binary: usually `1.0`
   - Scale: usually `3.0`
   - Percentage: usually `70`

5. **Specify ground truth**
   - Column name: what column has the answer
   - File path: which CSV file

6. **Save CSV and run!**

---

## ⚠️ **Common Mistakes to Avoid**

### ❌ Mistake 1: Including JSON in rubric
**Wrong:**
```
Check accuracy. Return JSON: {"score": 1}
```

**Right:**
```
Check if the response is factually accurate
```

*System adds JSON format automatically!*

### ❌ Mistake 2: Including {variables} in rubric
**Wrong:**
```
Check if {response} matches {ground_truth}
```

**Right:**
```
Check if the response matches the ground truth
```

*System adds variables automatically!*

### ❌ Mistake 3: Wrong threshold for type
**Wrong:**
```
type: scale_1_5
threshold: 1.0  ← Too low! (everything passes)
```

**Right:**
```
type: scale_1_5
threshold: 3.0  ← Average or better
```

### ❌ Mistake 4: Vague rubric
**Wrong:**
```
Check if good
```

**Right:**
```
Check if the response is factually accurate with no errors
```

---

## 📊 **Column Presence Rules**

### Option 1: Simple Rubric (Recommended)
Use column: **`grading_rubric`**
```csv
name,type,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
accuracy,binary,Check if accurate,1.0,correct,gt.csv
```

### Option 2: Traditional (Also Supported)
Use column: **`evaluation_prompt`**
```csv
name,type,evaluation_prompt,threshold,ground_truth_column,ground_truth_file_path
accuracy,binary,Check if accurate,1.0,correct,gt.csv
```

**System checks both!** Use whichever you prefer.

---

## 🎓 **From Your Example**

### What You Had:
```csv
accuracy_check,binary,Checks if response contains accurate information,"Rate the accuracy... Return JSON: {""accuracy_check_score"": 1, ""explanation"": ""...""}",1.0,correct_answer,ground_truth_accuracy.csv
```

**Problems:**
- PM has to write JSON examples
- PM has to handle escaping quotes
- PM has to know format string syntax
- Too complicated!

### What You Should Have:
```csv
name,type,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
accuracy_check,binary,Check if the response is factually accurate by comparing to the ground truth. No factual errors allowed.,1.0,correct_answer,ground_truth_accuracy.csv
```

**Benefits:**
- ✅ Plain English only
- ✅ No JSON to write
- ✅ No quote escaping
- ✅ No format strings
- ✅ Just describe what to check!

**System automatically converts this into proper prompt!**

---

## 🔥 **The Magic: Auto-Prompt Generation**

When you write:
```
grading_rubric: "Check if the response is factually accurate"
type: binary
```

The system automatically generates:
```
You are an expert evaluator. Evaluate the AI response based on these criteria:

Check if the response is factually accurate

**User Query:** {prompt}

**AI Response:** {response}

**Ground Truth:** {ground_truth}

**Your Task:**
Return a score of 1 if the criteria is met, or 0 if not.

**Required Output Format:**
Return ONLY valid JSON:
{
  "score": 1,
  "explanation": "Brief explanation"
}
```

**You never see this! System handles it automatically!**

---

## 💡 **Real Examples from Different Industries**

### E-Commerce
```csv
name,type,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
product_accuracy,binary,Verify all product specifications and prices are correct,1.0,correct_specs,products_gt.csv
description_quality,scale_1_5,Rate product description quality from 1-5. Consider clarity and appeal,3.0,quality_notes,products_gt.csv
```

### Healthcare
```csv
name,type,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
medical_accuracy,binary,Verify medical information is accurate and safe. No incorrect medical advice,1.0,correct_medical_info,medical_gt.csv
patient_empathy,scale_1_5,Rate empathy and patient-centeredness from 1-5,4.0,empathy_notes,medical_gt.csv
```

### Legal
```csv
name,type,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
legal_accuracy,binary,Verify legal information is accurate. No incorrect legal advice,1.0,correct_legal_info,legal_gt.csv
comprehensibility,scale_1_5,Rate how understandable the legal explanation is for non-lawyers from 1-5,3.0,clarity_notes,legal_gt.csv
```

### Education
```csv
name,type,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
factual_correctness,binary,Verify all educational content is factually correct,1.0,correct_facts,education_gt.csv
age_appropriate,binary,Check if content is appropriate for target age group,1.0,age_rating,education_gt.csv
engagement,scale_1_5,Rate how engaging and interesting the content is from 1-5,4.0,engagement_score,education_gt.csv
```

---

## 🎯 **Checklist: Before Creating Your Metrics**

Ask yourself:

1. **What do I want to measure?**
   - Accuracy, helpfulness, safety, completeness, quality, etc.

2. **How should it be scored?**
   - Pass/Fail → binary
   - Quality rating → scale_1_5
   - Partial completion → percentage

3. **What's the minimum acceptable?**
   - Must pass every time → threshold: 1.0 (binary)
   - Should be above average → threshold: 3.0 (scale_1_5)
   - Should be mostly complete → threshold: 70 (percentage)

4. **Do I have the correct answers?**
   - Yes → specify ground_truth_column and ground_truth_file_path
   - No → use "Not provided" (judge uses general knowledge)

---

## ✅ **Your Simple 3-Column Format**

If you want the absolute minimum:

```csv
name,type,grading_rubric
accuracy,binary,Check if factually accurate
helpfulness,scale_1_5,Rate helpfulness from 1-5
safety,binary,Check if safe and appropriate
```

**System will use defaults for:**
- threshold (1.0 for binary, 3.0 for scale, 70 for percentage)
- ground_truth (will try to find it automatically)

---

## 🎉 **Bottom Line**

**Old Way (Complex):**
- Write JSON examples
- Handle quote escaping
- Include format strings
- Know technical syntax

**New Way (Simple):**
- Write plain English rubric
- Choose metric type
- Set threshold
- Done!

**The code does all the hard work for you!** 🚀

---

## 📞 **Quick Reference**

| I Want To... | Use Type | Example Rubric |
|-------------|----------|----------------|
| Check yes/no | `binary` | "Check if response is accurate" |
| Rate quality | `scale_1_5` | "Rate clarity from 1-5" |
| Measure completeness | `percentage` | "What % of info is included" |
| Verify safety | `binary` | "Check if safe for all ages" |
| Rate helpfulness | `scale_1_5` | "Rate helpfulness from 1-5" |

**That's all you need to know!** ✅
