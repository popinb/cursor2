# Databricks notebook source
# MAGIC %md
# MAGIC # 🤖 LLM Judge Evaluation System - Production Ready
# MAGIC
# MAGIC **Complete evaluation system for LLM responses using Databricks or OpenAI models**
# MAGIC
# MAGIC ## Features:
# MAGIC - ✅ Auto-discovery of Databricks LLM endpoints
# MAGIC - ✅ Support for OpenAI API models (GPT-4o, GPT-4o-mini, GPT-3.5-turbo)
# MAGIC - ✅ Multiple metric types (Binary, 1-5 Scale, Percentage)
# MAGIC - ✅ Multiple ground truth files per metric
# MAGIC - ✅ Robust JSON parsing with fallbacks
# MAGIC - ✅ MLflow experiment tracking
# MAGIC - ✅ Beautiful results display and export
# MAGIC
# MAGIC ## Instructions:
# MAGIC 1. **Run Cell 1**: Install packages and imports
# MAGIC 2. **Run Cell 2**: Configure file uploads
# MAGIC 3. **Run Cell 3**: Configure model settings  
# MAGIC 4. **Run Cell 4**: Verify metrics loaded
# MAGIC 5. **Run Cell 5-7**: Execute evaluation system
# MAGIC 6. **Run Cell 8**: Export results
# MAGIC 7. **Run Cell 9**: View MLflow dashboard

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 1: Installation and Setup

# COMMAND ----------

# Install packages
%pip install mlflow pandas plotly python-docx openai langchain-core langchain-openai langsmith --quiet

%restart_python

print("✅ All packages installed!")

# COMMAND ----------

# Import required libraries
import time
import os
import json
import requests
import glob
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from openai import OpenAI
import mlflow

print("✅ All libraries imported successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 2: File Configuration

# COMMAND ----------

# Widgets for file paths
dbutils.widgets.text(
    "evaluation_data_path", 
    "evaluation_data.csv", 
    "📊 Evaluation Data (CSV)"
)

dbutils.widgets.text(
    "metrics_config_path",
    "sample_metrics_config_simplified.csv",
    "📋 Metrics Configuration (CSV)"
)

dbutils.widgets.text(
    "ground_truth_files",
    "/Workspace/Users/popinb@zillowgroup.com/ground_truth_accuracy.csv;/Workspace/Users/popinb@zillowgroup.com/ground_truth_safety.csv",
    "📚 Ground Truth Files (semicolon separated)"
)

# Get settings
EVAL_DATA_PATH = dbutils.widgets.get("evaluation_data_path")
METRICS_CONFIG_PATH = dbutils.widgets.get("metrics_config_path")
GROUND_TRUTH_FILES_STRING = dbutils.widgets.get("ground_truth_files")

print("📁 FILE CONFIGURATION")
print("="*60)
print(f"Evaluation Data: {EVAL_DATA_PATH}")
print(f"Metrics Config: {METRICS_CONFIG_PATH}")
print(f"Ground Truth Files: {GROUND_TRUTH_FILES_STRING}")
print("="*60)

def parse_ground_truth_files(gt_files_string):
    """Parse semicolon or comma separated ground truth file paths."""
    if not gt_files_string or not str(gt_files_string).strip():
        return []
    
    gt_files_string = str(gt_files_string)
    
    files = []
    for separator in [';', ',']:
        if separator in gt_files_string:
            files = [f.strip() for f in gt_files_string.split(separator) if f.strip()]
            break
    
    if not files:
        files = [gt_files_string.strip()]
    
    return files

def find_file_in_workspace(filename):
    """Auto-detect file in common Databricks locations."""
    if os.path.exists(filename):
        return filename
    
    user_name = dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()
    search_locations = [
        f"/Workspace/Users/{user_name}/{filename}",
        f"./{filename}",
        f"/tmp/{filename}"
    ]
    
    for location in search_locations:
        if os.path.exists(location):
            return location
    
    return None

def load_csv_file(filename, file_type="data"):
    """Load CSV file with auto-detection."""
    try:
        file_path = find_file_in_workspace(filename)
        
        if not file_path:
            print(f"❌ {file_type.title()} file not found: {filename}")
            return None
        
        df = pd.read_csv(file_path)
        print(f"✅ Loaded {file_type}: {len(df)} rows, {len(df.columns)} columns")
        return df
        
    except Exception as e:
        print(f"❌ Error loading {file_type}: {e}")
        return None

# Load evaluation data
print(f"\n📊 Loading evaluation data...")
evaluation_data_df = load_csv_file(EVAL_DATA_PATH, "evaluation data")

if evaluation_data_df is None:
    print("\n📝 Creating sample data...")
    evaluation_data_df = pd.DataFrame({
        "sample_id": [1, 2, 3],
        "prompt": [
            "What is the capital of France?",
            "Explain machine learning in simple terms",
            "How do I bake a chocolate cake?"
        ],
        "response": [
            "The capital of France is Paris, a beautiful city known for its culture and history.",
            "Machine learning is a type of AI where computers learn patterns from data to make predictions.",
            "To bake a chocolate cake, mix flour, cocoa, eggs, and sugar, then bake at 350°F for 30 minutes."
        ]
    })
    print("✅ Sample data created")

# Load metrics configuration
print(f"\n📋 Loading metrics configuration...")
metrics_config_df = load_csv_file(METRICS_CONFIG_PATH, "metrics config")

if metrics_config_df is None:
    print("❌ No metrics configuration loaded!")
else:
    print(f"✅ Loaded {len(metrics_config_df)} metrics")

# Load ground truth files
GROUND_TRUTH_FILES_LIST = parse_ground_truth_files(GROUND_TRUTH_FILES_STRING)
ground_truth_data = {}

if GROUND_TRUTH_FILES_LIST:
    print(f"\n📚 Loading {len(GROUND_TRUTH_FILES_LIST)} ground truth files...")
    for file_path in GROUND_TRUTH_FILES_LIST:
        if file_path and os.path.exists(file_path):
            filename = os.path.basename(file_path)
            try:
                df = pd.read_csv(file_path)
                ground_truth_data[filename] = df
                print(f"✅ Loaded {filename}: {len(df)} rows")
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
        else:
            print(f"⚠️ File not found: {file_path}")

# Store data globally
EVALUATION_DATA = evaluation_data_df
METRICS_CONFIG_DATA = metrics_config_df

print(f"\n📊 Data loaded successfully!")
print(f"   Evaluation samples: {len(EVALUATION_DATA)}")
print(f"   Metrics configured: {len(METRICS_CONFIG_DATA) if METRICS_CONFIG_DATA is not None else 0}")
print(f"   Ground truth files: {len(ground_truth_data)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 3: Model Configuration

# COMMAND ----------

# Model selection
dbutils.widgets.dropdown(
    "judge_model",
    "databricks-llm",
    ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "databricks-llm"],
    "🤖 Judge Model"
)

# Get settings
JUDGE_MODEL = dbutils.widgets.get("judge_model")

print("🤖 MODEL SETTINGS")
print("="*60)
print(f"Judge Model: {JUDGE_MODEL}")
print("="*60)

# Initialize API connection
if JUDGE_MODEL == "databricks-llm":
    print("\n🏢 Databricks LLM selected")
    client = None
else:
    print("\n🔗 Initializing OpenAI connection...")
    try:
        OPENAI_KEY = dbutils.secrets.get("popin-secure-scope", "openai_key")
        os.environ["OPENAI_API_KEY"] = OPENAI_KEY
        
        client = OpenAI(
            base_url="https://api.zillowlabs.com/openai/v1",
            api_key=OPENAI_KEY
        )
        
        # Test connection
        test_response = client.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=10
        )
        print(f"✅ OpenAI connection successful!")
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 4: Verify Metrics

# COMMAND ----------

if METRICS_CONFIG_DATA is not None:
    print("✅ Metrics Configuration")
    print("="*60)
    for idx, row in METRICS_CONFIG_DATA.iterrows():
        print(f"{idx+1}. {row['name']} ({row['type']}) - threshold: {row['threshold']}")
else:
    print("❌ No metrics configuration loaded!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 5: Core Classes

# COMMAND ----------

class MetricType(Enum):
    BINARY = "binary"
    SCALE_1_5 = "1-5_scale"
    PERCENTAGE = "percentage"

@dataclass
class MetricConfig:
    name: str
    description: str
    metric_type: MetricType
    prompt_template: str
    threshold: float
    ground_truth_column: str
    ground_truth_file_path: str = ""

print("✅ Core classes defined")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 6: LLM Judge Evaluator (Main Logic)

# COMMAND ----------

import json
import time
import re
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import os

class LLMJudgeEvaluator:
    """Main evaluator class with proper prompt escaping and robust JSON parsing."""
    
    def __init__(self, judge_model: str, metrics: List[MetricConfig], ground_truth_data: Dict[str, pd.DataFrame] = None):
        self.judge_model = judge_model
        self.metrics = metrics
        self.ground_truth_data = ground_truth_data or {}
        self.is_databricks_llm = judge_model == "databricks-llm"
        
        if self.is_databricks_llm:
            self._init_databricks_llm()
        else:
            self._init_openai_llm()
    
    def _init_databricks_llm(self):
        """Initialize Databricks LLM client."""
        try:
            self.databricks_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
            self.workspace_url = dbutils.notebook.entry_point.getDbutils().notebook().getContext().browserHostName().get()
            
            self.databricks_headers = {
                "Authorization": f"Bearer {self.databricks_token}",
                "Content-Type": "application/json"
            }
            
            import requests
            url = f"https://{self.workspace_url}/api/2.0/serving-endpoints"
            response = requests.get(url, headers=self.databricks_headers, timeout=10)
            
            if response.status_code == 200:
                endpoints = response.json().get('endpoints', [])
                available_models = [ep['name'] for ep in endpoints]
                
                # Find Claude Sonnet (preferred)
                for endpoint_name in available_models:
                    if 'claude-sonnet' in endpoint_name.lower():
                        self.databricks_endpoint = endpoint_name
                        self.response_format = 'openai'
                        print(f"✅ Using Databricks endpoint: {endpoint_name}")
                        return
                
                # Fallback to first available
                if available_models:
                    self.databricks_endpoint = available_models[0]
                    self.response_format = 'openai'
                    print(f"✅ Using Databricks endpoint: {available_models[0]}")
                else:
                    raise Exception("No endpoints found")
            else:
                raise Exception(f"Failed to list endpoints: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Databricks init failed: {e}")
            raise
    
    def _init_openai_llm(self):
        """Initialize OpenAI LLM client."""
        if 'client' in globals() and client is not None:
            self.llm_client = client
            print(f"✅ OpenAI client initialized")
        else:
            raise ValueError("OpenAI client not found")
    
    def _call_databricks_llm(self, prompt: str) -> str:
        """Call Databricks LLM endpoint."""
        try:
            import requests
            url = f"https://{self.workspace_url}/serving-endpoints/{self.databricks_endpoint}/invocations"
            
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            response = requests.post(url, headers=self.databricks_headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
            
            return ""
                
        except Exception as e:
            print(f"Error calling Databricks LLM: {e}")
            return ""
    
    def _call_openai_llm(self, prompt: str) -> str:
        """Call OpenAI LLM endpoint."""
        try:
            response = self.llm_client.chat.completions.create(
                model=self.judge_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI LLM: {e}")
            return ""
    
    def _get_ground_truth_for_metric(self, metric: MetricConfig, sample_idx: int) -> str:
        """Get ground truth for a metric from multiple files."""
        try:
            files = []
            if ';' in metric.ground_truth_file_path:
                files = [f.strip() for f in metric.ground_truth_file_path.split(';') if f.strip()]
            elif ',' in metric.ground_truth_file_path:
                files = [f.strip() for f in metric.ground_truth_file_path.split(',') if f.strip()]
            else:
                files = [metric.ground_truth_file_path.strip()]
            
            if not files or not files[0]:
                return "Not provided"
            
            for file_path in files:
                filename = os.path.basename(file_path)
                if filename in self.ground_truth_data:
                    df = self.ground_truth_data[filename]
                    if metric.ground_truth_column in df.columns:
                        if sample_idx < len(df):
                            ground_truth = df[metric.ground_truth_column].iloc[sample_idx]
                            return str(ground_truth) if pd.notna(ground_truth) else "Not provided"
            
            return "Not provided"
            
        except Exception as e:
            return "Not provided"
    
    def _escape_prompt_template(self, template: str) -> str:
        """
        Properly escape prompt template to handle JSON examples.
        
        Protects {prompt}, {response}, {ground_truth} while escaping other braces.
        """
        actual_placeholders = {
            '{prompt}': '<<<PROMPT_PLACEHOLDER>>>',
            '{response}': '<<<RESPONSE_PLACEHOLDER>>>',
            '{ground_truth}': '<<<GROUND_TRUTH_PLACEHOLDER>>>'
        }
        
        escaped_template = template
        for placeholder, marker in actual_placeholders.items():
            escaped_template = escaped_template.replace(placeholder, marker)
        
        # Escape all remaining curly braces
        escaped_template = escaped_template.replace('{', '{{').replace('}', '}}')
        
        # Restore actual placeholders
        for placeholder, marker in actual_placeholders.items():
            escaped_template = escaped_template.replace(marker, placeholder)
        
        return escaped_template
    
    def evaluate_single(self, prompt: str, response: str, ground_truth_data: dict, metric: MetricConfig, sample_idx: int = 0) -> dict:
        """Evaluate a single sample with one metric."""
        try:
            ground_truth = self._get_ground_truth_for_metric(metric, sample_idx)
            
            # Escape prompt template
            safe_template = self._escape_prompt_template(metric.prompt_template)
            
            # Format prompt
            eval_prompt = safe_template.format(
                prompt=prompt,
                response=response,
                ground_truth=ground_truth if ground_truth else "Not provided"
            )
            
            # Call LLM
            if self.is_databricks_llm:
                llm_response = self._call_databricks_llm(eval_prompt)
            else:
                llm_response = self._call_openai_llm(eval_prompt)
            
            if not llm_response or str(llm_response).strip() == "":
                return {
                    "score": 0,
                    "explanation": "Empty response from LLM",
                    "status": "❌"
                }
            
            # Parse response
            score, explanation = self._parse_llm_response(llm_response, metric)
            
            status = "✅" if score >= metric.threshold else "❌"
            
            return {
                "score": score,
                "explanation": explanation,
                "status": status
            }
            
        except Exception as e:
            return {
                "score": 0,
                "explanation": f"Evaluation error: {str(e)}",
                "status": "❌"
            }
    
    def _parse_llm_response(self, llm_response: str, metric: MetricConfig) -> tuple:
        """Parse LLM response to extract score and explanation."""
        content = str(llm_response).strip()
        
        # Remove markdown code blocks
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        # Try JSON parsing
        try:
            result_json = json.loads(content)
            
            # FIXED: Extract score with metric name included
            score = self._extract_json_value(result_json, [
                metric.name,  # Check for metric name itself (e.g., "completeness_score")
                "score", "Score", "value", "Value", "rating", "Rating",
                f"{metric.name}_score", f"{metric.name}Score"
            ], default=0)
            
            # Extract explanation
            explanation = self._extract_json_value(result_json, [
                "explanation", "Explanation", "reason", "Reason",
                "comment", "Comment", "rationale", "Rationale"
            ], default="No explanation provided")
            
        except json.JSONDecodeError:
            score, explanation = self._fallback_parse(content, metric)
        
        # Normalize score
        score = self._normalize_score(score, metric.metric_type)
        
        return score, str(explanation)[:500]
    
    def _extract_json_value(self, json_obj: dict, possible_keys: list, default: Any) -> Any:
        """Extract value from JSON object trying multiple possible keys."""
        for key in possible_keys:
            if key in json_obj:
                return json_obj[key]
        return default
    
    def _fallback_parse(self, content: str, metric: MetricConfig) -> tuple:
        """Fallback parsing when JSON parsing fails."""
        score = 0
        explanation = content
        
        if metric.metric_type == MetricType.BINARY:
            if any(word in content.lower() for word in ['pass', 'correct', 'accurate', 'yes', 'true', '1']):
                score = 1
        
        elif metric.metric_type == MetricType.SCALE_1_5:
            numbers = re.findall(r'\b[1-5]\b', content)
            if numbers:
                score = int(numbers[0])
        
        elif metric.metric_type == MetricType.PERCENTAGE:
            percentages = re.findall(r'(\d+(?:\.\d+)?)[%]?', content)
            if percentages:
                score = float(percentages[0])
                if score > 1:
                    score = score / 100
        
        return score, explanation
    
    def _normalize_score(self, score: Any, metric_type: MetricType) -> float:
        """Normalize score to valid range."""
        try:
            score = float(score)
        except (ValueError, TypeError):
            return 0.0
        
        if metric_type == MetricType.BINARY:
            return 1.0 if score > 0.5 else 0.0
        elif metric_type == MetricType.SCALE_1_5:
            return max(1.0, min(5.0, score))
        elif metric_type == MetricType.PERCENTAGE:
            return max(0.0, min(1.0, score))
        
        return score
    
    def evaluate_dataset(self, evaluation_data: pd.DataFrame) -> pd.DataFrame:
        """Evaluate entire dataset with all metrics."""
        print(f"\n🔍 Evaluating {len(evaluation_data)} samples with {len(self.metrics)} metrics...")
        
        results = []
        
        for idx, row in evaluation_data.iterrows():
            sample_id = row.get('sample_id', f'sample_{idx}')
            prompt = row.get('prompt', '')
            response = row.get('response', '')
            
            print(f"\n📝 Sample {idx + 1}/{len(evaluation_data)}: {sample_id}")
            
            for metric in self.metrics:
                print(f"   📊 {metric.name}...", end=' ')
                
                ground_truth_data = {}
                for col in evaluation_data.columns:
                    if col not in ['sample_id', 'prompt', 'response']:
                        ground_truth_data[col] = row.get(col, '')
                
                result = self.evaluate_single(prompt, response, ground_truth_data, metric, idx)
                
                print(f"{result['status']}")
                
                results.append({
                    'sample_id': sample_id,
                    'metric_name': metric.name,
                    'metric_type': metric.metric_type.value,
                    'score': result['score'],
                    'threshold': result.get('threshold', metric.threshold),
                    'status': result['status'],
                    'explanation': result['explanation'],
                    'prompt': prompt[:100] + "..." if len(prompt) > 100 else prompt,
                    'response': response[:100] + "..." if len(response) > 100 else response
                })
        
        print(f"\n✅ Evaluation complete!")
        return pd.DataFrame(results)

print("✅ LLM Judge Evaluator defined")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 7: Run Evaluation

# COMMAND ----------

def load_metrics_from_csv():
    """Load metrics from CSV."""
    if METRICS_CONFIG_DATA is None:
        return []
    
    metric_configs = []
    for _, row in METRICS_CONFIG_DATA.iterrows():
        metric_type_str = row['type'].strip().lower()
        if metric_type_str == 'binary':
            metric_type = MetricType.BINARY
        elif metric_type_str in ['1-5_scale', 'scale_1_5']:
            metric_type = MetricType.SCALE_1_5
        elif metric_type_str == 'percentage':
            metric_type = MetricType.PERCENTAGE
        else:
            metric_type = MetricType.BINARY
        
        metric_config = MetricConfig(
            name=row['name'].strip(),
            metric_type=metric_type,
            description=row['description'].strip(),
            prompt_template=row['evaluation_prompt'].strip(),
            threshold=float(row['threshold']),
            ground_truth_column=row['ground_truth_column'].strip(),
            ground_truth_file_path=row['ground_truth_file_path'].strip()
        )
        
        metric_configs.append(metric_config)
    
    return metric_configs

# Load metrics
metric_configs = load_metrics_from_csv()

if not metric_configs:
    print("❌ No valid metrics!")
else:
    # Create evaluator
    evaluator = LLMJudgeEvaluator(
        judge_model=JUDGE_MODEL,
        metrics=metric_configs,
        ground_truth_data=ground_truth_data
    )
    
    # Run evaluation
    print("="*60)
    print("🚀 STARTING EVALUATION")
    print("="*60)
    
    start_time = time.time()
    results_df = evaluator.evaluate_dataset(EVALUATION_DATA)
    eval_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"✅ COMPLETE in {eval_time:.1f}s")
    print(f"{'='*60}")
    
    # Display summary
    total = len(results_df)
    passed = len(results_df[results_df['status'] == '✅'])
    pass_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"\n📊 RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Total Evaluations: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"{'='*60}")
    
    # Per-metric results
    for metric_name in results_df['metric_name'].unique():
        metric_results = results_df[results_df['metric_name'] == metric_name]
        metric_passed = len(metric_results[metric_results['status'] == '✅'])
        metric_total = len(metric_results)
        metric_pass_rate = (metric_passed / metric_total) * 100 if metric_total > 0 else 0
        avg_score = metric_results['score'].mean()
        
        print(f"\n🔹 {metric_name}:")
        print(f"   Pass Rate: {metric_pass_rate:.1f}% ({metric_passed}/{metric_total})")
        print(f"   Avg Score: {avg_score:.2f}")
        print(f"   Threshold: {metric_results['threshold'].iloc[0]}")
    
    # Store globally
    globals()['results_df'] = results_df
    
    # Log to MLflow
    mlflow.set_experiment(f"/Users/{dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()}/llm_evaluation_experiment")
    
    with mlflow.start_run(run_name=f"eval_{JUDGE_MODEL}_{time.strftime('%Y%m%d_%H%M%S')}"):
        mlflow.log_param("judge_model", JUDGE_MODEL)
        mlflow.log_param("num_samples", len(EVALUATION_DATA))
        mlflow.log_param("metrics", ",".join([cfg.name for cfg in metric_configs]))
        
        mlflow.log_metric("overall_pass_rate", pass_rate)
        mlflow.log_metric("total_evaluations", total)
        mlflow.log_metric("passed_evaluations", passed)
        
        for metric_name in results_df['metric_name'].unique():
            metric_results = results_df[results_df['metric_name'] == metric_name]
            scores = metric_results['score'].tolist()
            numeric_scores = [s for s in scores if isinstance(s, (int, float))]
            
            if numeric_scores:
                mean_score = sum(numeric_scores) / len(numeric_scores)
                threshold = metric_results['threshold'].iloc[0]
                pass_count = sum(1 for s in numeric_scores if s >= threshold)
                pass_rate_metric = (pass_count / len(numeric_scores)) * 100
                
                mlflow.log_metric(f"{metric_name}_mean", float(mean_score))
                mlflow.log_metric(f"{metric_name}_pass_rate", float(pass_rate_metric))
        
        # Save results
        out_dir = "/tmp/llm_eval_artifacts"
        os.makedirs(out_dir, exist_ok=True)
        csv_path = os.path.join(out_dir, f"results_{int(time.time())}.csv")
        results_df.to_csv(csv_path, index=False)
        mlflow.log_artifact(csv_path, artifact_path="tables")
    
    print(f"\n✅ Results logged to MLflow")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 8: Export Results

# COMMAND ----------

if 'results_df' in globals() and not results_df.empty:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    user_name = dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()
    workspace_path = f"/Workspace/Users/{user_name}"
    
    filename = f"{workspace_path}/llm_evaluation_results_{timestamp}.csv"
    results_df.to_csv(filename, index=False)
    
    print(f"📊 Results exported to: {filename}")
    print(f"✅ {len(results_df)} evaluations saved")
    
    # Display first few rows
    print(f"\n📋 Sample Results:")
    display(results_df.head(10))
else:
    print("❌ No results to export")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 9: MLflow Dashboard

# COMMAND ----------

import plotly.io as pio

MLFLOW_EXPERIMENT_PATH = f"/Users/{dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()}/llm_evaluation_experiment"

print("Creating dashboard from MLflow data...")

exp = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_PATH)
if exp is None:
    print(f"❌ Experiment not found: {MLFLOW_EXPERIMENT_PATH}")
else:
    runs_df = mlflow.search_runs(
        experiment_ids=[exp.experiment_id],
        filter_string="attributes.status = 'FINISHED'",
        order_by=["attributes.start_time DESC"],
        max_results=100
    )
    
    num_runs = len(runs_df)
    print(f"✅ Found {num_runs} runs")
    
    if num_runs > 0:
        # Get metric columns
        metric_mean_cols = [c for c in runs_df.columns if c.startswith("metrics.") and c.endswith("_mean")]
        metric_pass_cols = [c for c in runs_df.columns if c.startswith("metrics.") and c.endswith("_pass_rate")]
        
        # Latest run summary
        latest = runs_df.iloc[0]
        
        print(f"\n📊 LATEST RUN SUMMARY")
        print(f"{'='*60}")
        print(f"Run ID: {latest['run_id'][:8]}...")
        print(f"Model: {latest.get('params.judge_model', 'N/A')}")
        print(f"Samples: {latest.get('params.num_samples', 'N/A')}")
        
        for col in metric_pass_cols:
            metric_name = col.replace('metrics.', '').replace('_pass_rate', '')
            pass_rate = latest[col]
            print(f"{metric_name}: {pass_rate:.1f}%")
        
        print(f"{'='*60}")
        
        # Create visualization
        fig = go.Figure()
        
        for col in metric_pass_cols:
            metric_name = col.replace('metrics.', '').replace('_pass_rate', '')
            fig.add_trace(go.Scatter(
                x=runs_df['start_time'],
                y=runs_df[col],
                mode='lines+markers',
                name=metric_name
            ))
        
        fig.update_layout(
            title="Metric Pass Rates Over Time",
            xaxis_title="Run Time",
            yaxis_title="Pass Rate (%)",
            height=500
        )
        
        displayHTML(pio.to_html(fig, include_plotlyjs='cdn'))
    else:
        print("No runs found")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🎉 Evaluation Complete!
# MAGIC
# MAGIC **System Features:**
# MAGIC - ✅ Databricks + OpenAI model support
# MAGIC - ✅ Multiple ground truth files per metric
# MAGIC - ✅ Robust JSON parsing with fallbacks
# MAGIC - ✅ MLflow experiment tracking
# MAGIC - ✅ CSV export functionality
# MAGIC - ✅ Interactive dashboard
# MAGIC
# MAGIC **Next Steps:**
# MAGIC 1. Review results in Cell 8
# MAGIC 2. Check MLflow dashboard in Cell 9
# MAGIC 3. Export data for further analysis
# MAGIC 4. Customize metrics for your use case
