# How to Import the LLM Judge Evaluation System into Databricks

## 📥 **Import Instructions**

### **Option 1: Direct Import (Recommended)**

1. **Download the file:**
   - Download `LLM_Judge_Evaluation_System.py` to your computer

2. **Import into Databricks:**
   - Go to your Databricks workspace
   - Click on **Workspace** in the left sidebar
   - Navigate to your user folder (e.g., `/Users/your.email@company.com/`)
   - Click the **⋮** (three dots) menu
   - Select **Import**
   - Click **Browse** and select `LLM_Judge_Evaluation_System.py`
   - Click **Import**

3. **Open the notebook:**
   - The notebook will appear in your workspace
   - Click on it to open
   - You're ready to run!

### **Option 2: Import via URL**

If the file is hosted on GitHub or another URL:

1. Go to **Workspace** → **Import**
2. Select **URL** tab
3. Paste the URL to `LLM_Judge_Evaluation_System.py`
4. Click **Import**

### **Option 3: Using Databricks CLI**

```bash
databricks workspace import \
  --language PYTHON \
  --format SOURCE \
  ./LLM_Judge_Evaluation_System.py \
  /Users/your.email@company.com/LLM_Judge_Evaluation_System
```

---

## 🚀 **Quick Start Guide**

### **Before Running:**

1. **Upload your CSV files to Databricks:**
   - Evaluation data CSV
   - Metrics configuration CSV
   - Ground truth CSV files

2. **Update the widgets in Cell 2:**
   - Set `evaluation_data_path` to your evaluation CSV
   - Set `metrics_config_path` to your metrics CSV
   - Set `ground_truth_files` to your ground truth file paths (semicolon-separated)

3. **For OpenAI models:**
   - Make sure your OpenAI API key is stored in Databricks secrets:
     ```
     Scope: popin-secure-scope
     Key: openai_key
     ```
   - Update the `base_url` in Cell 3 if needed

### **Run Order:**

1. **Cell 1:** Install packages (run once, then restart Python)
2. **Cell 2:** Load data files
3. **Cell 3:** Configure model (Databricks or OpenAI)
4. **Cell 4:** Verify metrics loaded
5. **Cell 5:** Load core classes
6. **Cell 6:** Load evaluator logic
7. **Cell 7:** Run evaluation (this does the work!)
8. **Cell 8:** Export results to CSV
9. **Cell 9:** View MLflow dashboard

---

## 📊 **Required CSV Format**

### **Metrics Configuration CSV:**

```csv
name,type,description,evaluation_prompt,threshold,ground_truth_column,ground_truth_file_path
accuracy_check,binary,Checks accuracy,"Evaluate if the response contains accurate information...",1.0,correct_answer,ground_truth_accuracy.csv
helpfulness_rating,1-5_scale,Rate helpfulness,"Rate the helpfulness...",3.0,helpful_answer,ground_truth_accuracy.csv
safety_check,binary,Check safety,"Check if this response contains any harmful content...",1.0,safe_response,ground_truth_safety.csv
completeness_score,percentage,Evaluate completeness,"Evaluate the completeness...",0.7,complete_answer,ground_truth_safety.csv
```

### **Evaluation Data CSV:**

```csv
sample_id,prompt,response
1,What is the capital of France?,The capital of France is Paris.
2,Explain machine learning,Machine learning is AI that learns from data.
```

### **Ground Truth CSV:**

```csv
sample_id,correct_answer,helpful_answer
1,Paris is the capital of France,This response is clear and informative
2,Machine learning is a subset of AI,The explanation is simple and easy to understand
```

---

## 🎯 **Key Features**

✅ **Auto-discovery** of Databricks LLM endpoints  
✅ **OpenAI API** support (GPT-4o, GPT-4o-mini, etc.)  
✅ **Multiple metric types** (Binary, 1-5 Scale, Percentage)  
✅ **Multiple ground truth files** per metric  
✅ **Robust JSON parsing** with fallbacks  
✅ **MLflow tracking** for experiment management  
✅ **CSV export** for results  
✅ **Interactive dashboard** with visualizations  

---

## 🔧 **Troubleshooting**

### **File not found errors:**
- Make sure CSV files are uploaded to your Databricks workspace
- Use full paths like `/Workspace/Users/your.email@company.com/file.csv`

### **OpenAI connection issues:**
- Verify your API key is in Databricks secrets
- Check the `base_url` in Cell 3 matches your OpenAI endpoint

### **Databricks endpoint not found:**
- The system auto-discovers available endpoints
- Make sure you have access to Databricks Foundation Model APIs

### **Score extraction issues:**
- The system now checks for metric names directly (fixes `completeness_score` issue)
- Supports flexible JSON response formats

---

## 📞 **Support**

If you encounter issues:
1. Check the cell outputs for error messages
2. Verify all CSV files are properly formatted
3. Make sure you have the required permissions in Databricks
4. Check MLflow experiment logs for detailed information

---

**Happy Evaluating!** 🎉
