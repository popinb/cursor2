# Workshop Setup Checklist

## Pre-Workshop Preparation (1 Week Before)

### ✅ Infrastructure Setup
- [ ] Databricks workspace configured and accessible
- [ ] Cluster with Python 3.9+ available
- [ ] OpenAI API key obtained and tested
- [ ] Databricks secrets configured:
  - Secret scope: `popin-secure-scope`
  - Secret key: `openai_key`
- [ ] MLflow workspace enabled
- [ ] DBFS FileStore accessible

### ✅ Notebook Preparation
- [ ] Upload `llm_judge_workshop.py` to Databricks
- [ ] Test run all cells with sample data
- [ ] Verify API connections work
- [ ] Confirm MLflow logging works
- [ ] Check CSV exports to DBFS

### ✅ Sample Data Preparation
- [ ] Upload `sample_evaluation_data.csv` to `/dbfs/FileStore/llm_judge/`
- [ ] Test loading sample data in notebook
- [ ] Verify ground truth matching works
- [ ] Create additional example datasets (optional)

### ✅ Documentation
- [ ] Share `README_LLM_JUDGE_WORKSHOP.md` with participants
- [ ] Share `QUICK_REFERENCE.md` as handout
- [ ] Prepare slide deck (optional)
- [ ] Create Slack/Teams channel for questions

---

## Day Before Workshop

### ✅ Technical Checks
- [ ] Test notebook end-to-end one more time
- [ ] Verify all participants have Databricks access
- [ ] Confirm API keys are working
- [ ] Test screen sharing setup
- [ ] Prepare backup cluster if needed

### ✅ Materials
- [ ] Email pre-read materials to participants
- [ ] Share sample datasets
- [ ] Send calendar reminder with Zoom/meeting link
- [ ] Prepare troubleshooting guide

### ✅ Environment
- [ ] Book meeting room with good WiFi
- [ ] Test projector/screen sharing
- [ ] Prepare whiteboard for diagrams
- [ ] Have backup plan for technical issues

---

## Day of Workshop - Setup (30 min before)

### ✅ Technical Setup
- [ ] Start Databricks cluster (takes 5-10 min)
- [ ] Open notebook and verify it's ready
- [ ] Test API connection one final time
- [ ] Open MLflow UI in separate tab
- [ ] Prepare file explorer with sample data

### ✅ Presentation Setup
- [ ] Connect laptop to projector
- [ ] Test screen sharing
- [ ] Open all necessary tabs:
  - Databricks notebook
  - MLflow UI
  - Documentation
  - Slack channel
- [ ] Increase font size for visibility
- [ ] Close unnecessary applications

### ✅ Materials Distribution
- [ ] Share links in chat:
  - Databricks workspace
  - Documentation
  - Sample data location
  - Slack channel
- [ ] Confirm everyone can access links

---

## Workshop Agenda (2 hours)

### Introduction (15 min)
- [ ] Welcome and introductions
- [ ] Overview of LLM-as-a-Judge concept
- [ ] Workshop goals and outcomes
- [ ] Logistics (breaks, Q&A, etc.)

### Demo: Notebook Walkthrough (20 min)
- [ ] Show Cell 1-2: Setup and imports
- [ ] Explain Cell 3: Data configuration
- [ ] Show Cell 4: Model selection
- [ ] Deep dive Cell 5: Metric definitions
- [ ] Quick overview Cell 6-10
- [ ] Run evaluation with sample data
- [ ] Show results and visualizations

### Exercise 1: Basic Run (15 min)
- [ ] Participants run cells 1-7
- [ ] Use provided sample data
- [ ] Review results together
- [ ] Address any errors

### Break (10 min)

### Deep Dive: Creating Metrics (20 min)
- [ ] Explain three metric types in detail
- [ ] Show good vs. bad metric examples
- [ ] Demonstrate prompt engineering tips
- [ ] Live coding: create metric together

### Exercise 2: Custom Metrics (20 min)
- [ ] Participants create 2-3 custom metrics
- [ ] Test with sample data
- [ ] Share interesting results
- [ ] Troubleshoot issues

### Exercise 3: Your Own Data (15 min)
- [ ] Participants upload their data
- [ ] Adapt metrics to their use case
- [ ] Run evaluation
- [ ] Review results

### Wrap Up (15 min)
- [ ] Review key learnings
- [ ] Show MLflow comparison
- [ ] Best practices recap
- [ ] Q&A session
- [ ] Share resources for continued learning

---

## Post-Workshop

### ✅ Immediate Follow-Up (Same Day)
- [ ] Share recording (if recorded)
- [ ] Send thank you email
- [ ] Share additional resources
- [ ] Create shared notebook for reference

### ✅ Within 1 Week
- [ ] Send feedback survey
- [ ] Compile Q&A from workshop
- [ ] Share FAQ document
- [ ] Offer 1-on-1 office hours

### ✅ Ongoing Support
- [ ] Monitor Slack channel for questions
- [ ] Update documentation based on feedback
- [ ] Schedule follow-up session (optional)
- [ ] Share success stories from participants

---

## Troubleshooting Quick Reference

### Issue: API Connection Fails
**Solution**: 
```python
# Verify secret
key = dbutils.secrets.get("popin-secure-scope", "openai_key")
print(f"Key starts with: {key[:10]}...")

# Test connection
import openai
client = OpenAI(api_key=key, base_url="https://api.zillowlabs.com/openai/v1")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "test"}],
    max_tokens=5
)
```

### Issue: File Not Found
**Solution**:
```python
# Check DBFS
dbutils.fs.ls("/FileStore/llm_judge/")

# Upload file via UI
# Workspace → Data → Upload file to DBFS
```

### Issue: Package Installation Fails
**Solution**:
```python
# Restart cluster and try again
# Or install individually:
%pip install mlflow==2.10.0
dbutils.library.restartPython()
```

### Issue: MLflow Not Logging
**Solution**:
```python
# Check experiment exists
import mlflow
try:
    experiment = mlflow.get_experiment_by_name("/Users/[email]/llm_judge_evaluation")
    print(f"Experiment ID: {experiment.experiment_id}")
except:
    mlflow.create_experiment("/Users/[email]/llm_judge_evaluation")
```

### Issue: Evaluation Too Slow
**Solution**:
- Switch to smaller sample: `df.head(10)`
- Use faster model: `gpt-4o-mini`
- Reduce batch size to 1 for visibility

---

## Success Criteria

Workshop is successful if participants can:
- ✅ Load and validate evaluation data
- ✅ Define at least one custom metric
- ✅ Run evaluation successfully
- ✅ Interpret results and visualizations
- ✅ Export results to CSV
- ✅ Understand when to use each metric type

---

## Resources for Participants

### Documentation
- Full README: `/workspace/README_LLM_JUDGE_WORKSHOP.md`
- Quick Reference: `/workspace/QUICK_REFERENCE.md`
- Sample Data: `/workspace/sample_evaluation_data.csv`

### Online Resources
- OpenAI API Docs: https://platform.openai.com/docs
- MLflow Docs: https://mlflow.org/docs/latest/index.html
- Databricks Docs: https://docs.databricks.com

### Internal Resources
- Slack Channel: #llm-evaluation
- Wiki: [your-wiki-link]
- Email Support: [support-email]

---

## Metrics for Workshop Success

Track these to improve future sessions:
- Number of participants
- Completion rate (% finishing all exercises)
- Support tickets opened
- Feedback survey scores
- Adoption rate (% using in real work)

---

## Tips for Facilitators

### Do's ✅
- Start with simple examples
- Encourage questions throughout
- Use real-world use cases
- Show both successes and failures
- Give plenty of hands-on time
- Circulate during exercises
- Celebrate participant wins

### Don'ts ❌
- Rush through exercises
- Skip error handling demos
- Assume prior knowledge
- Ignore struggling participants
- Go off on tangents
- Skip the wrap-up
- Forget to get feedback

---

## Advanced Workshop Extensions

If time permits or for advanced participants:

### Bonus Exercise 1: Parallel Evaluation
- Implement async evaluation for speed
- Compare performance metrics

### Bonus Exercise 2: Custom Thresholds
- Analyze score distributions
- Set data-driven thresholds
- Compare threshold strategies

### Bonus Exercise 3: A/B Testing
- Evaluate two AI systems
- Compare metrics side-by-side
- Statistical significance testing

### Bonus Exercise 4: Human Alignment
- Compare LLM judge to human ratings
- Calculate inter-rater reliability
- Tune prompts for better alignment

---

**Workshop Version**: 1.0  
**Last Updated**: 2025-10-10  
**Prepared By**: [Your Name]

Good luck with your workshop! 🚀
