# Databricks notebook source
# MAGIC %md
# MAGIC # LLM Judge - Evaluation Framework for AI Responses
# MAGIC
# MAGIC This notebook provides a streamlined framework for evaluating AI responses using LLM judges.
# MAGIC
# MAGIC ## Quick Start Guide:
# MAGIC 1. **Run Cell 1** - Install required packages
# MAGIC 2. **Run Cell 2** - Import libraries
# MAGIC 3. **Configure Cell 3** - Set file paths for your evaluation data
# MAGIC 4. **Configure Cell 4** - Select judge model and evaluation settings
# MAGIC 5. **Define Cell 5** - Create your custom evaluation metrics
# MAGIC 6. **Run Remaining Cells** - Execute evaluation and view results
# MAGIC
# MAGIC ## Features:
# MAGIC - ✅ Three metric types: Binary (Pass/Fail), 1-5 Scale, Percentage (0-100%)
# MAGIC - ✅ Support for ground truth data (CSV or DOCX format)
# MAGIC - ✅ Automatic matching and validation
# MAGIC - ✅ MLflow experiment tracking
# MAGIC - ✅ CSV export for analysis
# MAGIC - ✅ Visual summary reports

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 1: Package Installation
# MAGIC **Run this cell first - no changes needed**

# COMMAND ----------

# Install required packages
%pip install mlflow==2.10.0 --quiet
%pip install openai==1.12.0 --quiet
%pip install pandas==2.0.3 --quiet
%pip install plotly==5.18.0 --quiet
%pip install python-docx==1.1.0 --quiet
%pip install langchain-core==0.1.23 --quiet
%pip install langchain-openai==0.0.5 --quiet

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 2: Import Libraries
# MAGIC **Run this cell - no changes needed**

# COMMAND ----------

# Standard library imports
import time
import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Data processing
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Document processing
from docx import Document

# LLM and MLflow
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from openai import OpenAI
import mlflow

print("✅ All libraries imported successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 3: 📤 Data Configuration
# MAGIC **Configure your data file paths below**

# COMMAND ----------

# =============================================================================
# DATA FILE CONFIGURATION
# =============================================================================

# Get current user for default paths
current_user = dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()

# Create configuration widgets
dbutils.widgets.text(
    "evaluation_data_path", 
    "/dbfs/FileStore/llm_judge/evaluation_data.csv", 
    "📁 Evaluation Data Path (CSV with 'prompt' and 'response' columns)"
)

dbutils.widgets.text(
    "ground_truth_paths",
    "",
    "📚 Ground Truth File Paths (comma-separated, optional)"
)

dbutils.widgets.dropdown(
    "ground_truth_format",
    "csv",
    ["csv", "docx"],
    "📄 Ground Truth File Format"
)

# Get configuration values
EVAL_DATA_PATH = dbutils.widgets.get("evaluation_data_path")
GROUND_TRUTH_PATHS = dbutils.widgets.get("ground_truth_paths")
GROUND_TRUTH_FORMAT = dbutils.widgets.get("ground_truth_format")

print("📁 DATA CONFIGURATION")
print("="*70)
print(f"Evaluation Data: {EVAL_DATA_PATH}")
print(f"Ground Truth Files: {GROUND_TRUTH_PATHS if GROUND_TRUTH_PATHS else 'None'}")
print(f"Ground Truth Format: {GROUND_TRUTH_FORMAT}")
print("="*70)

# Load evaluation data
def load_evaluation_data(file_path: str) -> pd.DataFrame:
    """Load and validate evaluation data."""
    try:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            print("Creating sample data for demonstration...")
            
            # Create sample data
            return pd.DataFrame({
                'prompt': [
                    "What's the best mortgage option for first-time home buyers?",
                    "How can I improve my credit score quickly?",
                    "What are the current mortgage interest rates?",
                    "Should I refinance my mortgage now?",
                    "What documents do I need for a mortgage application?"
                ],
                'response': [
                    "FHA loans are popular for first-time buyers, requiring only 3.5% down payment with credit scores as low as 580.",
                    "Pay all bills on time, reduce credit utilization below 30%, and dispute any errors on your credit report.",
                    "Current rates vary by lender but typically range from 6-7% for 30-year fixed mortgages.",
                    "Consider refinancing if rates have dropped 1% or more since your original loan, and you plan to stay in your home for several years.",
                    "You'll need proof of income (W-2s, pay stubs), tax returns, bank statements, and photo identification."
                ]
            })
        
        # Load CSV file
        df = pd.read_csv(file_path)
        print(f"✅ Loaded {len(df)} rows from {file_path}")
        
        # Validate required columns
        required_cols = ['prompt', 'response']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}. Found columns: {list(df.columns)}")
        
        print(f"✅ Data validation passed")
        return df
        
    except Exception as e:
        print(f"❌ Error loading evaluation data: {e}")
        raise

# Load ground truth data
def load_ground_truth_data(file_paths: str, file_format: str) -> pd.DataFrame:
    """Load and process ground truth data from one or more files."""
    if not file_paths or not file_paths.strip():
        return pd.DataFrame()
    
    print("\n📚 Loading ground truth data...")
    all_ground_truth = []
    
    for file_path in [f.strip() for f in file_paths.split(",")]:
        if not os.path.exists(file_path):
            print(f"   ⚠️  File not found: {file_path}")
            continue
        
        try:
            if file_format == "csv":
                gt_df = pd.read_csv(file_path)
            else:  # docx
                doc = Document(file_path)
                data = []
                for table in doc.tables:
                    headers = [cell.text.strip() for cell in table.rows[0].cells]
                    for row in table.rows[1:]:
                        row_data = [cell.text.strip() for cell in row.cells]
                        data.append(dict(zip(headers, row_data)))
                gt_df = pd.DataFrame(data)
            
            all_ground_truth.append(gt_df)
            print(f"   ✅ Loaded {len(gt_df)} entries from {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"   ❌ Error loading {file_path}: {e}")
    
    if not all_ground_truth:
        return pd.DataFrame()
    
    # Combine all ground truth data
    combined_df = pd.concat(all_ground_truth, ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=['prompt'], keep='last')
    print(f"✅ Total ground truth entries: {len(combined_df)}")
    
    return combined_df

# Load data
eval_df = load_evaluation_data(EVAL_DATA_PATH)
ground_truth_df = load_ground_truth_data(GROUND_TRUTH_PATHS, GROUND_TRUTH_FORMAT)

# Merge ground truth if available
if not ground_truth_df.empty and 'prompt' in ground_truth_df.columns and 'ground_truth' in ground_truth_df.columns:
    eval_df = eval_df.merge(
        ground_truth_df[['prompt', 'ground_truth']], 
        on='prompt', 
        how='left'
    )
    gt_coverage = eval_df['ground_truth'].notna().sum()
    print(f"✅ Ground truth matched for {gt_coverage}/{len(eval_df)} samples ({gt_coverage/len(eval_df):.1%})")
else:
    eval_df['ground_truth'] = None

# Display preview
print("\n📊 Data Preview:")
display(eval_df.head(3))

# Store globally
EVALUATION_DATA = eval_df

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 4: 🤖 Model and Evaluation Settings
# MAGIC **Configure your LLM judge and evaluation parameters**

# COMMAND ----------

# =============================================================================
# MODEL AND EVALUATION CONFIGURATION
# =============================================================================

# Model selection widget
dbutils.widgets.dropdown(
    "judge_model",
    "gpt-4o-mini",
    ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
    "🤖 Judge Model"
)

# MLflow experiment configuration
dbutils.widgets.text(
    "experiment_name",
    f"/Users/{current_user}/llm_judge_evaluation",
    "🔬 MLflow Experiment Name"
)

# Evaluation settings
dbutils.widgets.dropdown(
    "batch_size",
    "5",
    ["1", "5", "10", "20"],
    "📦 Batch Size (samples to process at once)"
)

# Get settings
JUDGE_MODEL = dbutils.widgets.get("judge_model")
EXPERIMENT_NAME = dbutils.widgets.get("experiment_name")
BATCH_SIZE = int(dbutils.widgets.get("batch_size"))

print("🤖 EVALUATION CONFIGURATION")
print("="*70)
print(f"Judge Model: {JUDGE_MODEL}")
print(f"MLflow Experiment: {EXPERIMENT_NAME}")
print(f"Batch Size: {BATCH_SIZE}")
print("="*70)

# Initialize API connection
print("\n🔗 Initializing LLM connection...")

try:
    # Get API key from secrets
    OPENAI_API_KEY = dbutils.secrets.get("popin-secure-scope", "openai_key")
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    
    # Initialize OpenAI client with Zillow API endpoint
    client = OpenAI(
        base_url="https://api.zillowlabs.com/openai/v1",
        api_key=OPENAI_API_KEY
    )
    
    # Test connection
    test_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Reply with: Connection successful"}],
        max_tokens=10,
        temperature=0
    )
    
    print("✅ LLM connection successful!")
    print(f"   Test response: {test_response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ LLM connection failed: {e}")
    print("   Please check your API key configuration in Databricks secrets")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 5: 📊 Define Custom Evaluation Metrics
# MAGIC **Define your evaluation metrics below**
# MAGIC
# MAGIC ### Metric Types:
# MAGIC - **Binary**: Pass/Fail (0 or 1)
# MAGIC - **Scale 1-5**: Rating from 1 (worst) to 5 (best)
# MAGIC - **Percentage**: 0-100% (expressed as 0.0 to 1.0)
# MAGIC
# MAGIC ### Instructions:
# MAGIC 1. Uncomment the example metrics below or create your own
# MAGIC 2. Ensure your evaluation prompt returns JSON in the format: `{"metric_name_score": value, "explanation": "text"}`
# MAGIC 3. Use `{prompt}`, `{response}`, and `{ground_truth}` placeholders in your prompt

# COMMAND ----------

# =============================================================================
# CUSTOM METRICS DEFINITION
# =============================================================================

CUSTOM_METRICS = [
    # ========================================
    # BINARY METRIC EXAMPLE
    # ========================================
    {
        "name": "accuracy",
        "type": "binary",
        "description": "Evaluates if the response contains accurate information",
        "evaluation_prompt": """
Evaluate if the response contains accurate information.

User Query: {prompt}
AI Response: {response}
Ground Truth (if available): {ground_truth}

Evaluation Criteria:
- All facts must be correct and verifiable
- No misleading or incorrect information
- Numbers, statistics, and procedures must be accurate

Scoring:
- 1 (PASS): All information is accurate
- 0 (FAIL): Contains any inaccurate or misleading information

Return JSON format:
{{
    "accuracy_score": 1,
    "explanation": "Brief explanation of the scoring decision"
}}
"""
    },
    
    # ========================================
    # SCALE 1-5 METRIC EXAMPLE
    # ========================================
    {
        "name": "helpfulness",
        "type": "scale_1_5",
        "description": "Rates how helpful the response is on a 1-5 scale",
        "evaluation_prompt": """
Rate the helpfulness of this response on a scale from 1 to 5.

User Query: {prompt}
AI Response: {response}
Ground Truth (if available): {ground_truth}

Rating Scale:
5 = Extremely helpful - Comprehensive, actionable, addresses all aspects
4 = Very helpful - Good information with useful details
3 = Moderately helpful - Adequate but could be improved
2 = Slightly helpful - Limited value, missing key information
1 = Not helpful - Fails to address the question adequately

Return JSON format:
{{
    "helpfulness_score": 4,
    "explanation": "Brief explanation of the rating"
}}
"""
    },
    
    # ========================================
    # PERCENTAGE METRIC EXAMPLE
    # ========================================
    {
        "name": "completeness",
        "type": "percentage",
        "description": "Measures what percentage of the question was addressed",
        "evaluation_prompt": """
Evaluate what percentage (0-100%) of the user's question was addressed in the response.

User Query: {prompt}
AI Response: {response}
Ground Truth (if available): {ground_truth}

Assessment Process:
1. Identify all components of the user's question
2. Determine which components were addressed in the response
3. Calculate the percentage of coverage

Scoring Guide:
- 0.9-1.0 (90-100%): Fully addresses all aspects comprehensively
- 0.7-0.89 (70-89%): Covers most important parts
- 0.5-0.69 (50-69%): Addresses about half of the question
- 0.3-0.49 (30-49%): Some aspects addressed
- 0.0-0.29 (0-29%): Minimal coverage

Return JSON format (use decimal value, e.g., 0.85 for 85%):
{{
    "completeness_score": 0.85,
    "explanation": "Brief explanation of what was covered and what was missed"
}}
"""
    },
]

# =============================================================================
# METRIC VALIDATION
# =============================================================================

def validate_metrics(metrics: List[Dict]) -> tuple[bool, List[str]]:
    """Validate metric definitions."""
    errors = []
    
    for i, metric in enumerate(metrics, 1):
        # Check required fields
        required_fields = ['name', 'type', 'description', 'evaluation_prompt']
        for field in required_fields:
            if field not in metric:
                errors.append(f"Metric {i}: Missing required field '{field}'")
        
        # Validate metric type
        if metric.get('type') not in ['binary', 'scale_1_5', 'percentage']:
            errors.append(f"Metric {i} ({metric.get('name')}): Invalid type '{metric.get('type')}'")
        
        # Check for required placeholders
        prompt = metric.get('evaluation_prompt', '')
        if '{prompt}' not in prompt:
            errors.append(f"Metric {i} ({metric.get('name')}): Missing {{prompt}} placeholder")
        if '{response}' not in prompt:
            errors.append(f"Metric {i} ({metric.get('name')}): Missing {{response}} placeholder")
    
    return len(errors) == 0, errors

# Validate and display metrics
is_valid, validation_errors = validate_metrics(CUSTOM_METRICS)

print("📊 CUSTOM METRICS SUMMARY")
print("="*70)

if not is_valid:
    print("\n❌ VALIDATION ERRORS:")
    for error in validation_errors:
        print(f"   {error}")
    raise ValueError("Metric validation failed. Please fix the errors above.")

# Display metric summary
metric_counts = {"binary": 0, "scale_1_5": 0, "percentage": 0}

for i, metric in enumerate(CUSTOM_METRICS, 1):
    metric_counts[metric['type']] += 1
    print(f"\n{i}. {metric['name'].upper()}")
    print(f"   Type: {metric['type']}")
    print(f"   Description: {metric['description']}")

print(f"\n📈 TOTAL METRICS: {len(CUSTOM_METRICS)}")
print(f"   Binary (Pass/Fail): {metric_counts['binary']}")
print(f"   Scale (1-5): {metric_counts['scale_1_5']}")
print(f"   Percentage (0-100%): {metric_counts['percentage']}")

# Set default thresholds
METRIC_THRESHOLDS = {}
for metric in CUSTOM_METRICS:
    if metric['type'] == 'binary':
        METRIC_THRESHOLDS[metric['name']] = 1.0  # Must be 1 to pass
    elif metric['type'] == 'scale_1_5':
        METRIC_THRESHOLDS[metric['name']] = 3.0  # 3+ to pass
    elif metric['type'] == 'percentage':
        METRIC_THRESHOLDS[metric['name']] = 0.7  # 70%+ to pass

print("\n🎯 Pass Thresholds (for determining pass/fail status):")
for name, threshold in METRIC_THRESHOLDS.items():
    print(f"   {name}: {threshold}")

print("\n✅ Metrics validated and ready for evaluation")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 6: System Classes and Core Logic
# MAGIC **Run this cell - no changes needed**

# COMMAND ----------

# =============================================================================
# CORE SYSTEM CLASSES
# =============================================================================

class MetricType(Enum):
    """Enumeration of supported metric types."""
    BINARY = "binary"
    SCALE_1_5 = "scale_1_5"
    PERCENTAGE = "percentage"

@dataclass
class MetricConfig:
    """Configuration for an evaluation metric."""
    name: str
    description: str
    metric_type: MetricType
    prompt_template: str
    threshold: float

class LLMJudgeEvaluator:
    """Main evaluator class for running LLM-based evaluations."""
    
    def __init__(self, judge_model: str, metrics: List[MetricConfig], client: OpenAI):
        """
        Initialize the evaluator.
        
        Args:
            judge_model: Name of the model to use as judge
            metrics: List of metric configurations
            client: OpenAI client instance
        """
        self.judge_model = judge_model
        self.metrics = metrics
        self.client = client
    
    def _call_llm_judge(self, prompt: str) -> Dict[str, Any]:
        """Call the LLM judge with a prompt."""
        try:
            response = self.client.chat.completions.create(
                model=self.judge_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"LLM call failed: {e}")
    
    def evaluate_single(
        self, 
        prompt: str, 
        response: str, 
        ground_truth: Optional[str], 
        metric: MetricConfig
    ) -> Dict[str, Any]:
        """
        Evaluate a single sample with one metric.
        
        Args:
            prompt: The user's input prompt
            response: The AI's response to evaluate
            ground_truth: Optional ground truth reference
            metric: Metric configuration to use
            
        Returns:
            Dictionary containing score, explanation, and pass/fail status
        """
        # Format the evaluation prompt
        eval_prompt = metric.prompt_template.format(
            prompt=prompt,
            response=response,
            ground_truth=ground_truth if ground_truth else "Not provided"
        )
        
        try:
            # Get evaluation from LLM
            result_json = self._call_llm_judge(eval_prompt)
            
            # Extract score and explanation
            score_key = f"{metric.name}_score"
            score = result_json.get(score_key)
            explanation = result_json.get("explanation", "No explanation provided")
            
            if score is None:
                raise ValueError(f"Score key '{score_key}' not found in LLM response")
            
            # Convert to float
            score = float(score)
            
            # Validate score range based on metric type
            if metric.metric_type == MetricType.BINARY and score not in [0, 1]:
                raise ValueError(f"Binary metric must return 0 or 1, got {score}")
            elif metric.metric_type == MetricType.SCALE_1_5 and not (1 <= score <= 5):
                raise ValueError(f"Scale metric must return 1-5, got {score}")
            elif metric.metric_type == MetricType.PERCENTAGE and not (0 <= score <= 1):
                raise ValueError(f"Percentage metric must return 0-1, got {score}")
            
            # Determine pass/fail status
            status = "✅ PASS" if score >= metric.threshold else "❌ FAIL"
            
            return {
                "score": score,
                "explanation": explanation,
                "status": status
            }
            
        except Exception as e:
            print(f"⚠️  Error evaluating {metric.name}: {e}")
            return {
                "score": 0,
                "explanation": f"Evaluation error: {str(e)}",
                "status": "❌ ERROR"
            }
    
    def evaluate_dataset(self, df: pd.DataFrame, batch_size: int = 5) -> pd.DataFrame:
        """
        Evaluate entire dataset with all metrics.
        
        Args:
            df: DataFrame with 'prompt', 'response', and optionally 'ground_truth'
            batch_size: Number of samples to process before showing progress
            
        Returns:
            DataFrame with evaluation results added
        """
        results_df = df.copy()
        
        print(f"\n🚀 STARTING EVALUATION")
        print("="*70)
        print(f"Samples: {len(df)}")
        print(f"Metrics: {len(self.metrics)}")
        print(f"Model: {self.judge_model}")
        print("="*70)
        
        for metric in self.metrics:
            print(f"\n📊 Evaluating: {metric.name} ({metric.metric_type.value})")
            
            scores = []
            explanations = []
            statuses = []
            
            for idx, row in df.iterrows():
                # Show progress
                if idx > 0 and idx % batch_size == 0:
                    print(f"   Progress: {idx}/{len(df)} samples completed")
                
                # Evaluate
                result = self.evaluate_single(
                    prompt=row['prompt'],
                    response=row['response'],
                    ground_truth=row.get('ground_truth'),
                    metric=metric
                )
                
                scores.append(result['score'])
                explanations.append(result['explanation'])
                statuses.append(result['status'])
            
            # Add results to dataframe
            results_df[f"{metric.name}_score"] = scores
            results_df[f"{metric.name}_explanation"] = explanations
            results_df[f"{metric.name}_status"] = statuses
            
            # Calculate summary
            mean_score = sum(scores) / len(scores) if scores else 0
            pass_count = sum(1 for s in scores if s >= metric.threshold)
            pass_rate = pass_count / len(scores) if scores else 0
            
            print(f"   ✅ Complete!")
            print(f"      Mean Score: {mean_score:.3f}")
            print(f"      Pass Rate: {pass_rate:.1%} ({pass_count}/{len(scores)})")
        
        return results_df

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def process_custom_metrics(custom_metrics: List[Dict]) -> List[MetricConfig]:
    """Convert custom metric dictionaries to MetricConfig objects."""
    configs = []
    
    for metric in custom_metrics:
        # Map metric type
        type_map = {
            'binary': MetricType.BINARY,
            'scale_1_5': MetricType.SCALE_1_5,
            'percentage': MetricType.PERCENTAGE
        }
        
        metric_type = type_map.get(metric['type'])
        if not metric_type:
            print(f"⚠️  Skipping metric '{metric['name']}': invalid type '{metric['type']}'")
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

print("✅ System classes and functions loaded")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 7: Run Evaluation
# MAGIC **Execute the evaluation process**

# COMMAND ----------

# Process metrics and create evaluator
metric_configs = process_custom_metrics(CUSTOM_METRICS)

if not metric_configs:
    raise ValueError("❌ No valid metrics to evaluate! Please define metrics in Cell 5")

# Create evaluator
evaluator = LLMJudgeEvaluator(
    judge_model=JUDGE_MODEL,
    metrics=metric_configs,
    client=client
)

# Run evaluation
print("="*70)
print("🚀 RUNNING EVALUATION")
print("="*70)

start_time = time.time()
results_df = evaluator.evaluate_dataset(EVALUATION_DATA, batch_size=BATCH_SIZE)
eval_time = time.time() - start_time

print("\n" + "="*70)
print(f"✅ EVALUATION COMPLETE")
print("="*70)
print(f"Total Time: {eval_time:.1f} seconds")
print(f"Average Time per Sample: {eval_time/len(EVALUATION_DATA):.2f} seconds")
print(f"Samples Evaluated: {len(results_df)}")

# Display sample results
print("\n📊 Sample Results:")
display_cols = ['prompt', 'response']
for m in metric_configs:
    display_cols.extend([f"{m.name}_score", f"{m.name}_status"])
display_cols = [col for col in display_cols if col in results_df.columns]

display(results_df[display_cols].head())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 8: Generate Summary Report
# MAGIC **View detailed evaluation statistics and visualizations**

# COMMAND ----------

if 'results_df' not in globals() or results_df.empty:
    raise ValueError("❌ No results to display. Please run Cell 7 first.")

print("📊 EVALUATION SUMMARY REPORT")
print("="*70)

# Overall statistics
print(f"\n📈 OVERALL STATISTICS:")
print(f"   Total Samples Evaluated: {len(results_df)}")
print(f"   Number of Metrics: {len(metric_configs)}")
print(f"   Evaluation Time: {eval_time:.1f} seconds")

# Per-metric detailed analysis
summary_data = []

for metric in metric_configs:
    scores = results_df[f"{metric.name}_score"]
    
    # Calculate statistics
    mean_score = scores.mean()
    median_score = scores.median()
    std_score = scores.std()
    min_score = scores.min()
    max_score = scores.max()
    pass_count = (scores >= metric.threshold).sum()
    pass_rate = pass_count / len(scores)
    
    summary_data.append({
        'Metric': metric.name,
        'Type': metric.metric_type.value,
        'Mean': f"{mean_score:.3f}",
        'Median': f"{median_score:.3f}",
        'Std Dev': f"{std_score:.3f}",
        'Min': f"{min_score:.3f}",
        'Max': f"{max_score:.3f}",
        'Threshold': f"{metric.threshold}",
        'Pass Rate': f"{pass_rate:.1%}",
        'Passed': f"{pass_count}/{len(scores)}"
    })
    
    print(f"\n{'='*70}")
    print(f"📊 {metric.name.upper()}")
    print(f"{'='*70}")
    print(f"   Metric Type: {metric.metric_type.value}")
    print(f"   Mean Score: {mean_score:.3f}")
    print(f"   Median Score: {median_score:.3f}")
    print(f"   Std Deviation: {std_score:.3f}")
    print(f"   Range: [{min_score:.3f}, {max_score:.3f}]")
    print(f"   Pass Threshold: {metric.threshold}")
    print(f"   Pass Rate: {pass_rate:.1%} ({pass_count}/{len(scores)} samples)")

# Display summary table
summary_df = pd.DataFrame(summary_data)
print(f"\n{'='*70}")
print("📋 SUMMARY TABLE")
print(f"{'='*70}")
display(summary_df)

# Create visualizations
if len(metric_configs) > 0:
    # Score distribution histograms
    fig = make_subplots(
        rows=1, 
        cols=len(metric_configs),
        subplot_titles=[m.name.replace('_', ' ').title() for m in metric_configs]
    )
    
    for i, metric in enumerate(metric_configs, 1):
        scores = results_df[f"{metric.name}_score"]
        
        fig.add_trace(
            go.Histogram(
                x=scores, 
                name=metric.name,
                nbinsx=20,
                marker_color='rgb(55, 83, 109)'
            ),
            row=1, col=i
        )
        
        # Add threshold line
        fig.add_vline(
            x=metric.threshold,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Threshold: {metric.threshold}",
            row=1, col=i
        )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        title_text="Score Distributions by Metric",
        title_font_size=16
    )
    fig.update_xaxes(title_text="Score")
    fig.update_yaxes(title_text="Count")
    
    fig.show()
    
    # Pass rate comparison
    fig2 = go.Figure(data=[
        go.Bar(
            x=[m.name for m in metric_configs],
            y=[(results_df[f"{m.name}_score"] >= m.threshold).mean() * 100 
               for m in metric_configs],
            text=[f"{(results_df[f'{m.name}_score'] >= m.threshold).mean():.1%}" 
                  for m in metric_configs],
            textposition='auto',
            marker_color='rgb(26, 118, 255)'
        )
    ])
    
    fig2.update_layout(
        title="Pass Rate by Metric",
        xaxis_title="Metric",
        yaxis_title="Pass Rate (%)",
        height=400,
        yaxis_range=[0, 100]
    )
    
    fig2.show()

print("\n✅ Summary report generated successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 9: Export Results
# MAGIC **Save evaluation results to CSV files**

# COMMAND ----------

if 'results_df' not in globals() or results_df.empty:
    raise ValueError("❌ No results to export. Please run Cell 7 first.")

# Generate timestamp for filenames
timestamp = time.strftime('%Y%m%d_%H%M%S')

# Define output paths
output_dir = "/dbfs/FileStore/llm_judge/results"
os.makedirs(output_dir, exist_ok=True)

results_filename = f"llm_judge_results_{timestamp}.csv"
summary_filename = f"llm_judge_summary_{timestamp}.csv"

results_path = os.path.join(output_dir, results_filename)
summary_path = os.path.join(output_dir, summary_filename)

print("💾 EXPORTING RESULTS")
print("="*70)

try:
    # Export detailed results
    results_df.to_csv(results_path, index=False)
    print(f"✅ Detailed results exported:")
    print(f"   Path: {results_path}")
    print(f"   Size: {len(results_df)} rows × {len(results_df.columns)} columns")
    
    # Export summary
    summary_df.to_csv(summary_path, index=False)
    print(f"\n✅ Summary exported:")
    print(f"   Path: {summary_path}")
    print(f"   Size: {len(summary_df)} rows × {len(summary_df.columns)} columns")
    
    print("\n📥 FILES AVAILABLE FOR DOWNLOAD:")
    print(f"   Detailed Results: /FileStore/llm_judge/results/{results_filename}")
    print(f"   Summary: /FileStore/llm_judge/results/{summary_filename}")
    
    print("\n💡 USE CASES:")
    print("   • Share with stakeholders")
    print("   • Further analysis in Excel or Python")
    print("   • Historical tracking and comparison")
    print("   • Integration with other tools")
    
except Exception as e:
    print(f"❌ Error exporting results: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 10: MLflow Experiment Tracking
# MAGIC **Log results to MLflow for tracking and comparison**

# COMMAND ----------

if 'results_df' not in globals() or results_df.empty:
    raise ValueError("❌ No results to log. Please run Cell 7 first.")

print("🔬 LOGGING TO MLFLOW")
print("="*70)

try:
    # Set or create experiment
    mlflow.set_experiment(EXPERIMENT_NAME)
    
    # Start MLflow run
    with mlflow.start_run(run_name=f"llm_judge_{timestamp}") as run:
        # Log parameters
        mlflow.log_param("judge_model", JUDGE_MODEL)
        mlflow.log_param("num_samples", len(results_df))
        mlflow.log_param("num_metrics", len(metric_configs))
        mlflow.log_param("batch_size", BATCH_SIZE)
        mlflow.log_param("evaluation_time_seconds", eval_time)
        mlflow.log_param("has_ground_truth", 'ground_truth' in results_df.columns and results_df['ground_truth'].notna().any())
        
        # Log metrics for each evaluation metric
        for metric in metric_configs:
            scores = results_df[f"{metric.name}_score"]
            
            # Log aggregate statistics
            mlflow.log_metric(f"{metric.name}_mean", scores.mean())
            mlflow.log_metric(f"{metric.name}_median", scores.median())
            mlflow.log_metric(f"{metric.name}_std", scores.std())
            mlflow.log_metric(f"{metric.name}_min", scores.min())
            mlflow.log_metric(f"{metric.name}_max", scores.max())
            
            # Log pass rate
            pass_rate = (scores >= metric.threshold).mean()
            mlflow.log_metric(f"{metric.name}_pass_rate", pass_rate)
        
        # Log artifacts (CSV files)
        mlflow.log_artifact(results_path, "results")
        mlflow.log_artifact(summary_path, "results")
        
        # Log metric configurations as JSON
        metrics_config_path = os.path.join(output_dir, f"metrics_config_{timestamp}.json")
        with open(metrics_config_path, 'w') as f:
            json.dump(CUSTOM_METRICS, f, indent=2)
        mlflow.log_artifact(metrics_config_path, "config")
        
        run_id = run.info.run_id
        
        print(f"✅ Results logged to MLflow")
        print(f"   Experiment: {EXPERIMENT_NAME}")
        print(f"   Run ID: {run_id}")
        print(f"   Run Name: llm_judge_{timestamp}")
        
        print(f"\n📊 LOGGED ITEMS:")
        print(f"   Parameters: {len(metric_configs) + 5}")
        print(f"   Metrics: {len(metric_configs) * 6}")
        print(f"   Artifacts: 3 (results CSV, summary CSV, config JSON)")
        
        print(f"\n💡 VIEW IN MLFLOW UI:")
        print(f"   Navigate to: Experiments → {EXPERIMENT_NAME}")
        print(f"   Use MLflow UI to compare runs and track progress over time")
        
except Exception as e:
    print(f"⚠️  MLflow logging failed: {e}")
    print("   Results are still saved in CSV files")
    print(f"   Please check your MLflow experiment configuration")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🎉 Evaluation Complete!
# MAGIC
# MAGIC ### Summary:
# MAGIC Your LLM Judge evaluation has been completed successfully!
# MAGIC
# MAGIC ### What Was Done:
# MAGIC 1. ✅ Loaded and validated evaluation data
# MAGIC 2. ✅ Executed LLM-based evaluations across all metrics
# MAGIC 3. ✅ Generated comprehensive summary statistics
# MAGIC 4. ✅ Created visualizations for analysis
# MAGIC 5. ✅ Exported results to CSV files
# MAGIC 6. ✅ Logged experiment to MLflow
# MAGIC
# MAGIC ### Next Steps:
# MAGIC - **Review Results**: Check the summary report in Cell 8
# MAGIC - **Download Files**: Access CSV exports from Cell 9
# MAGIC - **Compare Runs**: Use MLflow UI to track experiments over time
# MAGIC - **Iterate**: Modify metrics in Cell 5 and re-run for different evaluations
# MAGIC - **Share**: Distribute results with stakeholders
# MAGIC
# MAGIC ### Tips for Workshop:
# MAGIC - **Binary Metrics**: Best for clear pass/fail criteria (e.g., accuracy, compliance)
# MAGIC - **Scale Metrics**: Ideal for quality assessments (e.g., helpfulness, clarity)
# MAGIC - **Percentage Metrics**: Perfect for completeness or coverage evaluations
# MAGIC - **Ground Truth**: When available, significantly improves evaluation quality
# MAGIC - **Batch Processing**: Adjust batch size in Cell 4 for optimal performance
# MAGIC
# MAGIC ### Questions?
# MAGIC Refer to the documentation or reach out to your workshop facilitator.
