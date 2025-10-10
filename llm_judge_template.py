# Databricks notebook source
# MAGIC %md
# MAGIC # LLM Judge Evaluation System
# MAGIC
# MAGIC A streamlined framework for evaluating AI responses using LLM judges in Databricks.
# MAGIC
# MAGIC ## Quick Start:
# MAGIC 1. **Cell 1** - Install packages
# MAGIC 2. **Cell 2** - Upload your evaluation data
# MAGIC 3. **Cell 3** - Configure judge model and settings
# MAGIC 4. **Cell 4** - Define your custom metrics
# MAGIC 5. **Cell 5** - Run evaluation
# MAGIC 6. **Cell 6** - View results and export

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 1: Installation and Setup

# COMMAND ----------

# Install essential packages
%pip install mlflow openai pandas plotly python-docx langchain-core langchain-openai --quiet

%restart_python

print("✅ Packages installed successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 2: Import Libraries and Setup

# COMMAND ----------

import os
import json
import time
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from docx import Document
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from openai import OpenAI
import mlflow

print("✅ Libraries imported successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 3: Data Upload and Configuration

# COMMAND ----------

# File upload widgets
dbutils.widgets.text("evaluation_data_path", "/workspace/evaluation_data.csv", "📁 Evaluation Data (CSV)")
dbutils.widgets.text("ground_truth_path", "", "📚 Ground Truth File (optional)")
dbutils.widgets.dropdown("ground_truth_format", "csv", ["csv", "docx"], "📄 Ground Truth Format")

# Model configuration
dbutils.widgets.dropdown("judge_model", "gpt-4o-mini", ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"], "🤖 Judge Model")
dbutils.widgets.text("experiment_name", f"/Users/{dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()}/llm_judge", "🔬 MLflow Experiment")

# Get configuration
EVAL_DATA_PATH = dbutils.widgets.get("evaluation_data_path")
GROUND_TRUTH_PATH = dbutils.widgets.get("ground_truth_path")
GROUND_TRUTH_FORMAT = dbutils.widgets.get("ground_truth_format")
JUDGE_MODEL = dbutils.widgets.get("judge_model")
EXPERIMENT_NAME = dbutils.widgets.get("experiment_name")

print("📁 CONFIGURATION")
print("="*50)
print(f"Evaluation Data: {EVAL_DATA_PATH}")
print(f"Ground Truth: {GROUND_TRUTH_PATH or 'None'}")
print(f"Judge Model: {JUDGE_MODEL}")
print(f"Experiment: {EXPERIMENT_NAME}")

# Load evaluation data
try:
    if os.path.exists(EVAL_DATA_PATH):
        eval_df = pd.read_csv(EVAL_DATA_PATH)
        print(f"\n✅ Loaded {len(eval_df)} evaluation samples")
        
        # Validate required columns
        required_cols = ['prompt', 'response']
        missing_cols = [col for col in required_cols if col not in eval_df.columns]
        if missing_cols:
            print(f"❌ Missing columns: {missing_cols}")
            print(f"Available columns: {list(eval_df.columns)}")
        else:
            print("✅ Data validation passed")
            display(eval_df.head(2))
    else:
        print(f"❌ File not found: {EVAL_DATA_PATH}")
        # Create sample data
        eval_df = pd.DataFrame({
            'prompt': [
                "What's the best mortgage for first-time buyers?",
                "How do I improve my credit score?",
                "What are current interest rates?"
            ],
            'response': [
                "FHA loans are popular for first-time buyers with 3.5% down payment.",
                "Pay bills on time, reduce credit utilization, and check for errors.",
                "Current rates vary by lender, typically 6-7% for 30-year fixed."
            ]
        })
        print("✅ Created sample data for demonstration")
        display(eval_df)

except Exception as e:
    print(f"❌ Error loading data: {e}")
    eval_df = pd.DataFrame()

# Load ground truth if provided
if GROUND_TRUTH_PATH and os.path.exists(GROUND_TRUTH_PATH):
    try:
        if GROUND_TRUTH_FORMAT == "csv":
            gt_df = pd.read_csv(GROUND_TRUTH_PATH)
        else:  # docx
            doc = Document(GROUND_TRUTH_PATH)
            data = []
            for table in doc.tables:
                headers = [cell.text.strip() for cell in table.rows[0].cells]
                for row in table.rows[1:]:
                    row_data = [cell.text.strip() for cell in row.cells]
                    data.append(dict(zip(headers, row_data)))
            gt_df = pd.DataFrame(data)
        
        # Merge with evaluation data
        if 'prompt' in gt_df.columns and 'ground_truth' in gt_df.columns:
            eval_df = eval_df.merge(gt_df[['prompt', 'ground_truth']], on='prompt', how='left')
            coverage = eval_df['ground_truth'].notna().sum()
            print(f"✅ Ground truth loaded: {coverage}/{len(eval_df)} samples matched")
        else:
            print("⚠️ Ground truth file missing 'prompt' or 'ground_truth' columns")
    except Exception as e:
        print(f"⚠️ Error loading ground truth: {e}")

# Store globally
EVALUATION_DATA = eval_df

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 4: Define Custom Metrics

# COMMAND ----------

# Define your evaluation metrics here
CUSTOM_METRICS = [
    {
        "name": "accuracy",
        "type": "binary",
        "description": "Checks if the response contains accurate information",
        "evaluation_prompt": """
Evaluate if the response contains accurate information.

User Query: {prompt}
AI Response: {response}
Ground Truth (if available): {ground_truth}

Criteria:
- All facts must be correct
- No misleading information
- Numbers and statistics must be accurate

Return JSON:
{{
    "accuracy_score": 1,
    "explanation": "All information is accurate and verified."
}}
"""
    },
    
    {
        "name": "helpfulness",
        "type": "scale_1_5",
        "description": "Rates how helpful the response is (1-5 scale)",
        "evaluation_prompt": """
Rate the helpfulness of this response from 1 to 5.

User Query: {prompt}
AI Response: {response}
Ground Truth (if available): {ground_truth}

Scale:
5 = Extremely helpful - Comprehensive answer with actionable steps
4 = Very helpful - Good answer with useful information
3 = Moderately helpful - Adequate but could be better
2 = Slightly helpful - Limited value, missing key information
1 = Not helpful - Fails to address the question

Return JSON:
{{
    "helpfulness_score": 4,
    "explanation": "Very helpful response that answers the main question..."
}}
"""
    },
    
    {
        "name": "completeness",
        "type": "percentage",
        "description": "Measures what percentage of the question was addressed",
        "evaluation_prompt": """
Evaluate what percentage (0-100%) of the user's question was addressed.

User Query: {prompt}
AI Response: {response}
Ground Truth (if available): {ground_truth}

Assessment:
- Identify all components of the user's question
- Check which components were addressed
- Calculate percentage of coverage

Return JSON (use decimal, e.g., 0.85 for 85%):
{{
    "completeness_score": 0.85,
    "explanation": "The response addresses 85% of the question..."
}}
"""
    }
]

# Set thresholds
METRIC_THRESHOLDS = {
    "accuracy": 1.0,      # Binary: Pass = 1
    "helpfulness": 3.0,   # 1-5 Scale: Pass = 3+
    "completeness": 0.7   # Percentage: Pass = 70%+
}

print("📊 METRICS CONFIGURED")
print("="*50)
for i, metric in enumerate(CUSTOM_METRICS, 1):
    print(f"{i}. {metric['name'].upper()}")
    print(f"   Type: {metric['type']}")
    print(f"   Threshold: {METRIC_THRESHOLDS[metric['name']]}")
    print(f"   Description: {metric['description']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 5: LLM Judge System

# COMMAND ----------

class MetricType(Enum):
    BINARY = "binary"
    SCALE_1_5 = "scale_1_5"
    PERCENTAGE = "percentage"

@dataclass
class MetricConfig:
    name: str
    description: str
    metric_type: MetricType
    prompt_template: str
    threshold: float

class LLMJudgeEvaluator:
    def __init__(self, judge_model: str, metrics: List[MetricConfig]):
        self.judge_model = judge_model
        self.metrics = metrics
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client with Zillow API."""
        try:
            OPENAI_KEY = dbutils.secrets.get("popin-secure-scope", "openai_key")
            self.client = OpenAI(
                base_url="https://api.zillowlabs.com/openai/v1",
                api_key=OPENAI_KEY
            )
            
            # Test connection
            test_response = self.client.chat.completions.create(
                model=self.judge_model,
                messages=[{"role": "user", "content": "Say 'OK'"}],
                max_tokens=10
            )
            print(f"✅ Connected to {self.judge_model}")
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise
    
    def evaluate_single(self, prompt: str, response: str, ground_truth: str, metric: MetricConfig) -> dict:
        """Evaluate a single sample with one metric."""
        eval_prompt = metric.prompt_template.format(
            prompt=prompt,
            response=response,
            ground_truth=ground_truth if ground_truth else "Not provided"
        )
        
        try:
            result = self.client.chat.completions.create(
                model=self.judge_model,
                messages=[{"role": "user", "content": eval_prompt}],
                max_tokens=500,
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            result_json = json.loads(result.choices[0].message.content)
            score_key = f"{metric.name}_score"
            score = result_json.get(score_key, 0)
            explanation = result_json.get("explanation", "No explanation provided")
            
            return {
                "score": score,
                "explanation": explanation,
                "status": "✅" if score >= metric.threshold else "❌"
            }
            
        except Exception as e:
            return {
                "score": 0,
                "explanation": f"Evaluation error: {str(e)}",
                "status": "❌"
            }
    
    def evaluate_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Evaluate entire dataset."""
        results_df = df.copy()
        
        print(f"\n🚀 Evaluating {len(df)} samples with {len(self.metrics)} metrics...")
        
        for metric in self.metrics:
            print(f"\n📊 Evaluating: {metric.name}")
            
            scores = []
            explanations = []
            statuses = []
            
            for idx, row in df.iterrows():
                if idx > 0 and idx % 10 == 0:
                    print(f"   Progress: {idx}/{len(df)}")
                
                result = self.evaluate_single(
                    prompt=row['prompt'],
                    response=row['response'],
                    ground_truth=row.get('ground_truth', ''),
                    metric=metric
                )
                
                scores.append(result['score'])
                explanations.append(result['explanation'])
                statuses.append(result['status'])
            
            # Add results
            results_df[f"{metric.name}_score"] = scores
            results_df[f"{metric.name}_explanation"] = explanations
            results_df[f"{metric.name}_status"] = statuses
            
            # Calculate summary
            mean_score = sum(scores) / len(scores)
            pass_rate = sum(1 for s in scores if s >= metric.threshold) / len(scores)
            print(f"   ✅ Complete - Mean: {mean_score:.3f}, Pass Rate: {pass_rate:.1%}")
        
        return results_df

def process_metrics(custom_metrics: list) -> List[MetricConfig]:
    """Convert custom metrics to MetricConfig objects."""
    configs = []
    
    for metric in custom_metrics:
        if metric['type'] == 'binary':
            metric_type = MetricType.BINARY
        elif metric['type'] == 'scale_1_5':
            metric_type = MetricType.SCALE_1_5
        elif metric['type'] == 'percentage':
            metric_type = MetricType.PERCENTAGE
        else:
            continue
        
        config = MetricConfig(
            name=metric['name'],
            description=metric['description'],
            metric_type=metric_type,
            prompt_template=metric['evaluation_prompt'],
            threshold=METRIC_THRESHOLDS.get(metric['name'], 1.0)
        )
        configs.append(config)
    
    return configs

print("✅ LLM Judge system loaded")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 6: Run Evaluation

# COMMAND ----------

# Process metrics and create evaluator
metric_configs = process_metrics(CUSTOM_METRICS)

if not metric_configs:
    print("❌ No valid metrics defined!")
else:
    # Create evaluator
    evaluator = LLMJudgeEvaluator(
        judge_model=JUDGE_MODEL,
        metrics=metric_configs
    )
    
    # Run evaluation
    print("="*60)
    print("🚀 STARTING EVALUATION")
    print("="*60)
    
    start_time = time.time()
    results_df = evaluator.evaluate_dataset(EVALUATION_DATA)
    eval_time = time.time() - start_time
    
    print(f"\n✅ EVALUATION COMPLETE in {eval_time:.1f} seconds")
    
    # Display sample results
    print("\n📊 Sample Results:")
    display_cols = ['prompt', 'response'] + [f"{m.name}_score" for m in metric_configs]
    display_cols = [col for col in display_cols if col in results_df.columns]
    display(results_df[display_cols].head())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 7: Results Summary and Export

# COMMAND ----------

if 'results_df' in globals() and not results_df.empty:
    print("📊 EVALUATION SUMMARY")
    print("="*60)
    
    # Overall statistics
    print(f"Total Samples: {len(results_df)}")
    print(f"Metrics Evaluated: {len(metric_configs)}")
    
    # Per-metric summary
    summary_data = []
    
    for metric in metric_configs:
        scores = results_df[f"{metric.name}_score"]
        
        mean_score = scores.mean()
        pass_count = (scores >= metric.threshold).sum()
        pass_rate = pass_count / len(scores)
        
        summary_data.append({
            'Metric': metric.name,
            'Type': metric.metric_type.value,
            'Mean Score': f"{mean_score:.3f}",
            'Pass Rate': f"{pass_rate:.1%}",
            'Passed': f"{pass_count}/{len(scores)}"
        })
        
        print(f"\n📊 {metric.name.upper()}:")
        print(f"   Mean Score: {mean_score:.3f}")
        print(f"   Pass Rate: {pass_rate:.1%} ({pass_count}/{len(scores)})")
        print(f"   Threshold: {metric.threshold}")
    
    # Display summary table
    summary_df = pd.DataFrame(summary_data)
    print("\n📋 Summary Table:")
    display(summary_df)
    
    # Create visualization
    if len(metric_configs) > 0:
        fig = make_subplots(
            rows=1, 
            cols=len(metric_configs),
            subplot_titles=[m.name for m in metric_configs]
        )
        
        for i, metric in enumerate(metric_configs, 1):
            scores = results_df[f"{metric.name}_score"]
            fig.add_trace(
                go.Histogram(x=scores, name=metric.name, nbinsx=20),
                row=1, col=i
            )
        
        fig.update_layout(height=400, showlegend=False, title_text="Score Distributions")
        fig.show()
    
    # Export results
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    output_filename = f"llm_judge_results_{timestamp}.csv"
    output_path = f"/workspace/{output_filename}"
    
    try:
        results_df.to_csv(output_path, index=False)
        print(f"\n✅ Results exported to: {output_path}")
        
        # MLflow logging
        try:
            mlflow.set_experiment(EXPERIMENT_NAME)
            with mlflow.start_run(run_name=f"llm_judge_{timestamp}"):
                mlflow.log_param("judge_model", JUDGE_MODEL)
                mlflow.log_param("num_samples", len(results_df))
                
                for metric in metric_configs:
                    scores = results_df[f"{metric.name}_score"]
                    mlflow.log_metric(f"{metric.name}_mean", scores.mean())
                    mlflow.log_metric(f"{metric.name}_pass_rate", (scores >= metric.threshold).mean())
                
                mlflow.log_artifact(output_path)
                print(f"✅ Results logged to MLflow: {EXPERIMENT_NAME}")
                
        except Exception as e:
            print(f"⚠️ MLflow logging failed: {e}")
            
    except Exception as e:
        print(f"❌ Export failed: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🎉 Evaluation Complete!
# MAGIC
# MAGIC ### Next Steps:
# MAGIC 1. **Review the summary** above
# MAGIC 2. **Download the CSV file** for further analysis
# MAGIC 3. **Check MLflow** for experiment tracking
# MAGIC 4. **Modify metrics** in Cell 4 for different evaluations
# MAGIC
# MAGIC ### Tips:
# MAGIC - **Binary metrics**: Clear pass/fail criteria
# MAGIC - **1-5 Scale**: Quality assessments
# MAGIC - **Percentage**: Completeness or coverage metrics
# MAGIC - **Ground truth**: Improves evaluation quality when available