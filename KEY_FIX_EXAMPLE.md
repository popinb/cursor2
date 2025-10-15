# The Key Fix: Prompt Template Escaping

## ❌ The Problem

Your prompt templates contain JSON examples that look like this:

```python
evaluation_prompt = """
Evaluate the accuracy of the response.

Prompt: {prompt}
Response: {response}
Ground Truth: {ground_truth}

Return JSON like this:
{
  "accuracy_score": 1,
  "explanation": "Correct answer"
}
"""
```

When you call `.format()` on this template:
```python
eval_prompt = evaluation_prompt.format(
    prompt="What is 2+2?",
    response="4",
    ground_truth="4"
)
```

Python sees `{accuracy_score}` and `{explanation}` as format placeholders and throws:
```
KeyError: 'accuracy_score'
```

## ✅ The Solution

### Old Approach (Didn't Work)
```python
# Only escaped specific metric names - missed other JSON keys
metric_score_placeholder = f"{{{metric.name}_score}}"
if metric_score_placeholder in safe_prompt_template:
    safe_prompt_template = safe_prompt_template.replace(
        metric_score_placeholder, 
        f"{{{{{metric.name}_score}}}}"  # Double braces
    )
```

**Problems:**
- Only escapes `{metric_name_score}`
- Doesn't escape `{explanation}` or other JSON keys
- Fragile and hard to maintain

### New Approach (Works!)
```python
def _escape_prompt_template(self, template: str) -> str:
    """
    Protect actual placeholders, escape everything else.
    """
    # Step 1: Mark the real placeholders we want to keep
    actual_placeholders = {
        '{prompt}': '<<<PROMPT_PLACEHOLDER>>>',
        '{response}': '<<<RESPONSE_PLACEHOLDER>>>',
        '{ground_truth}': '<<<GROUND_TRUTH_PLACEHOLDER>>>'
    }
    
    escaped_template = template
    for placeholder, marker in actual_placeholders.items():
        escaped_template = escaped_template.replace(placeholder, marker)
    
    # Step 2: Escape ALL remaining curly braces
    # This makes JSON examples safe: { becomes {{, } becomes }}
    escaped_template = escaped_template.replace('{', '{{').replace('}', '}}')
    
    # Step 3: Restore the real placeholders
    for placeholder, marker in actual_placeholders.items():
        escaped_template = escaped_template.replace(marker, placeholder)
    
    return escaped_template
```

## 🎬 Example Transformation

**Input Template:**
```
Prompt: {prompt}
Response: {response}
Ground Truth: {ground_truth}

Return JSON:
{
  "accuracy_score": 1,
  "explanation": "Correct"
}
```

**After `_escape_prompt_template()`:**
```
Prompt: {prompt}
Response: {response}
Ground Truth: {ground_truth}

Return JSON:
{{
  "accuracy_score": 1,
  "explanation": "Correct"
}}
```

**After `.format(prompt="Q", response="A", ground_truth="A")`:**
```
Prompt: Q
Response: A
Ground Truth: A

Return JSON:
{
  "accuracy_score": 1,
  "explanation": "Correct"
}
```

✅ No KeyError!  
✅ JSON example preserved correctly!  
✅ All placeholders filled!

## 📊 Visual Flow

```
Original Template
    ↓
Step 1: Replace {prompt} → <<<PROMPT_PLACEHOLDER>>>
        Replace {response} → <<<RESPONSE_PLACEHOLDER>>>
        Replace {ground_truth} → <<<GROUND_TRUTH_PLACEHOLDER>>>
    ↓
Step 2: Replace { → {{
        Replace } → }}
    ↓
Step 3: Replace <<<PROMPT_PLACEHOLDER>>> → {prompt}
        Replace <<<RESPONSE_PLACEHOLDER>>> → {response}
        Replace <<<GROUND_TRUTH_PLACEHOLDER>>> → {ground_truth}
    ↓
Safe Template Ready for .format()
```

## 🧪 Test Cases

### Test 1: Simple JSON Example
```python
template = "Evaluate {response}. Return: {\"score\": 1}"
escaped = _escape_prompt_template(template)
# Result: "Evaluate {response}. Return: {{\"score\": 1}}"
result = escaped.format(response="Good")
# Result: "Evaluate Good. Return: {\"score\": 1}"
✅ Works!
```

### Test 2: Complex JSON Example
```python
template = """
{prompt} → {response}
Example: {"key1": "val1", "key2": {"nested": "val2"}}
"""
escaped = _escape_prompt_template(template)
result = escaped.format(prompt="Q", response="A")
# Result includes properly formatted JSON example
✅ Works!
```

### Test 3: Multiple Placeholders
```python
template = "{prompt} {response} {ground_truth} {\"example\": true}"
escaped = _escape_prompt_template(template)
result = escaped.format(prompt="P", response="R", ground_truth="GT")
# Result: "P R GT {\"example\": true}"
✅ Works!
```

## 💡 Why This Approach Is Better

| Old Approach | New Approach |
|-------------|--------------|
| Escapes only specific keys | Escapes ALL non-placeholder braces |
| Must know all JSON keys in advance | Works with any JSON example |
| Fragile - breaks with new keys | Robust - handles unknown keys |
| Hard to maintain | Simple and clear |
| Partial solution | Complete solution |

## 🎯 Bottom Line

**Before:** Had to carefully avoid JSON examples in prompts  
**After:** Can use any JSON examples freely!

This is the fundamental fix that solves your format string issue once and for all.
