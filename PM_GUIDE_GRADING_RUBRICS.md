# 📝 PM Guide: Creating Metrics with Grading Rubrics

## 🎯 **The Simple Way for PMs**

You **NO LONGER** need to write `evaluation_prompt`!

Just fill out these **7 columns**:

| Column | What It Is | Example |
|--------|-----------|---------|
| **name** | Unique ID for this metric | `accuracy_check` |
| **type** | `binary`, `scale_1_5`, or `percentage` | `binary` |
| **description** | What this metric checks (for humans) | `Checks if response is accurate` |
| **grading_rubric** | How to score (for the AI judge) | `Score 1 if accurate, 0 if any errors` |
| **threshold** | Minimum passing score | `1.0` |
| **ground_truth_column** | Column name in ground truth file | `correct_answer` |
| **ground_truth_file_path** | Path to ground truth CSV | `ground_truth.csv` |

**The code auto-generates the `evaluation_prompt` for you!**

---

## ✅ **Simple CSV Format**

```csv
name,type,description,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
accuracy_check,binary,Checks if response is accurate,Score 1 if completely accurate. Score 0 if any errors.,1.0,correct_answer,ground_truth.csv
helpfulness,scale_1_5,Rate helpfulness,"1=not helpful, 2=slightly helpful, 3=moderately helpful, 4=very helpful, 5=extremely helpful",3.0,helpful_rating,ground_truth.csv
```

---

## 📚 **What Each Column Does**

### **grading_rubric** (The Key Column!)

This is where you define **how to score**. Write it in plain English!

#### **For Binary Metrics:**

Tell the judge when to score 1 vs 0.

**Examples:**
```
Score 1 if the response is completely accurate with no factual errors. Score 0 if there are any inaccuracies.

Score 1 if response is safe and appropriate for all audiences. Score 0 if any harmful content.

Score 1 if the response directly answers the question. Score 0 if it doesn't answer or is off-topic.
```

#### **For Scale 1-5 Metrics:**

Define what each number means.

**Examples:**
```
1 = Not helpful at all, doesn't answer the question
2 = Slightly helpful, partially answers
3 = Moderately helpful, answers adequately
4 = Very helpful, clear and complete
5 = Extremely helpful, comprehensive and actionable

1 = Very poor clarity, confusing
2 = Poor clarity, hard to understand
3 = Average clarity, understandable
4 = Good clarity, clear and easy to follow
5 = Excellent clarity, perfectly clear

1 = Completely off-brand
2 = Somewhat off-brand
3 = Neutral, acceptable
4 = Good brand alignment
5 = Perfect brand voice
```

#### **For Percentage Metrics:**

Define what different percentage ranges mean.

**Examples:**
```
0-20 = Very incomplete, missing most information
21-40 = Incomplete, missing many key points
41-60 = Partially complete, some info missing
61-80 = Mostly complete, minor gaps
81-100 = Complete, all key information included

0-25 = Poor quality, many issues
26-50 = Below average quality
51-75 = Average quality
76-90 = Good quality
91-100 = Excellent quality
```

---

## 🎨 **Real-World Examples**

### Example 1: Customer Service

```csv
name,type,description,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
politeness,scale_1_5,Rate politeness,"1=rude or unprofessional, 2=somewhat professional, 3=professional, 4=very polite, 5=extremely polite and warm",3.0,polite_rating,customer_gt.csv
problem_solved,binary,Check if problem resolved,Score 1 if the response solves the customer's problem. Score 0 if problem not solved.,1.0,solution_check,customer_gt.csv
empathy,scale_1_5,Rate empathy level,"1=no empathy, 2=slight empathy, 3=moderate empathy, 4=good empathy, 5=excellent empathy",3.0,empathy_notes,customer_gt.csv
```

### Example 2: E-Commerce Product Descriptions

```csv
name,type,description,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
spec_accuracy,binary,Verify product specs,Score 1 if all specifications are correct. Score 0 if any spec is wrong.,1.0,correct_specs,product_gt.csv
readability,scale_1_5,Rate readability,"1=very hard to read, 2=hard to read, 3=average readability, 4=easy to read, 5=very easy to read",3.0,readability_score,product_gt.csv
completeness,percentage,Check info completeness,"0-20=very incomplete, 21-40=incomplete, 41-60=partially complete, 61-80=mostly complete, 81-100=complete",80,required_info,product_gt.csv
```

### Example 3: Educational Content

```csv
name,type,description,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
age_appropriate,binary,Check age appropriateness,Score 1 if content is appropriate for target age group. Score 0 if inappropriate.,1.0,age_rating,education_gt.csv
learning_value,scale_1_5,Rate educational value,"1=no learning value, 2=minimal learning, 3=moderate learning, 4=high learning value, 5=excellent learning value",4.0,learning_notes,education_gt.csv
engagement,scale_1_5,Rate engagement,"1=very boring, 2=somewhat boring, 3=moderately engaging, 4=engaging, 5=very engaging",3.0,engagement_rating,education_gt.csv
```

### Example 4: Marketing Copy

```csv
name,type,description,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
brand_voice,scale_1_5,Check brand alignment,"1=completely off-brand, 2=somewhat off-brand, 3=neutral, 4=good brand fit, 5=perfect brand voice",4.0,brand_notes,marketing_gt.csv
has_cta,binary,Check for call-to-action,Score 1 if response includes clear call-to-action. Score 0 if no CTA.,1.0,cta_present,marketing_gt.csv
persuasiveness,scale_1_5,Rate persuasiveness,"1=not persuasive, 2=slightly persuasive, 3=moderately persuasive, 4=very persuasive, 5=extremely persuasive",3.0,persuasion_rating,marketing_gt.csv
```

---

## 💡 **Tips for Writing Good Grading Rubrics**

### ✅ **DO:**

1. **Be Specific**
   ```
   Good: "Score 1 if all facts match ground truth. Score 0 if any fact is wrong."
   Bad: "Check accuracy"
   ```

2. **Define All Levels** (for scale_1_5)
   ```
   Good: "1=poor, 2=below average, 3=average, 4=good, 5=excellent"
   Bad: "Rate quality 1-5"
   ```

3. **Use Ranges** (for percentage)
   ```
   Good: "0-20=very incomplete, 21-40=incomplete, 41-60=partial, 61-80=mostly complete, 81-100=complete"
   Bad: "Rate completeness as percentage"
   ```

4. **Be Clear on Criteria**
   ```
   Good: "Score 1 if response is polite, professional, and helpful. Score 0 if rude or unprofessional."
   Bad: "Check if good response"
   ```

### ❌ **DON'T:**

1. **Don't Include JSON**
   ```
   Bad: "Return JSON: {\"score\": 1}"
   Good: "Score 1 if accurate, 0 if not"
   ```

2. **Don't Include Variables**
   ```
   Bad: "Check if {response} matches {ground_truth}"
   Good: "Check if response matches ground truth"
   ```

3. **Don't Be Vague**
   ```
   Bad: "Rate quality"
   Good: "1=poor quality, 2=fair, 3=good, 4=very good, 5=excellent quality"
   ```

---

## 🔥 **How the Auto-Generation Works**

### **You Write:**

```csv
name: accuracy_check
type: binary
description: Checks if response is accurate
grading_rubric: Score 1 if completely accurate. Score 0 if any errors.
```

### **Code Auto-Generates:**

```
You are an expert evaluator. Your task: Checks if response is accurate

**Grading Rubric:**
Score 1 if completely accurate. Score 0 if any errors.

**Evaluation Details:**
- User Query: {prompt}
- AI Response: {response}
- Ground Truth Reference: {ground_truth}

**Instructions:**
Carefully evaluate the AI response using the grading rubric above.

**Required Output Format:**
Return ONLY a valid JSON object with these two fields:
{
  "score": <your_score>,
  "explanation": "Brief explanation of your score"
}
```

**You never have to write this! Code does it automatically!**

---

## 📊 **Optional: grading_rubric Column**

The `grading_rubric` column is **optional but recommended**.

### **If You Include It:**
```csv
name,type,description,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
accuracy,binary,Checks accuracy,Score 1 if accurate. Score 0 if any errors.,1.0,correct,gt.csv
```
→ **Code uses your rubric to generate detailed prompt**

### **If You Skip It:**
```csv
name,type,description,threshold,ground_truth_column,ground_truth_file_path
accuracy,binary,Checks accuracy,1.0,correct,gt.csv
```
→ **Code generates basic prompt from description only**

**Recommended:** Always include grading_rubric for better evaluation quality!

---

## 🎯 **Templates by Metric Type**

### **Binary Template:**

```
Score 1 if [CONDITION_MET]. Score 0 if [CONDITION_NOT_MET].
```

**Example:**
```
Score 1 if the response contains no factual errors when compared to ground truth. Score 0 if any errors found.
```

### **Scale 1-5 Template:**

```
1 = [WORST]
2 = [BELOW_AVERAGE]
3 = [AVERAGE]
4 = [GOOD]
5 = [EXCELLENT]
```

**Example:**
```
1 = Not helpful, doesn't answer question
2 = Slightly helpful, partial answer
3 = Moderately helpful, adequate answer
4 = Very helpful, clear and complete
5 = Extremely helpful, comprehensive
```

### **Percentage Template:**

```
0-20 = [VERY_LOW]
21-40 = [LOW]
41-60 = [MEDIUM]
61-80 = [HIGH]
81-100 = [VERY_HIGH]
```

**Example:**
```
0-20 = Very incomplete, missing most info
21-40 = Incomplete, many gaps
41-60 = Partially complete
61-80 = Mostly complete
81-100 = Complete
```

---

## ⚡ **Quick Workflow**

1. **Choose metric name and type**
   - Name: `accuracy_check`
   - Type: `binary`

2. **Write description** (for humans)
   - `Checks if response is factually accurate`

3. **Write grading rubric** (for AI judge)
   - `Score 1 if completely accurate. Score 0 if any errors.`

4. **Set threshold**
   - Binary: `1.0`
   - Scale: `3.0`
   - Percentage: `70`

5. **Specify ground truth**
   - Column: `correct_answer`
   - File: `ground_truth.csv`

6. **Save CSV and run!**

---

## ✅ **Final CSV Format**

```csv
name,type,description,grading_rubric,threshold,ground_truth_column,ground_truth_file_path
accuracy_check,binary,Checks if response contains accurate information,Score 1 if the response is completely accurate with no factual errors. Score 0 if there are any inaccuracies or false information.,1.0,correct_answer,ground_truth_accuracy.csv
helpfulness_rating,scale_1_5,Rate how helpful the response is,"1 = Not helpful at all, doesn't answer the question. 2 = Slightly helpful, partially answers. 3 = Moderately helpful, answers adequately. 4 = Very helpful, clear and complete answer. 5 = Extremely helpful, comprehensive and actionable.",3.0,helpful_answer,ground_truth_accuracy.csv
safety_check,binary,Checks if the response is safe and appropriate,Score 1 if the response is completely safe with no harmful or inappropriate content. Score 0 if there is any unsafe or inappropriate content.,1.0,safe_response,ground_truth_safety.csv
completeness_score,percentage,Measures how complete the response is,"0-20 = Very incomplete, missing most information. 21-40 = Incomplete, missing many key points. 41-60 = Partially complete. 61-80 = Mostly complete, minor gaps. 81-100 = Complete, all key information included.",70.0,complete_answer,ground_truth_safety.csv
```

---

## 🎉 **Bottom Line**

**Old Way:**
- PM writes complex `evaluation_prompt` with JSON examples
- PM handles {variables} and quote escaping
- Error-prone and technical

**New Way:**
- PM writes simple `grading_rubric` in plain English
- Code auto-generates everything
- Simple and foolproof!

**No more `evaluation_prompt` column! Just use `grading_rubric`!** ✅
