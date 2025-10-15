# How to Fix Your Cell 7 Issue

## Problem
You're still using the OLD Cell 7 code with broken escaping. That's why you see:
```
🔧 Escaped pattern: "accuracy_check_score" -> __PLACEHOLDER_0__
⚠️ Still getting KeyError after escaping: '__PLACEHOLDER_0__'
```

## Solution - 3 Steps

### Step 1: Delete Current Cell 7
1. Go to **Cell 7** in your Databricks notebook
2. **Select ALL the code** in Cell 7 (Ctrl+A)
3. **Delete it** (Delete key)

### Step 2: Copy New Cell 7
1. Copy the **ENTIRE code** from `COMPLETE_CELL_7_FOR_DATABRICKS.py`
2. **Paste it** into Cell 7
3. Make sure you got ALL 553 lines!

### Step 3: Re-run Cells
1. **Run Cell 7** - You should see:
   ```
   ✅ LLM Judge Evaluator class defined (cleaned version with proper escaping)
   ```
2. **Run Cell 9** - Now it should work!

## How to Verify It's Working

After running Cell 7, you should see this message at the end:
```
✅ LLM Judge Evaluator class defined (cleaned version with proper escaping)
```

When you run Cell 9, you should NOT see these error messages anymore:
- ❌ `🔧 Escaped pattern: "accuracy_check_score" -> __PLACEHOLDER_0__`
- ❌ `⚠️ Still getting KeyError after escaping`
- ❌ `🔧 Used string replacement as fallback`

Instead, you should see:
- ✅ `📝 Evaluation prompt preview: ...`
- ✅ `🤖 LLM response preview: ...`
- ✅ `✅ Successfully parsed JSON response`

## Why This Happened

The OLD Cell 7 had this broken escaping:
```python
# OLD (doesn't work):
metric_score_placeholder = f"{{{metric.name}_score}}"
safe_prompt_template = metric.prompt_template.replace(
    metric_score_placeholder, 
    f"{{{{{metric.name}_score}}}}"
)
```

The NEW Cell 7 has this working escaping:
```python
# NEW (works!):
def _escape_prompt_template(self, template: str) -> str:
    actual_placeholders = {
        '{prompt}': '<<<PROMPT_PLACEHOLDER>>>',
        '{response}': '<<<RESPONSE_PLACEHOLDER>>>',
        '{ground_truth}': '<<<GROUND_TRUTH_PLACEHOLDER>>>'
    }
    
    escaped_template = template
    for placeholder, marker in actual_placeholders.items():
        escaped_template = escaped_template.replace(placeholder, marker)
    
    escaped_template = escaped_template.replace('{', '{{').replace('}', '}}')
    
    for placeholder, marker in actual_placeholders.items():
        escaped_template = escaped_template.replace(marker, placeholder)
    
    return escaped_template
```

## Quick Check

After replacing Cell 7, check if this method exists:
- Search for `_escape_prompt_template` in Cell 7
- It should be on line ~272-307

If you can't find it, you didn't copy the new version!
