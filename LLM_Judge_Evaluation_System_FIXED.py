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
# MAGIC - ✅ Robust JSON parsing that works with ANY custom metric name
# MAGIC - ✅ MLflow experiment tracking
# MAGIC - ✅ Beautiful results display and export

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
    print("💡 TIP: In your metrics CSV, just specify the filename (e.g., 'ground_truth_accuracy.csv')")
    print("        Code will automatically match it to the uploaded files below:\n")
    
    for file_path in GROUND_TRUTH_FILES_LIST:
        if file_path and os.path.exists(file_path):
            filename = os.path.basename(file_path)
            try:
                df = pd.read_csv(file_path)
                ground_truth_data[filename] = df
                print(f"✅ {filename} → {len(df)} rows, columns: {', '.join(df.columns.tolist())}")
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
        else:
            print(f"⚠️ File not found: {file_path}")
    
    print(f"\n✅ Loaded {len(ground_truth_data)} ground truth files")

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
    """
    Main evaluator class with bulletproof JSON parsing for ANY custom metric name.
    
    Key Innovation: Smart key detection that works with any metric naming convention.
    """
    
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
        """
        Get ground truth for a metric from ground truth files.
        
        How it works:
        1. PM specifies just the FILENAME in CSV (e.g., 'ground_truth_accuracy.csv')
        2. Full paths come from UI widget (e.g., '/Workspace/Users/email/ground_truth_accuracy.csv')
        3. Code matches filename from CSV to actual uploaded files
        
        This means PMs don't need to know full paths - just the filename!
        """
        try:
            # PM can specify filename or full path - we handle both
            files = []
            if ';' in metric.ground_truth_file_path:
                files = [f.strip() for f in metric.ground_truth_file_path.split(';') if f.strip()]
            elif ',' in metric.ground_truth_file_path:
                files = [f.strip() for f in metric.ground_truth_file_path.split(',') if f.strip()]
            else:
                files = [metric.ground_truth_file_path.strip()]
            
            if not files or not files[0]:
                return "Not provided"
            
            # Match by filename (PM provides filename, widget provides full paths)
            for file_path in files:
                filename = os.path.basename(file_path)  # Extract just the filename
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
        """
        BULLETPROOF JSON parsing that works with ANY custom metric name.
        
        Strategy:
        1. Try to parse as JSON
        2. Look for score using intelligent key detection
        3. Fall back to text parsing if JSON fails
        """
        content = str(llm_response).strip()
        
        # Remove markdown code blocks
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        # Try JSON parsing
        try:
            result_json = json.loads(content)
            
            # BULLETPROOF: Smart score extraction
            score = self._smart_extract_score(result_json, metric)
            
            # BULLETPROOF: Smart explanation extraction
            explanation = self._smart_extract_explanation(result_json)
            
        except json.JSONDecodeError:
            # Fallback to text parsing
            score, explanation = self._fallback_parse(content, metric)
        
        # Normalize score
        score = self._normalize_score(score, metric.metric_type)
        
        return score, str(explanation)[:500]
    
    def _smart_extract_score(self, json_obj: dict, metric: MetricConfig) -> Any:
        """
        BULLETPROOF score extraction that handles ANY custom metric name.
        
        Strategy:
        1. Try standard keys first (score, value, rating)
        2. Try the exact metric name
        3. Try metric name variations (with/without common suffixes)
        4. Try case-insensitive search through all keys
        5. Try finding any numeric value in the JSON
        """
        # Step 1: Try standard keys first (most common)
        standard_keys = ["score", "Score", "value", "Value", "rating", "Rating", "result", "Result"]
        for key in standard_keys:
            if key in json_obj:
                return json_obj[key]
        
        # Step 2: Try exact metric name
        if metric.name in json_obj:
            return json_obj[metric.name]
        
        # Step 3: Try metric name with common suffix variations
        # Remove common suffixes if they exist
        base_name = metric.name
        common_suffixes = ['_score', '_rating', '_check', '_value', '_result', 'Score', 'Rating', 'Check', 'Value', 'Result']
        
        for suffix in common_suffixes:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break
        
        # Try base name without suffix
        if base_name in json_obj:
            return json_obj[base_name]
        
        # Try base name with different suffixes
        for suffix in ['_score', '_rating', '_value', 'Score', 'Rating', 'Value']:
            key = f"{base_name}{suffix}"
            if key in json_obj:
                return json_obj[key]
        
        # Step 4: Case-insensitive search
        metric_name_lower = metric.name.lower()
        for key, value in json_obj.items():
            if key.lower() == metric_name_lower:
                return value
        
        # Step 5: Look for keys containing the metric name or common score words
        score_keywords = ['score', 'rating', 'value', 'result', metric.name.lower()]
        for key, value in json_obj.items():
            key_lower = key.lower()
            for keyword in score_keywords:
                if keyword in key_lower and isinstance(value, (int, float, str)):
                    try:
                        # Try to convert to number
                        return float(value) if '.' in str(value) else int(value)
                    except:
                        pass
        
        # Step 6: Last resort - find ANY numeric value in the JSON
        for key, value in json_obj.items():
            if isinstance(value, (int, float)):
                return value
            if isinstance(value, str):
                try:
                    return float(value) if '.' in value else int(value)
                except:
                    pass
        
        # If nothing found, return 0
        return 0
    
    def _smart_extract_explanation(self, json_obj: dict) -> str:
        """
        BULLETPROOF explanation extraction.
        
        Tries multiple common keys for explanations.
        """
        explanation_keys = [
            "explanation", "Explanation", 
            "reason", "Reason", 
            "comment", "Comment", 
            "rationale", "Rationale", 
            "justification", "Justification",
            "reasoning", "Reasoning",
            "details", "Details",
            "description", "Description"
        ]
        
        # Try standard keys
        for key in explanation_keys:
            if key in json_obj:
                return json_obj[key]
        
        # Case-insensitive search
        for key, value in json_obj.items():
            key_lower = key.lower()
            if any(exp_key.lower() in key_lower for exp_key in explanation_keys):
                if isinstance(value, str):
                    return value
        
        # Look for any string value that's not too short
        for key, value in json_obj.items():
            if isinstance(value, str) and len(value) > 10:
                return value
        
        return "No explanation provided"
    
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
                # Keep raw score - _normalize_score will handle range conversion
        
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
            # Keep percentage in 0-100 range to match thresholds in CSV
            # If LLM returns 0-1 range, convert to 0-100
            if score <= 1.0:
                score = score * 100
            return max(0.0, min(100.0, score))
        
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
                    'threshold': metric.threshold,
                    'status': result['status'],
                    'explanation': result['explanation'],
                    'prompt': prompt[:100] + "..." if len(prompt) > 100 else prompt,
                    'response': response[:100] + "..." if len(response) > 100 else response
                })
        
        print(f"\n✅ Evaluation complete!")
        return pd.DataFrame(results)

print("✅ LLM Judge Evaluator defined with BULLETPROOF JSON parsing")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 7: Run Evaluation

# COMMAND ----------

def auto_generate_evaluation_prompt(metric_name: str, metric_type: str, description: str, grading_rubric: str) -> str:
    """
    Auto-generate evaluation prompt from grading rubric.
    PM just provides grading rubric, code handles the rest!
    """
    
    # Add grading rubric section
    rubric_section = f"\n**Grading Rubric:**\n{grading_rubric}\n" if grading_rubric else ""
    
    # Build complete evaluation prompt
    prompt = f"""You are an expert evaluator. Your task: {description}

{rubric_section}
**Evaluation Details:**
- User Query: {{prompt}}
- AI Response: {{response}}
- Ground Truth Reference: {{ground_truth}}

**Instructions:**
Carefully evaluate the AI response using the grading rubric above.

**Required Output Format:**
Return ONLY a valid JSON object with these two fields:
{{
  "score": <your_score>,
  "explanation": "Brief explanation of your score"
}}

Do not include any other text outside the JSON object."""
    
    return prompt

def load_metrics_from_csv():
    """Load metrics from CSV and auto-generate evaluation prompts."""
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
        
        # Check if using new format (grading_rubric) or old format (evaluation_prompt)
        if 'grading_rubric' in row and pd.notna(row.get('grading_rubric')):
            # NEW FORMAT: Auto-generate evaluation prompt from grading rubric
            grading_rubric = str(row['grading_rubric']).strip()
            prompt_template = auto_generate_evaluation_prompt(
                metric_name=row['name'].strip(),
                metric_type=metric_type_str,
                description=row.get('description', '').strip(),
                grading_rubric=grading_rubric
            )
            print(f"✅ {row['name'].strip()} - Auto-generated prompt from grading rubric")
        elif 'evaluation_prompt' in row and pd.notna(row.get('evaluation_prompt')):
            # OLD FORMAT: Use evaluation_prompt directly (backward compatibility)
            prompt_template = row['evaluation_prompt'].strip()
            print(f"✅ {row['name'].strip()} - Using provided evaluation_prompt")
        else:
            # Fallback: Generate basic prompt from description
            prompt_template = auto_generate_evaluation_prompt(
                metric_name=row['name'].strip(),
                metric_type=metric_type_str,
                description=row.get('description', '').strip(),
                grading_rubric=""
            )
            print(f"⚠️ {row['name'].strip()} - No rubric or prompt provided, using basic prompt")
        
        # Ground truth file matching (PM provides filename, code matches to uploaded files)
        gt_file_value = row.get('ground_truth_file_path', '').strip()
        
        metric_config = MetricConfig(
            name=row['name'].strip(),
            metric_type=metric_type,
            description=row.get('description', '').strip(),
            prompt_template=prompt_template,
            threshold=float(row['threshold']),
            ground_truth_column=row['ground_truth_column'].strip(),
            ground_truth_file_path=gt_file_value
        )
        
        # Show which GT file this metric will use
        if gt_file_value:
            gt_filename = os.path.basename(gt_file_value)
            print(f"   📚 Ground truth: {gt_filename} → column '{row['ground_truth_column'].strip()}'")
        
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
# MAGIC - ✅ BULLETPROOF JSON parsing that works with ANY custom metric name
# MAGIC - ✅ Smart key detection handles all naming conventions
# MAGIC - ✅ Databricks + OpenAI model support
# MAGIC - ✅ Multiple ground truth files per metric
# MAGIC - ✅ MLflow experiment tracking
# MAGIC - ✅ CSV export functionality
# MAGIC - ✅ Interactive dashboard
# MAGIC
# MAGIC **Key Innovation:**
# MAGIC The system now uses intelligent score extraction that:
# MAGIC 1. Tries standard keys (score, value, rating)
# MAGIC 2. Tries exact metric name
# MAGIC 3. Handles metric names with/without common suffixes (_score, _rating, etc.)
# MAGIC 4. Does case-insensitive search
# MAGIC 5. Finds any numeric value as last resort
# MAGIC
# MAGIC This means it works with ANY custom metric naming convention!
