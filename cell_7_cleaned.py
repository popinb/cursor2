# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 7: LLM Calling and Evaluation Methods
# MAGIC **Core evaluation logic - no changes needed**

# COMMAND ----------

# =============================================================================
# LLM JUDGE EVALUATOR CLASS - CLEANED VERSION WITH PROPER ESCAPING
# =============================================================================

import json
import time
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

class MetricType(Enum):
    BINARY = "binary"
    SCALE_1_5 = "1-5_scale"
    PERCENTAGE = "percentage"

@dataclass
class MetricConfig:
    name: str
    metric_type: MetricType
    description: str
    prompt_template: str
    threshold: float
    ground_truth_column: str
    ground_truth_file_path: str

class LLMJudgeEvaluator:
    def __init__(self, judge_model: str, metrics: List[MetricConfig], ground_truth_data: Dict[str, pd.DataFrame] = None):
        self.judge_model = judge_model
        self.metrics = metrics
        self.ground_truth_data = ground_truth_data or {}
        
        # Use the same logic as Cell 3 for model detection
        self.is_databricks_llm = self._is_databricks_model(judge_model)
        
        print(f"🔍 Model detection: {judge_model} -> Databricks: {self.is_databricks_llm}")
        
        # Initialize LLM client based on model type
        if self.is_databricks_llm:
            self._init_databricks_llm()
        else:
            self._init_openai_llm()
    
    def _is_databricks_model(self, model: str) -> bool:
        """Check if the model is a Databricks LLM endpoint."""
        if model == "databricks-llm":
            return True
        
        databricks_patterns = [
            "databricks-llama", "databricks-mpt", "databricks-dolly",
            "databricks-", "llama-2", "mpt-", "dolly-"
        ]
        
        for pattern in databricks_patterns:
            if pattern in model.lower():
                return True
        
        return False
    
    def _init_databricks_llm(self):
        """Initialize Databricks LLM client."""
        try:
            print("🔧 Initializing Databricks LLM client...")
            
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
                
                print(f"   ✅ Databricks workspace connection successful!")
                print(f"   Available serving endpoints: {len(available_models)}")
                if available_models:
                    print(f"   Models: {available_models[:3]}{'...' if len(available_models) > 3 else ''}")
                    self.databricks_endpoint, self.response_format = self._find_working_llm_endpoint(available_models)
                    print(f"   🎯 Selected endpoint: {self.databricks_endpoint}")
                else:
                    print("   ⚠️ No serving endpoints found - will use default endpoint")
                    self.databricks_endpoint = "default"
                    self.response_format = "openai"
            else:
                print(f"   ⚠️ Could not list endpoints (status {response.status_code})")
                self.databricks_endpoint = "default"
                self.response_format = "openai"
                
        except Exception as e:
            print(f"   ⚠️ Databricks connection test failed: {e}")
            self.databricks_endpoint = "default"
            self.response_format = "openai"
    
    def _find_working_llm_endpoint(self, available_models):
        """Find working general LLM endpoints in Databricks workspace."""
        print("🔍 Looking for working LLM endpoints...")
        
        # Priority order: Claude Sonnet > Claude Opus > Llama 405B > Llama 70B > Others
        priority_patterns = [
            'claude-sonnet', 'claude-opus', 'llama*405b', 'llama*70b', 
            'llama*8b', 'gemma', 'dbrx'
        ]
        
        for pattern in priority_patterns:
            pattern_clean = pattern.replace('*', '')
            for endpoint_name in available_models:
                if pattern_clean in endpoint_name.lower():
                    print(f"   ✅ Found endpoint: {endpoint_name}")
                    return endpoint_name, 'openai'
        
        # Skip known non-LLM endpoints
        for endpoint_name in available_models:
            if any(skip in endpoint_name.lower() for skip in ['agent', 'embedding', 'bge', 'gte']):
                continue
            print(f"   🔄 Using endpoint: {endpoint_name}")
            return endpoint_name, 'openai'
        
        if available_models:
            print(f"   🔄 Using first available endpoint: {available_models[0]}")
            return available_models[0], 'openai'
        
        raise Exception("No suitable LLM endpoints found")
    
    def _init_openai_llm(self):
        """Initialize OpenAI LLM client using variables from Cell 3."""
        try:
            import openai
            
            if 'client' in globals() and client is not None:
                self.llm_client = client
                print(f"✅ OpenAI client initialized using Cell 3 client")
            elif 'OPENAI_KEY' in globals() and OPENAI_KEY:
                self.llm_client = openai.OpenAI(api_key=OPENAI_KEY)
                print(f"✅ OpenAI client initialized with OPENAI_KEY")
            else:
                env_key = os.getenv('OPENAI_API_KEY')
                if env_key:
                    self.llm_client = openai.OpenAI(api_key=env_key)
                    print(f"✅ OpenAI client initialized with environment API key")
                else:
                    self.llm_client = openai.OpenAI()
                    print(f"✅ OpenAI client initialized with default key")
        except ImportError:
            raise ImportError("OpenAI library not available. Please install: pip install openai")
    
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
                else:
                    print(f"Unexpected response format: {result}")
                    return ""
            else:
                print(f"Databricks API error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            print(f"Error calling Databricks LLM: {e}")
            return ""
    
    def _call_openai_llm(self, prompt: str) -> str:
        """Call OpenAI LLM endpoint."""
        try:
            model_to_use = self.judge_model
            
            # Handle GPT-5 variants that use max_completion_tokens
            if "gpt-5" in model_to_use.lower() or model_to_use in ["gpt-5-chat-latest"]:
                response = self.llm_client.chat.completions.create(
                    model=model_to_use,
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=1000,
                    temperature=0.1
                )
            else:
                response = self.llm_client.chat.completions.create(
                    model=model_to_use,
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
            # Parse multiple files from the ground_truth_file_path
            files = []
            if ';' in metric.ground_truth_file_path:
                files = [f.strip() for f in metric.ground_truth_file_path.split(';') if f.strip()]
            elif ',' in metric.ground_truth_file_path:
                files = [f.strip() for f in metric.ground_truth_file_path.split(',') if f.strip()]
            else:
                files = [metric.ground_truth_file_path.strip()]
            
            if not files or not files[0]:
                return "Not provided"
            
            print(f"   🔍 Looking for {metric.ground_truth_column} in {len(files)} files: {files}")
            
            for file_path in files:
                filename = os.path.basename(file_path)
                if filename in self.ground_truth_data:
                    df = self.ground_truth_data[filename]
                    if metric.ground_truth_column in df.columns:
                        if sample_idx < len(df):
                            ground_truth = df[metric.ground_truth_column].iloc[sample_idx]
                            print(f"   ✅ Found {metric.ground_truth_column} in {filename}: {ground_truth}")
                            return str(ground_truth) if pd.notna(ground_truth) else "Not provided"
                        else:
                            print(f"   ⚠️ Sample index {sample_idx} out of range for {filename}")
                    else:
                        print(f"   ⚠️ Column {metric.ground_truth_column} not found in {filename}")
                else:
                    print(f"   ⚠️ File {filename} not loaded in ground_truth_data")
            
            return "Not provided"
            
        except Exception as e:
            print(f"   ❌ Error getting ground truth: {e}")
            return "Not provided"
    
    def _escape_prompt_template(self, template: str) -> str:
        """
        Properly escape prompt template to handle JSON examples with curly braces.
        
        Strategy:
        1. Identify and temporarily replace actual placeholders ({prompt}, {response}, {ground_truth})
        2. Escape all remaining curly braces by doubling them
        3. Restore the actual placeholders
        """
        # Define actual format placeholders we want to keep
        actual_placeholders = {
            '{prompt}': '<<<PROMPT_PLACEHOLDER>>>',
            '{response}': '<<<RESPONSE_PLACEHOLDER>>>',
            '{ground_truth}': '<<<GROUND_TRUTH_PLACEHOLDER>>>'
        }
        
        # Step 1: Replace actual placeholders with temporary markers
        escaped_template = template
        for placeholder, marker in actual_placeholders.items():
            escaped_template = escaped_template.replace(placeholder, marker)
        
        # Step 2: Escape all remaining curly braces by doubling them
        # This protects JSON examples like {"key": "value"} from being interpreted
        escaped_template = escaped_template.replace('{', '{{').replace('}', '}}')
        
        # Step 3: Restore actual placeholders
        for placeholder, marker in actual_placeholders.items():
            escaped_template = escaped_template.replace(marker, placeholder)
        
        return escaped_template
    
    def evaluate_single(self, prompt: str, response: str, ground_truth_data: dict, metric: MetricConfig, sample_idx: int = 0) -> dict:
        """Evaluate a single sample with one metric."""
        try:
            # Get the specific ground truth for this metric
            ground_truth = self._get_ground_truth_for_metric(metric, sample_idx)
            
            # Properly escape the prompt template
            safe_template = self._escape_prompt_template(metric.prompt_template)
            
            # Format the evaluation prompt with actual values
            eval_prompt = safe_template.format(
                prompt=prompt,
                response=response,
                ground_truth=ground_truth if ground_truth else "Not provided"
            )
            
            print(f"   📝 Evaluation prompt preview: {eval_prompt[:200]}...")
            
            # Route to appropriate LLM
            if self.is_databricks_llm:
                llm_response = self._call_databricks_llm(eval_prompt)
            else:
                llm_response = self._call_openai_llm(eval_prompt)
            
            print(f"   🤖 LLM response preview: {llm_response[:200]}...")
            
            # Validate response
            if not llm_response or str(llm_response).strip() == "":
                return {
                    "score": 0,
                    "explanation": "Empty response from LLM",
                    "status": "❌"
                }
            
            # Parse the LLM response
            score, explanation = self._parse_llm_response(llm_response, metric)
            
            # Determine pass/fail status
            status = "✅" if score >= metric.threshold else "❌"
            
            print(f"   ✅ Evaluation complete - score: {score}, status: {status}")
            
            return {
                "score": score,
                "explanation": explanation,
                "status": status
            }
            
        except Exception as e:
            print(f"   ❌ Error evaluating {metric.name}: {e}")
            import traceback
            traceback.print_exc()
            return {
                "score": 0,
                "explanation": f"Evaluation error: {str(e)}",
                "status": "❌"
            }
    
    def _parse_llm_response(self, llm_response: str, metric: MetricConfig) -> tuple:
        """
        Parse LLM response to extract score and explanation.
        
        Returns:
            tuple: (score, explanation)
        """
        content = str(llm_response).strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        # Try to parse as JSON first
        try:
            result_json = json.loads(content)
            print(f"   ✅ Successfully parsed JSON response")
            
            # Extract score with flexible key matching
            score = self._extract_json_value(result_json, [
                "score", "Score", "value", "Value", "rating", "Rating",
                f"{metric.name}_score", f"{metric.name}Score"
            ], default=0)
            
            # Extract explanation with flexible key matching
            explanation = self._extract_json_value(result_json, [
                "explanation", "Explanation", "reason", "Reason",
                "comment", "Comment", "rationale", "Rationale", "justification"
            ], default="No explanation provided")
            
        except json.JSONDecodeError:
            print(f"   ⚠️ JSON parsing failed, using fallback extraction")
            score, explanation = self._fallback_parse(content, metric)
        
        # Ensure score is numeric and within valid range
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
        
        # Extract scores based on metric type
        if metric.metric_type == MetricType.BINARY:
            # Look for pass/fail indicators
            if any(word in content.lower() for word in ['pass', 'correct', 'accurate', 'yes', 'true', '1']):
                score = 1
            elif any(word in content.lower() for word in ['fail', 'incorrect', 'inaccurate', 'no', 'false', '0']):
                score = 0
        
        elif metric.metric_type == MetricType.SCALE_1_5:
            # Extract numbers between 1-5
            numbers = re.findall(r'\b[1-5]\b', content)
            if numbers:
                score = int(numbers[0])
        
        elif metric.metric_type == MetricType.PERCENTAGE:
            # Extract percentages
            percentages = re.findall(r'(\d+(?:\.\d+)?)[%]?', content)
            if percentages:
                score = float(percentages[0])
                if score > 1:  # Convert percentage to decimal
                    score = score / 100
        
        print(f"   🔄 Fallback parsing - score: {score}")
        return score, explanation
    
    def _normalize_score(self, score: Any, metric_type: MetricType) -> float:
        """Normalize score to ensure it's within valid range for the metric type."""
        # Convert to float
        try:
            score = float(score)
        except (ValueError, TypeError):
            return 0.0
        
        # Normalize based on metric type
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
        
        # Process each sample
        for idx, row in evaluation_data.iterrows():
            sample_id = row.get('sample_id', f'sample_{idx}')
            prompt = row.get('prompt', '')
            response = row.get('response', '')
            
            print(f"\n📝 Processing sample {idx + 1}/{len(evaluation_data)}: {sample_id}")
            
            # Evaluate with each metric
            for metric in self.metrics:
                print(f"   📊 Evaluating {metric.name}...")
                
                # Get ground truth data for this sample
                ground_truth_data = {}
                for col in evaluation_data.columns:
                    if col not in ['sample_id', 'prompt', 'response']:
                        ground_truth_data[col] = row.get(col, '')
                
                # Evaluate single metric
                result = self.evaluate_single(prompt, response, ground_truth_data, metric, idx)
                
                # Store result
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
        
        print(f"\n✅ Evaluation complete! Processed {len(results)} evaluations")
        return pd.DataFrame(results)

print("✅ LLM Judge Evaluator class defined (cleaned version)")
