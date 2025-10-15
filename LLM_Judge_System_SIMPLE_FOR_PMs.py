# Databricks notebook source
# MAGIC %md
# MAGIC # 🤖 LLM Judge Evaluation System - Simple PM Version
# MAGIC
# MAGIC **No coding required! Just write grading rubrics in plain English.**
# MAGIC
# MAGIC ## For Product Managers:
# MAGIC - ✅ Write grading rubrics in plain English (no JSON, no code!)
# MAGIC - ✅ System auto-generates proper prompts for you
# MAGIC - ✅ Support for any custom metric name
# MAGIC - ✅ Simple CSV format (edit in Excel)
# MAGIC - ✅ Beautiful results and dashboard
# MAGIC
# MAGIC ## Quick Start:
# MAGIC 1. Create metrics CSV with your grading rubrics
# MAGIC 2. Upload your evaluation data
# MAGIC 3. Upload ground truth files (optional)
# MAGIC 4. Run the notebook
# MAGIC 5. Get results!

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 1: Installation

# COMMAND ----------

%pip install mlflow pandas plotly openai langchain-core langchain-openai --quiet
%restart_python
print("✅ Packages installed!")

# COMMAND ----------

import time
import os
import json
import requests
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

from openai import OpenAI
import mlflow

print("✅ Libraries imported successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 2: File Configuration
# MAGIC **Update the file paths below with your files**

# COMMAND ----------

# Widgets for file paths
dbutils.widgets.text("evaluation_data_path", "evaluation_data.csv", "📊 Evaluation Data CSV")
dbutils.widgets.text("metrics_config_path", "metrics_config.csv", "📋 Metrics Config CSV")
dbutils.widgets.text("ground_truth_files", "/Workspace/Users/your.email@company.com/ground_truth_accuracy.csv;/Workspace/Users/your.email@company.com/ground_truth_safety.csv", "📚 Ground Truth Files (semicolon separated)")

EVAL_DATA_PATH = dbutils.widgets.get("evaluation_data_path")
METRICS_CONFIG_PATH = dbutils.widgets.get("metrics_config_path")
GROUND_TRUTH_FILES_STRING = dbutils.widgets.get("ground_truth_files")

print("📁 FILE CONFIGURATION")
print("="*60)
print(f"Evaluation Data: {EVAL_DATA_PATH}")
print(f"Metrics Config: {METRICS_CONFIG_PATH}")
print(f"Ground Truth Files: {GROUND_TRUTH_FILES_STRING}")
print("="*60)

def find_file(filename):
    """Find file in workspace."""
    if os.path.exists(filename):
        return filename
    user_name = dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()
    paths = [f"/Workspace/Users/{user_name}/{filename}", f"./{filename}", f"/tmp/{filename}"]
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def load_csv(filename, file_type="data"):
    """Load CSV file."""
    try:
        file_path = find_file(filename)
        if not file_path:
            print(f"❌ {file_type} not found: {filename}")
            return None
        df = pd.read_csv(file_path)
        print(f"✅ Loaded {file_type}: {len(df)} rows")
        return df
    except Exception as e:
        print(f"❌ Error loading {file_type}: {e}")
        return None

# Load files
print(f"\n📊 Loading data...")
evaluation_data_df = load_csv(EVAL_DATA_PATH, "evaluation data")

if evaluation_data_df is None:
    evaluation_data_df = pd.DataFrame({
        "sample_id": [1, 2, 3],
        "prompt": ["What is the capital of France?", "Explain machine learning", "How do I bake a cake?"],
        "response": ["Paris is the capital of France.", "ML is AI that learns from data.", "Mix flour, eggs, sugar, bake at 350°F."]
    })
    print("✅ Using sample data")

metrics_config_df = load_csv(METRICS_CONFIG_PATH, "metrics config")

# Load ground truth files
ground_truth_data = {}
if GROUND_TRUTH_FILES_STRING:
    files = [f.strip() for f in GROUND_TRUTH_FILES_STRING.split(';') if f.strip()]
    print(f"\n📚 Loading {len(files)} ground truth files...")
    for file_path in files:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            df = pd.read_csv(file_path)
            ground_truth_data[filename] = df
            print(f"✅ Loaded {filename}")

EVALUATION_DATA = evaluation_data_df
METRICS_CONFIG_DATA = metrics_config_df

print(f"\n✅ Data ready: {len(EVALUATION_DATA)} samples, {len(METRICS_CONFIG_DATA) if METRICS_CONFIG_DATA is not None else 0} metrics, {len(ground_truth_data)} GT files")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 3: Model Configuration

# COMMAND ----------

dbutils.widgets.dropdown("judge_model", "databricks-llm", ["gpt-4o", "gpt-4o-mini", "databricks-llm"], "🤖 Judge Model")

JUDGE_MODEL = dbutils.widgets.get("judge_model")

print(f"🤖 Model: {JUDGE_MODEL}")

if JUDGE_MODEL != "databricks-llm":
    OPENAI_KEY = dbutils.secrets.get("popin-secure-scope", "openai_key")
    os.environ["OPENAI_API_KEY"] = OPENAI_KEY
    client = OpenAI(base_url="https://api.zillowlabs.com/openai/v1", api_key=OPENAI_KEY)
    print("✅ OpenAI client ready")
else:
    client = None
    print("✅ Databricks LLM ready")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 4: Core Classes

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
    grading_rubric: str
    threshold: float
    ground_truth_column: str
    ground_truth_file_path: str = ""

print("✅ Classes defined")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 5: Auto-Prompt Generator
# MAGIC **Automatically builds proper prompts from PM's grading rubrics**

# COMMAND ----------

class PromptGenerator:
    """Automatically generates proper evaluation prompts from simple grading rubrics."""
    
    @staticmethod
    def generate_prompt(metric: MetricConfig) -> str:
        """
        Auto-generate evaluation prompt from grading rubric.
        
        PM just writes: "Check if the response is accurate"
        System generates: Full prompt with JSON instructions, placeholders, etc.
        """
        
        # Build scoring instructions based on metric type
        if metric.metric_type == MetricType.BINARY:
            score_instruction = "Score: 1 if criteria met, 0 if not"
            example_score = "1"
        elif metric.metric_type == MetricType.SCALE_1_5:
            score_instruction = "Score: Rate from 1 (worst) to 5 (best)"
            example_score = "4"
        else:  # PERCENTAGE
            score_instruction = "Score: Percentage from 0 to 100"
            example_score = "85"
        
        # Build the complete evaluation prompt
        prompt = f"""You are an expert evaluator. Your task:

{metric.grading_rubric}

**Information to evaluate:**
- User Query: {{prompt}}
- AI Response: {{response}}
- Ground Truth: {{ground_truth}}

**Scoring Instructions:**
{score_instruction}

**Output Format:**
Return ONLY a JSON object with these two fields:
- "score": {example_score}
- "explanation": "Brief explanation of your rating"

Do not include any other text outside the JSON.
"""
        
        return prompt

print("✅ Auto-Prompt Generator ready")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 6: Evaluator with Smart Parsing

# COMMAND ----------

class LLMJudgeEvaluator:
    """Evaluator with bulletproof JSON parsing for ANY metric name."""
    
    def __init__(self, judge_model: str, metrics: List[MetricConfig], ground_truth_data: Dict[str, pd.DataFrame] = None):
        self.judge_model = judge_model
        self.metrics = metrics
        self.ground_truth_data = ground_truth_data or {}
        self.is_databricks_llm = judge_model == "databricks-llm"
        
        if self.is_databricks_llm:
            self._init_databricks()
        else:
            self._init_openai()
    
    def _init_databricks(self):
        """Initialize Databricks client."""
        self.databricks_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
        self.workspace_url = dbutils.notebook.entry_point.getDbutils().notebook().getContext().browserHostName().get()
        self.databricks_headers = {"Authorization": f"Bearer {self.databricks_token}", "Content-Type": "application/json"}
        
        response = requests.get(f"https://{self.workspace_url}/api/2.0/serving-endpoints", headers=self.databricks_headers, timeout=10)
        endpoints = response.json().get('endpoints', []) if response.status_code == 200 else []
        
        # Find Claude Sonnet or use first available
        for ep in endpoints:
            if 'claude-sonnet' in ep['name'].lower():
                self.databricks_endpoint = ep['name']
                print(f"✅ Using: {ep['name']}")
                return
        
        self.databricks_endpoint = endpoints[0]['name'] if endpoints else "default"
        print(f"✅ Using: {self.databricks_endpoint}")
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        if 'client' in globals() and client is not None:
            self.llm_client = client
            print("✅ OpenAI ready")
        else:
            raise ValueError("OpenAI client not found")
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM (Databricks or OpenAI)."""
        try:
            if self.is_databricks_llm:
                url = f"https://{self.workspace_url}/serving-endpoints/{self.databricks_endpoint}/invocations"
                payload = {"messages": [{"role": "user", "content": prompt}], "max_tokens": 1000, "temperature": 0.1}
                response = requests.post(url, headers=self.databricks_headers, json=payload, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and result['choices']:
                        return result['choices'][0]['message']['content']
            else:
                response = self.llm_client.chat.completions.create(
                    model=self.judge_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.1
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"LLM error: {e}")
        return ""
    
    def _get_ground_truth(self, metric: MetricConfig, sample_idx: int) -> str:
        """Get ground truth for metric."""
        try:
            files = [f.strip() for f in metric.ground_truth_file_path.split(';') if f.strip()]
            for file_path in files:
                filename = os.path.basename(file_path)
                if filename in self.ground_truth_data:
                    df = self.ground_truth_data[filename]
                    if metric.ground_truth_column in df.columns and sample_idx < len(df):
                        gt = df[metric.ground_truth_column].iloc[sample_idx]
                        return str(gt) if pd.notna(gt) else "Not provided"
        except:
            pass
        return "Not provided"
    
    def _smart_extract_score(self, json_obj: dict, metric: MetricConfig) -> Any:
        """
        BULLETPROOF score extraction for ANY metric name.
        Tries 6 different strategies to find the score.
        """
        # Strategy 1: Standard keys
        for key in ["score", "Score", "value", "Value", "rating", "Rating", "result", "Result"]:
            if key in json_obj:
                return json_obj[key]
        
        # Strategy 2: Exact metric name
        if metric.name in json_obj:
            return json_obj[metric.name]
        
        # Strategy 3: Metric name with/without common suffixes
        base_name = metric.name
        for suffix in ['_score', '_rating', '_check', '_value', '_result']:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break
        
        if base_name in json_obj:
            return json_obj[base_name]
        
        for suffix in ['_score', '_rating', '_value', '_result']:
            if f"{base_name}{suffix}" in json_obj:
                return json_obj[f"{base_name}{suffix}"]
        
        # Strategy 4: Case-insensitive
        metric_lower = metric.name.lower()
        for key, value in json_obj.items():
            if key.lower() == metric_lower:
                return value
        
        # Strategy 5: Partial match
        for key, value in json_obj.items():
            if metric.name.lower() in key.lower() or any(word in key.lower() for word in ['score', 'rating', 'value']):
                if isinstance(value, (int, float, str)):
                    try:
                        return float(value) if '.' in str(value) else int(value)
                    except:
                        pass
        
        # Strategy 6: ANY numeric value
        for value in json_obj.values():
            if isinstance(value, (int, float)):
                return value
        
        return 0
    
    def _smart_extract_explanation(self, json_obj: dict) -> str:
        """Extract explanation from JSON."""
        for key in ["explanation", "Explanation", "reason", "Reason", "comment", "rationale", "justification"]:
            if key in json_obj:
                return json_obj[key]
        
        for key, value in json_obj.items():
            if 'explan' in key.lower() or 'reason' in key.lower():
                if isinstance(value, str):
                    return value
        
        for value in json_obj.values():
            if isinstance(value, str) and len(value) > 10:
                return value
        
        return "No explanation"
    
    def evaluate_single(self, prompt: str, response: str, metric: MetricConfig, sample_idx: int = 0) -> dict:
        """Evaluate single sample."""
        try:
            # Get ground truth
            ground_truth = self._get_ground_truth(metric, sample_idx)
            
            # Generate evaluation prompt from grading rubric
            eval_prompt = metric.prompt_template.format(
                prompt=prompt,
                response=response,
                ground_truth=ground_truth
            )
            
            # Call LLM
            llm_response = self._call_llm(eval_prompt)
            
            if not llm_response:
                return {"score": 0, "explanation": "No LLM response", "status": "❌"}
            
            # Parse response
            content = llm_response.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            try:
                result_json = json.loads(content)
                score = self._smart_extract_score(result_json, metric)
                explanation = self._smart_extract_explanation(result_json)
            except:
                # Fallback parsing
                score, explanation = self._fallback_parse(content, metric)
            
            # Normalize score
            score = self._normalize_score(score, metric.metric_type)
            
            status = "✅" if score >= metric.threshold else "❌"
            
            return {"score": score, "explanation": str(explanation)[:500], "status": status}
            
        except Exception as e:
            return {"score": 0, "explanation": f"Error: {e}", "status": "❌"}
    
    def _fallback_parse(self, content: str, metric: MetricConfig) -> tuple:
        """Fallback text parsing."""
        score, explanation = 0, content
        
        if metric.metric_type == MetricType.BINARY:
            if any(w in content.lower() for w in ['pass', 'correct', 'yes', 'true', '1']):
                score = 1
        elif metric.metric_type == MetricType.SCALE_1_5:
            nums = re.findall(r'\b[1-5]\b', content)
            if nums:
                score = int(nums[0])
        else:  # PERCENTAGE
            pcts = re.findall(r'(\d+(?:\.\d+)?)', content)
            if pcts:
                score = float(pcts[0])
                if score > 1:
                    score = score / 100
        
        return score, explanation
    
    def _normalize_score(self, score: Any, metric_type: MetricType) -> float:
        """Normalize score to valid range."""
        try:
            score = float(score)
        except:
            return 0.0
        
        if metric_type == MetricType.BINARY:
            return 1.0 if score > 0.5 else 0.0
        elif metric_type == MetricType.SCALE_1_5:
            return max(1.0, min(5.0, score))
        else:  # PERCENTAGE
            if score > 1:
                score = score / 100
            return max(0.0, min(1.0, score))
    
    def evaluate_dataset(self, data: pd.DataFrame) -> pd.DataFrame:
        """Evaluate all samples."""
        print(f"\n🔍 Evaluating {len(data)} samples...")
        results = []
        
        for idx, row in data.iterrows():
            sample_id = row.get('sample_id', idx)
            prompt = row.get('prompt', '')
            response = row.get('response', '')
            
            print(f"\n📝 Sample {idx + 1}/{len(data)}")
            
            for metric in self.metrics:
                print(f"   {metric.name}...", end=' ')
                result = self.evaluate_single(prompt, response, metric, idx)
                print(result['status'])
                
                results.append({
                    'sample_id': sample_id,
                    'metric_name': metric.name,
                    'metric_type': metric.metric_type.value,
                    'score': result['score'],
                    'threshold': metric.threshold,
                    'status': result['status'],
                    'explanation': result['explanation'],
                    'prompt': prompt[:100] + "..." if len(prompt) > 100 else prompt,
                    'response': response[:100] + "..." if len(response) > 100 else response
                })
        
        print(f"\n✅ Done!")
        return pd.DataFrame(results)

print("✅ Evaluator ready")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 6: Load and Process Metrics

# COMMAND ----------

def auto_build_prompt_from_rubric(grading_rubric: str, metric_type: MetricType) -> str:
    """
    Auto-generate proper evaluation prompt from simple grading rubric.
    
    PM writes: "Check if response is accurate"
    System generates: Complete prompt with JSON format, placeholders, etc.
    """
    
    # Determine scoring instructions
    if metric_type == MetricType.BINARY:
        score_instruction = "Return a score of 1 if the criteria is met, or 0 if not."
        example = '"score": 1'
    elif metric_type == MetricType.SCALE_1_5:
        score_instruction = "Return a score from 1 (worst) to 5 (best)."
        example = '"score": 4'
    else:  # PERCENTAGE
        score_instruction = "Return a score from 0 to 100 representing the percentage."
        example = '"score": 85'
    
    # Build complete prompt with proper escaping handled automatically
    prompt_template = f"""You are an expert evaluator. Evaluate the AI response based on these criteria:

{grading_rubric}

**User Query:** {{prompt}}

**AI Response:** {{response}}

**Ground Truth (Reference Answer):** {{ground_truth}}

**Your Task:**
{score_instruction}

**Required Output Format:**
Return ONLY valid JSON with exactly these two fields:
{{
  {example},
  "explanation": "Brief explanation of your score"
}}

Important: Return ONLY the JSON object, no other text."""
    
    return prompt_template

def load_metrics_from_csv():
    """Load metrics and auto-generate prompts from rubrics."""
    if METRICS_CONFIG_DATA is None:
        return []
    
    metrics = []
    for _, row in METRICS_CONFIG_DATA.iterrows():
        # Get metric type
        type_str = row['type'].strip().lower()
        if type_str == 'binary':
            metric_type = MetricType.BINARY
        elif type_str in ['1-5_scale', 'scale_1_5', 'scale_1_to_5']:
            metric_type = MetricType.SCALE_1_5
        elif type_str in ['percentage', 'percent']:
            metric_type = MetricType.PERCENTAGE
        else:
            metric_type = MetricType.BINARY
        
        # Get grading rubric (try multiple column names for flexibility)
        grading_rubric = row.get('grading_rubric', row.get('evaluation_prompt', row.get('description', '')))
        
        # Auto-generate proper evaluation prompt
        auto_prompt = auto_build_prompt_from_rubric(grading_rubric, metric_type)
        
        metric = MetricConfig(
            name=row['name'].strip(),
            metric_type=metric_type,
            description=row.get('description', '').strip(),
            grading_rubric=grading_rubric.strip(),
            prompt_template=auto_prompt,  # Use auto-generated prompt
            threshold=float(row['threshold']),
            ground_truth_column=row['ground_truth_column'].strip(),
            ground_truth_file_path=row.get('ground_truth_file_path', '').strip()
        )
        
        metrics.append(metric)
        print(f"✅ {metric.name} ({metric.metric_type.value})")
    
    return metrics

print("Loading metrics...")
metric_configs = load_metrics_from_csv()
print(f"✅ Loaded {len(metric_configs)} metrics")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 7: Run Evaluation

# COMMAND ----------

if metric_configs:
    evaluator = LLMJudgeEvaluator(JUDGE_MODEL, metric_configs, ground_truth_data)
    
    print("="*60)
    print("🚀 STARTING EVALUATION")
    print("="*60)
    
    start = time.time()
    results_df = evaluator.evaluate_dataset(EVALUATION_DATA)
    duration = time.time() - start
    
    print(f"\n{'='*60}")
    print(f"✅ COMPLETE in {duration:.1f}s")
    print(f"{'='*60}")
    
    # Summary
    total = len(results_df)
    passed = len(results_df[results_df['status'] == '✅'])
    pass_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"\n📊 RESULTS")
    print(f"{'='*60}")
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"{'='*60}")
    
    # Per-metric
    for metric_name in results_df['metric_name'].unique():
        m_res = results_df[results_df['metric_name'] == metric_name]
        m_pass = len(m_res[m_res['status'] == '✅'])
        m_total = len(m_res)
        m_rate = (m_pass / m_total) * 100 if m_total > 0 else 0
        m_avg = m_res['score'].mean()
        
        print(f"\n{metric_name}:")
        print(f"  Pass Rate: {m_rate:.1f}% ({m_pass}/{m_total})")
        print(f"  Avg Score: {m_avg:.2f}")
    
    globals()['results_df'] = results_df
    
    # MLflow logging
    user_name = dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()
    mlflow.set_experiment(f"/Users/{user_name}/llm_evaluation")
    
    with mlflow.start_run(run_name=f"eval_{time.strftime('%Y%m%d_%H%M%S')}"):
        mlflow.log_param("model", JUDGE_MODEL)
        mlflow.log_param("samples", len(EVALUATION_DATA))
        mlflow.log_metric("pass_rate", pass_rate)
        mlflow.log_metric("total", total)
        
        for metric_name in results_df['metric_name'].unique():
            m_res = results_df[results_df['metric_name'] == metric_name]
            scores = [s for s in m_res['score'].tolist() if isinstance(s, (int, float))]
            if scores:
                mlflow.log_metric(f"{metric_name}_mean", float(sum(scores) / len(scores)))
                threshold = m_res['threshold'].iloc[0]
                passed_count = sum(1 for s in scores if s >= threshold)
                mlflow.log_metric(f"{metric_name}_pass_rate", float(passed_count / len(scores) * 100))
        
        # Save results
        os.makedirs("/tmp/results", exist_ok=True)
        csv_path = f"/tmp/results/eval_{int(time.time())}.csv"
        results_df.to_csv(csv_path, index=False)
        mlflow.log_artifact(csv_path)
    
    print(f"\n✅ Logged to MLflow")
else:
    print("❌ No metrics loaded")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 8: Export Results

# COMMAND ----------

if 'results_df' in globals() and not results_df.empty:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    user_name = dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()
    
    filename = f"/Workspace/Users/{user_name}/evaluation_results_{timestamp}.csv"
    results_df.to_csv(filename, index=False)
    
    print(f"✅ Results saved to: {filename}")
    print(f"✅ {len(results_df)} evaluations exported")
    
    print(f"\n📊 Results Preview:")
    display(results_df.head(10))
else:
    print("❌ No results to export")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 9: Dashboard

# COMMAND ----------

user_name = dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()
exp = mlflow.get_experiment_by_name(f"/Users/{user_name}/llm_evaluation")

if exp:
    runs = mlflow.search_runs(
        experiment_ids=[exp.experiment_id],
        filter_string="attributes.status = 'FINISHED'",
        order_by=["start_time DESC"],
        max_results=50
    )
    
    print(f"✅ Found {len(runs)} runs")
    
    if len(runs) > 0:
        # Get metrics
        metric_cols = [c for c in runs.columns if c.startswith("metrics.") and c.endswith("_pass_rate")]
        
        # Visualization
        fig = go.Figure()
        for col in metric_cols:
            name = col.replace('metrics.', '').replace('_pass_rate', '')
            fig.add_trace(go.Scatter(
                x=runs['start_time'],
                y=runs[col],
                mode='lines+markers',
                name=name
            ))
        
        fig.update_layout(
            title="Evaluation Pass Rates Over Time",
            xaxis_title="Time",
            yaxis_title="Pass Rate (%)",
            height=500
        )
        
        displayHTML(pio.to_html(fig, include_plotlyjs='cdn'))
        
        # Latest run summary
        latest = runs.iloc[0]
        print(f"\n📊 Latest Run:")
        print(f"Model: {latest.get('params.model', 'N/A')}")
        print(f"Samples: {latest.get('params.samples', 'N/A')}")
        for col in metric_cols:
            name = col.replace('metrics.', '').replace('_pass_rate', '')
            print(f"{name}: {latest[col]:.1f}%")
else:
    print("No experiment found")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🎉 Complete!
# MAGIC
# MAGIC **What You Did:**
# MAGIC - ✅ Defined metrics with simple grading rubrics
# MAGIC - ✅ System auto-generated proper prompts
# MAGIC - ✅ Evaluated your AI responses
# MAGIC - ✅ Got scores and explanations
# MAGIC - ✅ Exported results to CSV
# MAGIC - ✅ Tracked in MLflow dashboard
# MAGIC
# MAGIC **No JSON formatting, no code, just plain English rubrics!** 🚀
