# LLM Judge Workshop - Evaluation Framework

## Overview
This Databricks notebook provides a production-ready framework for evaluating AI responses using Large Language Models (LLMs) as judges. It's designed for product managers, data scientists, and ML engineers who need to systematically evaluate AI system outputs.

## What is LLM-as-a-Judge?
LLM-as-a-Judge is an evaluation methodology where a powerful language model (like GPT-4) evaluates the quality of responses from another AI system. This approach provides:
- **Scalability**: Evaluate thousands of responses automatically
- **Consistency**: Standardized evaluation criteria across all samples
- **Flexibility**: Custom metrics tailored to your use case
- **Speed**: Faster than human evaluation for initial assessments

## Prerequisites

### Required Access
- Databricks workspace with cluster access
- API key for OpenAI models (stored in Databricks secrets)
  - Secret scope: `popin-secure-scope`
  - Secret key: `openai_key`

### Input Data Format
Your evaluation data CSV must contain:
- `prompt`: The user's input question/query
- `response`: The AI's response to evaluate

Optional columns:
- `ground_truth`: Reference answer for comparison (recommended)
- Any additional metadata columns

### Example CSV:
```csv
prompt,response,ground_truth
"What is a mortgage?","A mortgage is a loan used to purchase property...","A mortgage is a loan secured by real property..."
```

## Quick Start Guide

### Step 1: Upload the Notebook
1. Open Databricks workspace
2. Navigate to Workspace → Import
3. Select `llm_judge_workshop.py`
4. Import as Python notebook

### Step 2: Prepare Your Data
1. Upload your evaluation data CSV to DBFS:
   ```
   /dbfs/FileStore/llm_judge/evaluation_data.csv
   ```
2. (Optional) Upload ground truth CSV:
   ```
   /dbfs/FileStore/llm_judge/ground_truth.csv
   ```

### Step 3: Configure API Access
Ensure your OpenAI API key is stored in Databricks secrets:
```python
dbutils.secrets.get("popin-secure-scope", "openai_key")
```

### Step 4: Run the Notebook
Execute cells in order:
1. **Cell 1**: Install dependencies
2. **Cell 2**: Import libraries  
3. **Cell 3**: Configure data paths
4. **Cell 4**: Select judge model and settings
5. **Cell 5**: Define custom metrics (see below)
6. **Cell 6**: Load system classes
7. **Cell 7**: Run evaluation
8. **Cell 8**: View summary report
9. **Cell 9**: Export results
10. **Cell 10**: Log to MLflow

## Defining Custom Metrics

### Three Metric Types

#### 1. Binary (Pass/Fail)
Use for clear yes/no criteria.

**Example**: Accuracy Check
- Score: 0 (fail) or 1 (pass)
- Threshold: 1.0 (must pass)
- Use cases: Factual accuracy, compliance checks, safety validation

```python
{
    "name": "accuracy",
    "type": "binary",
    "description": "Checks if response is factually accurate",
    "evaluation_prompt": """
Evaluate accuracy...
Return JSON:
{
    "accuracy_score": 1,
    "explanation": "All facts verified"
}
"""
}
```

#### 2. Scale (1-5 Rating)
Use for quality assessments.

**Example**: Helpfulness Rating
- Score: 1 (worst) to 5 (best)
- Threshold: 3.0 (adequate or better)
- Use cases: Helpfulness, clarity, professionalism

```python
{
    "name": "helpfulness",
    "type": "scale_1_5",
    "description": "Rates helpfulness on 1-5 scale",
    "evaluation_prompt": """
Rate helpfulness from 1-5...
Return JSON:
{
    "helpfulness_score": 4,
    "explanation": "Very helpful with actionable advice"
}
"""
}
```

#### 3. Percentage (0-100%)
Use for completeness or coverage metrics.

**Example**: Completeness
- Score: 0.0 to 1.0 (0% to 100%)
- Threshold: 0.7 (70% coverage)
- Use cases: Completeness, coverage, comprehensiveness

```python
{
    "name": "completeness",
    "type": "percentage",
    "description": "Measures coverage of the question",
    "evaluation_prompt": """
Calculate percentage of question addressed...
Return JSON:
{
    "completeness_score": 0.85,
    "explanation": "Addressed 85% of question components"
}
"""
}
```

### Best Practices for Metrics

1. **Be Specific**: Clearly define what you're measuring
2. **Use Examples**: Include scoring examples in your prompt
3. **JSON Format**: Always specify exact JSON format expected
4. **Placeholders**: Use `{prompt}`, `{response}`, `{ground_truth}`
5. **Explanations**: Require the judge to explain its reasoning

## Workshop Exercises

### Exercise 1: Run with Sample Data
1. Run notebook cells 1-4 without modifications
2. Cell 3 will create sample data automatically
3. Use the provided example metrics
4. Review results in Cell 8

### Exercise 2: Create Custom Metrics
1. Define 2-3 metrics relevant to your use case
2. Test with sample data
3. Iterate on prompts based on results

### Exercise 3: Evaluate Your Own Data
1. Upload your actual evaluation data
2. Adjust metrics to match your requirements
3. Run full evaluation
4. Export results and share with team

### Exercise 4: Compare Models
1. Run evaluation with `gpt-4o-mini`
2. Note the results
3. Re-run with `gpt-4o`
4. Compare using MLflow UI

## Understanding Results

### Summary Report (Cell 8)
- **Mean Score**: Average across all samples
- **Median Score**: Middle value (robust to outliers)
- **Std Dev**: Variability in scores
- **Pass Rate**: Percentage meeting threshold
- **Visualizations**: Histograms and comparison charts

### Output Files (Cell 9)
1. **Detailed Results CSV**: All scores and explanations per sample
2. **Summary CSV**: Aggregate statistics by metric
3. **Config JSON**: Metric definitions used

### MLflow Tracking (Cell 10)
- Compare different evaluation runs
- Track metric performance over time
- Version control for experiments

## Troubleshooting

### Common Issues

#### "API Connection Failed"
- Check Databricks secrets configuration
- Verify API key is valid
- Ensure network connectivity to Zillow API endpoint

#### "File Not Found"
- Verify file path starts with `/dbfs/`
- Check file was uploaded successfully
- Use full path, not relative path

#### "Missing Required Columns"
- Ensure CSV has `prompt` and `response` columns
- Check column names (case-sensitive)
- Verify no extra spaces in column names

#### "Invalid JSON Response"
- Review your evaluation prompt
- Ensure you specify exact JSON format
- Check for ambiguous instructions

#### "Evaluation Taking Too Long"
- Reduce batch size in Cell 4
- Use faster model (gpt-4o-mini vs gpt-4o)
- Consider parallelization options

## Performance Optimization

### Tips for Large Datasets
1. **Start Small**: Test with 10-20 samples first
2. **Batch Processing**: Adjust batch_size parameter
3. **Model Selection**: Use `gpt-4o-mini` for faster evaluation
4. **Concurrent Evaluation**: Consider async processing for production

### Cost Management
- `gpt-4o-mini`: ~$0.15 per 1M input tokens
- `gpt-4o`: ~$5 per 1M input tokens
- Estimate: ~500 tokens per evaluation
- Example: 1000 samples ≈ $0.075 (mini) or $2.50 (gpt-4o)

## Advanced Usage

### Adding Multiple Ground Truth Sources
```python
# In Cell 3 widget
ground_truth_paths = "/path/to/file1.csv,/path/to/file2.csv,/path/to/file3.docx"
```

### Custom Thresholds
Modify in Cell 5:
```python
METRIC_THRESHOLDS = {
    "accuracy": 1.0,      # Must be perfect
    "helpfulness": 4.0,   # Must be very helpful
    "completeness": 0.8   # Must cover 80%+
}
```

### Exporting to Different Locations
Modify in Cell 9:
```python
output_dir = "/dbfs/FileStore/my_custom_folder"
```

## Workshop Resources

### Sample Use Cases
1. **Customer Support**: Evaluate response quality, empathy, accuracy
2. **Content Generation**: Assess creativity, relevance, tone
3. **Question Answering**: Measure accuracy, completeness, clarity
4. **Summarization**: Evaluate coverage, conciseness, factual accuracy
5. **Code Generation**: Check correctness, efficiency, best practices

### Metric Template Library
Copy these templates and modify for your needs:

**Conciseness**:
```python
{
    "name": "conciseness",
    "type": "scale_1_5",
    "description": "Evaluates if response is appropriately concise",
    "evaluation_prompt": "Rate conciseness 1-5, where 5=perfectly concise..."
}
```

**Relevance**:
```python
{
    "name": "relevance", 
    "type": "binary",
    "description": "Checks if response is relevant to the query",
    "evaluation_prompt": "Determine if response addresses the query..."
}
```

**Tone Appropriateness**:
```python
{
    "name": "tone",
    "type": "scale_1_5", 
    "description": "Evaluates professional and appropriate tone",
    "evaluation_prompt": "Rate tone from 1-5, considering professionalism..."
}
```

## Support and Feedback

### During Workshop
- Raise your hand for immediate help
- Use Slack channel for quick questions
- Share interesting findings with the group

### After Workshop
- Email: [your-support-email]
- Documentation: [wiki-link]
- Slack: #llm-evaluation

## Additional Resources

### Further Reading
- [LLM-as-a-Judge Paper](https://arxiv.org/abs/2306.05685)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)

### Related Tools
- **LangChain**: For more complex evaluation pipelines
- **Weights & Biases**: Alternative experiment tracking
- **Argilla**: Human-in-the-loop evaluation platform

## License and Usage
This notebook is provided as an internal tool for evaluation purposes. Please follow your organization's data handling and API usage policies.

---

**Version**: 1.0  
**Last Updated**: 2025-10-10  
**Maintainer**: [Your Team Name]
