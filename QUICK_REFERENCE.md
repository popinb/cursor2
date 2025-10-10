# LLM Judge Workshop - Quick Reference Guide

## 📋 Cheat Sheet for Workshop Participants

### Essential File Paths
```
Notebook: /Workspace/Users/[your-email]/llm_judge_workshop
Data: /dbfs/FileStore/llm_judge/evaluation_data.csv
Results: /dbfs/FileStore/llm_judge/results/
```

### Cell Execution Order
```
1. Install packages      → Run once, restart Python
2. Import libraries      → Run after restart
3. Configure data        → Set your file paths
4. Configure model       → Choose judge model
5. Define metrics        → Create evaluation criteria
6. Load system classes   → Run as-is
7. Run evaluation        → Execute evaluation
8. View summary          → See results
9. Export results        → Save to CSV
10. Log to MLflow        → Track experiments
```

---

## 🎯 Metric Types Quick Reference

### Binary (Pass/Fail)
```python
{
    "name": "metric_name",
    "type": "binary",
    "evaluation_prompt": "... Return {\"metric_name_score\": 1, \"explanation\": \"...\"}"
}
```
- **Score**: 0 or 1
- **Threshold**: 1.0
- **Use for**: Accuracy, compliance, safety

### Scale (1-5)
```python
{
    "name": "metric_name",
    "type": "scale_1_5",
    "evaluation_prompt": "... Return {\"metric_name_score\": 4, \"explanation\": \"...\"}"
}
```
- **Score**: 1, 2, 3, 4, or 5
- **Threshold**: 3.0
- **Use for**: Quality, helpfulness, clarity

### Percentage (0-100%)
```python
{
    "name": "metric_name",
    "type": "percentage",
    "evaluation_prompt": "... Return {\"metric_name_score\": 0.85, \"explanation\": \"...\"}"
}
```
- **Score**: 0.0 to 1.0 (0% to 100%)
- **Threshold**: 0.7 (70%)
- **Use for**: Completeness, coverage

---

## 🔧 Common Modifications

### Change Judge Model
In **Cell 4**, select from dropdown:
- `gpt-4o` - Most capable, slower, higher cost
- `gpt-4o-mini` - Fast, cost-effective, recommended
- `gpt-3.5-turbo` - Fastest, lowest cost

### Adjust Batch Size
In **Cell 4**, select from dropdown:
- `1` - Show progress for each sample
- `5` - Good balance (default)
- `10` - Faster for large datasets
- `20` - Maximum speed

### Change Pass Thresholds
In **Cell 5**, modify:
```python
METRIC_THRESHOLDS = {
    "accuracy": 1.0,        # Binary: must be 1
    "helpfulness": 4.0,     # Scale: change to 4 for stricter
    "completeness": 0.8     # Percentage: change to 0.8 for 80%
}
```

### Update File Paths
In **Cell 3** widgets:
- Evaluation Data: `/dbfs/FileStore/your_folder/your_file.csv`
- Ground Truth: `/dbfs/FileStore/your_folder/ground_truth.csv`
- Format: `csv` or `docx`

---

## 📊 Reading Results

### Score Columns
- `metric_name_score` - Numerical score
- `metric_name_explanation` - Judge's reasoning
- `metric_name_status` - ✅ PASS or ❌ FAIL

### Summary Statistics
- **Mean** - Average score across all samples
- **Median** - Middle value (ignore outliers)
- **Std Dev** - How much scores vary
- **Pass Rate** - % meeting threshold
- **Min/Max** - Range of scores

### Visualizations
- **Histogram** - Distribution of scores
- **Threshold Line** - Pass/fail cutoff (red dashed line)
- **Bar Chart** - Pass rates comparison

---

## 🐛 Troubleshooting

### "Connection Failed"
```python
# Check secret configuration
dbutils.secrets.get("popin-secure-scope", "openai_key")
```

### "File Not Found"
```python
# List files in directory
dbutils.fs.ls("/FileStore/llm_judge/")

# Check if file exists
import os
os.path.exists("/dbfs/FileStore/llm_judge/evaluation_data.csv")
```

### "Missing Columns"
```python
# Check your CSV columns
import pandas as pd
df = pd.read_csv("/dbfs/FileStore/llm_judge/evaluation_data.csv")
print(df.columns.tolist())
# Must have: ['prompt', 'response']
```

### "Invalid JSON Response"
- Make sure your prompt specifies **exact** JSON format
- Include the metric name in the score key: `"metric_name_score"`
- Use double quotes in JSON example

### "Evaluation Too Slow"
1. Reduce batch size to 1 (see progress sooner)
2. Switch to `gpt-4o-mini` (faster model)
3. Test with subset first: `df.head(10)`

---

## 💡 Pro Tips

### Testing New Metrics
1. Start with 5-10 samples
2. Review explanations carefully
3. Iterate on prompt wording
4. Test edge cases
5. Scale to full dataset

### Cost Estimation
```
Approximate costs (per 1000 evaluations):
- gpt-4o-mini: $0.15 - $0.30
- gpt-4o: $5 - $10
- gpt-3.5-turbo: $0.05 - $0.10

Formula: samples × metrics × tokens_per_eval × price_per_token
```

### Best Practices
✅ **Do**:
- Define clear evaluation criteria
- Include examples in prompts
- Test with small batches first
- Use ground truth when available
- Document your metrics

❌ **Don't**:
- Use vague criteria
- Skip testing with samples
- Ignore explanation quality
- Forget to version experiments
- Mix metric types in one evaluation

---

## 🎓 Workshop Exercises

### Exercise 1: Basic Run (15 min)
1. Run cells 1-4 with defaults
2. Review sample metrics in Cell 5
3. Execute evaluation (Cell 7)
4. Analyze results (Cell 8)

### Exercise 2: Custom Metric (20 min)
1. Add a new metric in Cell 5:
   - Binary: "relevance"
   - Scale: "professionalism"
   - Percentage: "detail_level"
2. Run evaluation
3. Compare with existing metrics

### Exercise 3: Your Data (25 min)
1. Upload your CSV file
2. Modify metrics for your use case
3. Run full evaluation
4. Export and share results

### Exercise 4: Compare Models (20 min)
1. Run with `gpt-4o-mini`
2. Log to MLflow
3. Change to `gpt-4o` in Cell 4
4. Run again and compare in MLflow UI

---

## 📖 Metric Template Library

### Copy-Paste Templates

#### Relevance (Binary)
```python
{
    "name": "relevance",
    "type": "binary",
    "description": "Checks if response is relevant to the query",
    "evaluation_prompt": """
Is the response relevant to the user's query?

User Query: {prompt}
AI Response: {response}

Score 1 if relevant, 0 if not.

Return JSON:
{{
    "relevance_score": 1,
    "explanation": "Response directly addresses the question about..."
}}
"""
}
```

#### Clarity (Scale)
```python
{
    "name": "clarity",
    "type": "scale_1_5",
    "description": "Rates how clear and understandable the response is",
    "evaluation_prompt": """
Rate the clarity of this response from 1-5.

User Query: {prompt}
AI Response: {response}

5 = Crystal clear, easy to understand
4 = Clear with minor areas of confusion
3 = Moderately clear
2 = Somewhat confusing
1 = Very confusing or unclear

Return JSON:
{{
    "clarity_score": 4,
    "explanation": "Response is clear and well-structured with..."
}}
"""
}
```

#### Coverage (Percentage)
```python
{
    "name": "coverage",
    "type": "percentage",
    "description": "Measures how much of the topic is covered",
    "evaluation_prompt": """
What percentage of the topic is covered in the response?

User Query: {prompt}
AI Response: {response}
Ground Truth: {ground_truth}

Calculate coverage as a decimal (0.0 to 1.0).

Return JSON:
{{
    "coverage_score": 0.75,
    "explanation": "Covers 75% of the topic, missing information about..."
}}
"""
}
```

---

## 🔗 Useful Commands

### View MLflow Experiments
```python
# List all experiments
import mlflow
experiments = mlflow.search_experiments()
for exp in experiments:
    print(f"{exp.name}: {exp.experiment_id}")
```

### Load Previous Results
```python
# Load results from CSV
results_df = pd.read_csv("/dbfs/FileStore/llm_judge/results/llm_judge_results_20251010_120000.csv")
display(results_df)
```

### Compare Two Runs
```python
# In MLflow UI: Experiments → Select experiment → Check 2 runs → Compare
```

### Export Specific Columns
```python
# Export only scores
scores_df = results_df[['prompt'] + [col for col in results_df.columns if '_score' in col]]
scores_df.to_csv("/dbfs/FileStore/llm_judge/scores_only.csv", index=False)
```

---

## 📞 Getting Help

### During Workshop
1. 🙋 Raise hand for facilitator
2. 💬 Use Slack channel
3. 👥 Ask your neighbor
4. 📖 Check this reference

### After Workshop
- 📧 Email: [support-email]
- 📚 Full README: `/workspace/README_LLM_JUDGE_WORKSHOP.md`
- 🔗 Wiki: [your-wiki-link]

---

## ⚡ Keyboard Shortcuts (Databricks)

- `Shift + Enter` - Run cell and move to next
- `Ctrl + Enter` - Run cell and stay
- `Esc` - Command mode
- `A` - Insert cell above (command mode)
- `B` - Insert cell below (command mode)
- `D + D` - Delete cell (command mode)

---

**Happy Evaluating! 🚀**

*Remember: LLM judges are powerful but not perfect. Always review results critically and use human judgment for final decisions.*
