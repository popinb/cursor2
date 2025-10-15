# 📊 **Updated Cell 9 and Cell 10**

## **Complete Visualization Suite for LLM Evaluation**

---

## 📋 **Quick Summary**

**Cell 9: MLflow Dashboard (7 visualizations)**
- Historical tracking across multiple runs
- Run-to-run heatmap comparison
- Metric evolution trends
- Model comparison
- Improvement tracking

**Cell 10: Current Run Analysis (8 visualizations)**
- Deep dive into latest evaluation
- Sample × metric heatmap
- Score distributions
- Correlation analysis
- Performance scorecards

**Total: 15 beautiful, scalable visualizations! 🎨**

---

## 🔥 **Cell 9: MLflow Dashboard**

### **What It Does:**
Tracks your evaluation experiments over time with 7 comprehensive visualizations that automatically scale to ANY number of custom metrics.

### **Key Features:**
- ✅ Run-to-Run Performance Heatmap (rows=runs, columns=metrics)
- ✅ Metric Evolution Timeline (trends over time)
- ✅ Latest vs Best Comparison (catch regressions)
- ✅ Model Comparison (if you test multiple models)
- ✅ Improvement Tracking (first run vs latest)
- ✅ Latest Run Summary (text statistics)
- ✅ Experiment Summary (overall metadata)

### **Code:**

```python
# Databricks notebook source
# MAGIC %md
# MAGIC ## Cell 9: MLflow Dashboard 📊🔥
# MAGIC **Beautiful visualizations tracking evaluations over time**

# COMMAND ----------

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import pandas as pd
import numpy as np
from datetime import datetime

# Get experiment
user_name = dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()
MLFLOW_EXPERIMENT_PATH = f"/Users/{user_name}/llm_evaluation_experiment"

print("🔍 Loading MLflow experiment data...\n")

exp = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_PATH)

if exp is None:
    print(f"❌ Experiment not found: {MLFLOW_EXPERIMENT_PATH}")
    print(f"💡 Run an evaluation first (Cell 7) to create the experiment.")
else:
    # Get all runs
    runs_df = mlflow.search_runs(
        experiment_ids=[exp.experiment_id],
        filter_string="attributes.status = 'FINISHED'",
        order_by=["attributes.start_time DESC"],
        max_results=100
    )
    
    num_runs = len(runs_df)
    print(f"✅ Found {num_runs} experiment run(s)\n")
    
    if num_runs == 0:
        print("💡 No completed runs yet. Run an evaluation first (Cell 7).")
    
    elif num_runs > 0:
        
        # Get metric columns dynamically (works with ANY custom metrics!)
        metric_mean_cols = [c for c in runs_df.columns if c.startswith("metrics.") and c.endswith("_mean")]
        metric_pass_cols = [c for c in runs_df.columns if c.startswith("metrics.") and c.endswith("_pass_rate")]
        
        # Extract metric names
        metric_names = [c.replace('metrics.', '').replace('_pass_rate', '') for c in metric_pass_cols]
        
        print(f"📊 Tracking {len(metric_names)} custom metrics:")
        for m in metric_names:
            print(f"   • {m}")
        print()
        
        # ============================================================
        # 1. LATEST RUN SUMMARY
        # ============================================================
        print("="*70)
        print("📈 LATEST RUN SUMMARY")
        print("="*70)
        
        latest = runs_df.iloc[0]
        
        print(f"\n🆔 Run ID: {latest['run_id'][:12]}...")
        print(f"🤖 Model: {latest.get('params.model', latest.get('params.judge_model', 'N/A'))}")
        print(f"📊 Samples: {latest.get('params.samples', latest.get('params.num_samples', 'N/A'))}")
        print(f"📅 Time: {latest['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Duration: {(latest['end_time'] - latest['start_time']).total_seconds():.1f}s")
        
        if 'metrics.pass_rate' in latest:
            print(f"\n🎯 Overall Pass Rate: {latest['metrics.pass_rate']:.1f}%")
        
        print(f"\n📊 Metric Performance:")
        for col in metric_pass_cols:
            metric_name = col.replace('metrics.', '').replace('_pass_rate', '')
            if pd.notna(latest[col]):
                pass_rate = latest[col]
                mean_col = f"metrics.{metric_name}_mean"
                mean_score = latest.get(mean_col, 0)
                
                # Status icon
                icon = "✅" if pass_rate >= 70 else "⚠️" if pass_rate >= 50 else "❌"
                print(f"   {icon} {metric_name:30s} - Pass: {pass_rate:5.1f}% | Avg: {mean_score:.2f}")
        
        print("\n" + "="*70 + "\n")
        
        # ============================================================
        # 2. RUN-TO-RUN COMPARISON HEATMAP
        # ============================================================
        if num_runs >= 2:
            print("🔥 Creating Run-to-Run Comparison Heatmap...\n")
            
            # Create matrix: rows = runs, columns = metrics
            heatmap_data = []
            run_labels = []
            
            for idx, row in runs_df.iterrows():
                run_id_short = row['run_id'][:8]
                run_time = row['start_time'].strftime('%m/%d %H:%M')
                run_label = f"{run_time}\n{run_id_short}"
                run_labels.append(run_label)
                
                # Get pass rates for this run
                pass_rates = []
                for metric in metric_names:
                    col = f"metrics.{metric}_pass_rate"
                    if col in row and pd.notna(row[col]):
                        pass_rates.append(row[col])
                    else:
                        pass_rates.append(0)
                
                heatmap_data.append(pass_rates)
            
            # Convert to numpy array
            heatmap_matrix = np.array(heatmap_data)
            
            # Create heatmap
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=heatmap_matrix,
                x=metric_names,
                y=run_labels,
                colorscale=[
                    [0.0, '#d73027'],   # Red
                    [0.25, '#fc8d59'],  # Orange
                    [0.5, '#fee090'],   # Yellow
                    [0.75, '#91cf60'],  # Light green
                    [1.0, '#1a9850']    # Dark green
                ],
                text=heatmap_matrix,
                texttemplate='%{text:.0f}%',
                textfont={"size": 10},
                colorbar=dict(title="Pass Rate %"),
                hoverongaps=False,
                hovertemplate='Run: %{y}<br>Metric: %{x}<br>Pass Rate: %{z:.1f}%<extra></extra>'
            ))
            
            fig_heatmap.update_layout(
                title={
                    'text': "🔥 Run-to-Run Performance Heatmap (All Custom Metrics)",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2c3e50'}
                },
                xaxis_title="Metrics",
                yaxis_title="Experiment Runs (Time & Run ID)",
                height=max(400, num_runs * 50),
                width=max(900, len(metric_names) * 120),
                xaxis={'tickangle': -45, 'side': 'bottom'},
                yaxis={'autorange': 'reversed'},  # Latest run at top
                font=dict(size=11)
            )
            
            displayHTML(pio.to_html(fig_heatmap, include_plotlyjs='cdn'))
        
        # ============================================================
        # 3. METRIC EVOLUTION OVER TIME
        # ============================================================
        if num_runs >= 2:
            print("📈 Creating Metric Evolution Timeline...\n")
            
            fig_evolution = go.Figure()
            
            for metric in metric_names:
                col = f"metrics.{metric}_pass_rate"
                if col in runs_df.columns:
                    # Sort by time for proper line chart
                    sorted_df = runs_df.sort_values('start_time')
                    
                    fig_evolution.add_trace(go.Scatter(
                        x=sorted_df['start_time'],
                        y=sorted_df[col],
                        mode='lines+markers',
                        name=metric,
                        line=dict(width=3),
                        marker=dict(size=10),
                        hovertemplate='<b>%{fullData.name}</b><br>Time: %{x}<br>Pass Rate: %{y:.1f}%<extra></extra>'
                    ))
            
            fig_evolution.update_layout(
                title={
                    'text': "📈 Metric Performance Evolution Over Time",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2c3e50'}
                },
                xaxis_title="Experiment Run Time",
                yaxis_title="Pass Rate (%)",
                height=600,
                hovermode='x unified',
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02
                ),
                font=dict(size=12)
            )
            
            # Add threshold lines
            fig_evolution.add_hline(y=70, line_dash="dash", line_color="green", 
                                   annotation_text="Good (70%)", annotation_position="right")
            fig_evolution.add_hline(y=50, line_dash="dash", line_color="orange", 
                                   annotation_text="Okay (50%)", annotation_position="right")
            
            displayHTML(pio.to_html(fig_evolution, include_plotlyjs='cdn'))
        
        # ============================================================
        # 4. METRIC PERFORMANCE COMPARISON (Latest vs Best)
        # ============================================================
        if num_runs >= 2:
            print("🏆 Creating Latest vs Best Performance Comparison...\n")
            
            # Get best run for each metric
            comparison_data = []
            
            for metric in metric_names:
                pass_col = f"metrics.{metric}_pass_rate"
                mean_col = f"metrics.{metric}_mean"
                
                if pass_col in runs_df.columns:
                    latest_pass = latest.get(pass_col, 0)
                    best_pass = runs_df[pass_col].max()
                    
                    latest_mean = latest.get(mean_col, 0)
                    best_mean = runs_df[mean_col].max()
                    
                    comparison_data.append({
                        'metric': metric,
                        'latest_pass': latest_pass,
                        'best_pass': best_pass,
                        'latest_mean': latest_mean,
                        'best_mean': best_mean
                    })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            # Create grouped bar chart
            fig_comparison = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Pass Rate: Latest vs Best', 'Average Score: Latest vs Best'),
                specs=[[{"type": "bar"}, {"type": "bar"}]]
            )
            
            # Pass rates
            fig_comparison.add_trace(
                go.Bar(
                    x=comparison_df['metric'],
                    y=comparison_df['latest_pass'],
                    name='Latest Run',
                    marker_color='#3498db',
                    text=comparison_df['latest_pass'].round(1),
                    texttemplate='%{text}%',
                    textposition='outside'
                ),
                row=1, col=1
            )
            
            fig_comparison.add_trace(
                go.Bar(
                    x=comparison_df['metric'],
                    y=comparison_df['best_pass'],
                    name='Best Ever',
                    marker_color='#2ecc71',
                    text=comparison_df['best_pass'].round(1),
                    texttemplate='%{text}%',
                    textposition='outside'
                ),
                row=1, col=1
            )
            
            # Average scores
            fig_comparison.add_trace(
                go.Bar(
                    x=comparison_df['metric'],
                    y=comparison_df['latest_mean'],
                    name='Latest Run',
                    marker_color='#3498db',
                    text=comparison_df['latest_mean'].round(2),
                    texttemplate='%{text}',
                    textposition='outside',
                    showlegend=False
                ),
                row=1, col=2
            )
            
            fig_comparison.add_trace(
                go.Bar(
                    x=comparison_df['metric'],
                    y=comparison_df['best_mean'],
                    name='Best Ever',
                    marker_color='#2ecc71',
                    text=comparison_df['best_mean'].round(2),
                    texttemplate='%{text}',
                    textposition='outside',
                    showlegend=False
                ),
                row=1, col=2
            )
            
            fig_comparison.update_layout(
                title={
                    'text': "🏆 Latest Run vs Historical Best Performance",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2c3e50'}
                },
                height=600,
                barmode='group',
                font=dict(size=11)
            )
            
            fig_comparison.update_xaxes(tickangle=-45, row=1, col=1)
            fig_comparison.update_xaxes(tickangle=-45, row=1, col=2)
            fig_comparison.update_yaxes(title_text="Pass Rate (%)", row=1, col=1)
            fig_comparison.update_yaxes(title_text="Average Score", row=1, col=2)
            
            displayHTML(pio.to_html(fig_comparison, include_plotlyjs='cdn'))
        
        # ============================================================
        # 5. MODEL COMPARISON (if multiple models used)
        # ============================================================
        if 'params.model' in runs_df.columns or 'params.judge_model' in runs_df.columns:
            model_col = 'params.model' if 'params.model' in runs_df.columns else 'params.judge_model'
            unique_models = runs_df[model_col].dropna().unique()
            
            if len(unique_models) > 1:
                print("🤖 Creating Model Comparison...\n")
                
                # Group by model and calculate average pass rates
                model_comparison = []
                
                for model in unique_models:
                    model_runs = runs_df[runs_df[model_col] == model]
                    
                    for metric in metric_names:
                        pass_col = f"metrics.{metric}_pass_rate"
                        if pass_col in model_runs.columns:
                            avg_pass = model_runs[pass_col].mean()
                            model_comparison.append({
                                'model': model,
                                'metric': metric,
                                'avg_pass_rate': avg_pass
                            })
                
                model_comp_df = pd.DataFrame(model_comparison)
                
                # Create grouped bar chart
                fig_models = go.Figure()
                
                for model in unique_models:
                    model_data = model_comp_df[model_comp_df['model'] == model]
                    
                    fig_models.add_trace(go.Bar(
                        x=model_data['metric'],
                        y=model_data['avg_pass_rate'],
                        name=model,
                        text=model_data['avg_pass_rate'].round(1),
                        texttemplate='%{text}%',
                        textposition='outside'
                    ))
                
                fig_models.update_layout(
                    title={
                        'text': "🤖 Model Comparison: Average Pass Rates",
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 18, 'color': '#2c3e50'}
                    },
                    xaxis_title="Metrics",
                    yaxis_title="Average Pass Rate (%)",
                    height=600,
                    barmode='group',
                    xaxis={'tickangle': -45},
                    font=dict(size=12)
                )
                
                displayHTML(pio.to_html(fig_models, include_plotlyjs='cdn'))
        
        # ============================================================
        # 6. IMPROVEMENT TRACKING
        # ============================================================
        if num_runs >= 3:
            print("📊 Creating Improvement Tracking Dashboard...\n")
            
            # Calculate improvement from first run to latest
            first_run = runs_df.iloc[-1]  # Oldest run
            latest_run = runs_df.iloc[0]  # Newest run
            
            improvements = []
            
            for metric in metric_names:
                pass_col = f"metrics.{metric}_pass_rate"
                
                if pass_col in runs_df.columns:
                    first_val = first_run.get(pass_col, 0)
                    latest_val = latest_run.get(pass_col, 0)
                    
                    improvement = latest_val - first_val
                    
                    improvements.append({
                        'metric': metric,
                        'first': first_val,
                        'latest': latest_val,
                        'improvement': improvement
                    })
            
            improve_df = pd.DataFrame(improvements).sort_values('improvement')
            
            # Create waterfall-style chart
            fig_improve = go.Figure()
            
            colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in improve_df['improvement']]
            
            fig_improve.add_trace(go.Bar(
                x=improve_df['metric'],
                y=improve_df['improvement'],
                marker_color=colors,
                text=improve_df['improvement'].round(1),
                texttemplate='%{text:+.1f}%',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>First: %{customdata[0]:.1f}%<br>Latest: %{customdata[1]:.1f}%<br>Change: %{y:+.1f}%<extra></extra>',
                customdata=improve_df[['first', 'latest']].values
            ))
            
            fig_improve.update_layout(
                title={
                    'text': f"📊 Improvement Tracking: First Run vs Latest ({num_runs} runs)",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2c3e50'}
                },
                xaxis_title="Metrics",
                yaxis_title="Change in Pass Rate (%)",
                height=600,
                xaxis={'tickangle': -45},
                font=dict(size=12)
            )
            
            # Add zero line
            fig_improve.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
            
            displayHTML(pio.to_html(fig_improve, include_plotlyjs='cdn'))
            
            # Print summary
            print("\n" + "="*70)
            print("📊 IMPROVEMENT SUMMARY")
            print("="*70)
            
            improved = improve_df[improve_df['improvement'] > 0]
            declined = improve_df[improve_df['improvement'] < 0]
            unchanged = improve_df[improve_df['improvement'] == 0]
            
            print(f"\n✅ Improved: {len(improved)} metrics")
            for _, row in improved.iterrows():
                print(f"   🔼 {row['metric']:30s} +{row['improvement']:5.1f}% ({row['first']:.1f}% → {row['latest']:.1f}%)")
            
            if len(declined) > 0:
                print(f"\n⚠️  Declined: {len(declined)} metrics")
                for _, row in declined.iterrows():
                    print(f"   🔽 {row['metric']:30s} {row['improvement']:5.1f}% ({row['first']:.1f}% → {row['latest']:.1f}%)")
            
            if len(unchanged) > 0:
                print(f"\n➡️  Unchanged: {len(unchanged)} metrics")
            
            print("\n" + "="*70 + "\n")
        
        # ============================================================
        # 7. SUMMARY STATISTICS TABLE
        # ============================================================
        print("="*70)
        print("📊 MLFLOW EXPERIMENT SUMMARY")
        print("="*70)
        
        print(f"\n🆔 Experiment: {exp.name}")
        print(f"📁 Experiment ID: {exp.experiment_id}")
        print(f"📊 Total Runs: {num_runs}")
        print(f"📅 First Run: {runs_df.iloc[-1]['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 Latest Run: {runs_df.iloc[0]['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Metrics Tracked: {len(metric_names)}")
        
        if 'metrics.pass_rate' in runs_df.columns:
            overall_best = runs_df['metrics.pass_rate'].max()
            overall_avg = runs_df['metrics.pass_rate'].mean()
            print(f"\n🏆 Best Overall Pass Rate: {overall_best:.1f}%")
            print(f"📊 Average Overall Pass Rate: {overall_avg:.1f}%")
        
        print("\n" + "="*70)
        print("✅ MLflow Dashboard Complete!")
        print("="*70)
```

---

## 🎨 **Cell 10: Current Run Analysis**

### **What It Does:**
Deep analysis of your current evaluation run with 8 beautiful visualizations that automatically scale to ANY number of custom metrics.

### **Key Features:**
- ✅ Sample × Metric Performance Heatmap
- ✅ Metric Performance Dashboard (pass rate + avg score)
- ✅ Score Distribution (Violin Plots)
- ✅ Sample Performance Scorecard (ranked bars)
- ✅ Metric Correlation Matrix
- ✅ Pass/Fail Breakdown (stacked bars)
- ✅ Metric Type Analysis (pie + bar charts)
- ✅ Summary Statistics (comprehensive text)

### **Code:**

```python
# Databricks notebook source
# MAGIC %md
# MAGIC ## Cell 10: Advanced Visualizations 📊🎨
# MAGIC **Beautiful, scalable charts for any number of metrics**

# COMMAND ----------

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

if 'results_df' not in globals() or results_df.empty:
    print("❌ No results available. Run evaluation first (Cell 7).")
else:
    print("🎨 Creating advanced visualizations...\n")
    
    # ============================================================
    # 1. HEATMAP: Sample vs Metric Performance
    # ============================================================
    print("📊 1. Creating Sample vs Metric Heatmap...")
    
    # Create pivot table for heatmap
    heatmap_data = results_df.pivot_table(
        values='score',
        index='sample_id',
        columns='metric_name',
        aggfunc='first'
    )
    
    # Create custom colorscale
    # Green for high scores, Yellow for medium, Red for low
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale=[
            [0.0, '#d73027'],   # Red for 0
            [0.25, '#fc8d59'],  # Orange
            [0.5, '#fee090'],   # Yellow
            [0.75, '#91cf60'],  # Light green
            [1.0, '#1a9850']    # Dark green for 1
        ],
        text=heatmap_data.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Score"),
        hoverongaps=False
    ))
    
    fig_heatmap.update_layout(
        title={
            'text': "🔥 Sample vs Metric Performance Heatmap",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        xaxis_title="Metrics",
        yaxis_title="Samples",
        height=max(400, len(heatmap_data) * 40),
        width=max(800, len(heatmap_data.columns) * 100),
        xaxis={'tickangle': -45},
        font=dict(size=12)
    )
    
    displayHTML(pio.to_html(fig_heatmap, include_plotlyjs='cdn'))
    
    # ============================================================
    # 2. METRIC PERFORMANCE OVERVIEW
    # ============================================================
    print("📊 2. Creating Metric Performance Overview...")
    
    # Calculate metrics
    metric_summary = results_df.groupby('metric_name').agg({
        'score': ['mean', 'std', 'min', 'max'],
        'status': lambda x: (x == '✅').sum() / len(x) * 100  # Pass rate
    }).round(2)
    
    metric_summary.columns = ['Mean Score', 'Std Dev', 'Min', 'Max', 'Pass Rate %']
    metric_summary = metric_summary.reset_index()
    
    # Create subplot with 2 charts
    fig_metrics = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Pass Rate by Metric', 'Average Score by Metric'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Pass rate chart
    fig_metrics.add_trace(
        go.Bar(
            x=metric_summary['metric_name'],
            y=metric_summary['Pass Rate %'],
            marker=dict(
                color=metric_summary['Pass Rate %'],
                colorscale='RdYlGn',
                showscale=False,
                line=dict(color='black', width=1)
            ),
            text=metric_summary['Pass Rate %'].round(1),
            texttemplate='%{text}%',
            textposition='outside',
            name='Pass Rate'
        ),
        row=1, col=1
    )
    
    # Average score chart
    fig_metrics.add_trace(
        go.Bar(
            x=metric_summary['metric_name'],
            y=metric_summary['Mean Score'],
            marker=dict(
                color=metric_summary['Mean Score'],
                colorscale='Viridis',
                showscale=False,
                line=dict(color='black', width=1)
            ),
            text=metric_summary['Mean Score'].round(2),
            texttemplate='%{text}',
            textposition='outside',
            name='Avg Score',
            error_y=dict(
                type='data',
                array=metric_summary['Std Dev'],
                visible=True,
                color='rgba(0,0,0,0.3)'
            )
        ),
        row=1, col=2
    )
    
    fig_metrics.update_layout(
        title={
            'text': "📈 Metric Performance Dashboard",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        height=500,
        showlegend=False,
        font=dict(size=11)
    )
    
    fig_metrics.update_xaxes(tickangle=-45, row=1, col=1)
    fig_metrics.update_xaxes(tickangle=-45, row=1, col=2)
    fig_metrics.update_yaxes(title_text="Pass Rate (%)", row=1, col=1)
    fig_metrics.update_yaxes(title_text="Average Score", row=1, col=2)
    
    displayHTML(pio.to_html(fig_metrics, include_plotlyjs='cdn'))
    
    # ============================================================
    # 3. SCORE DISTRIBUTION: Violin Plots
    # ============================================================
    print("📊 3. Creating Score Distribution Analysis...")
    
    fig_violin = go.Figure()
    
    for metric in results_df['metric_name'].unique():
        metric_data = results_df[results_df['metric_name'] == metric]
        
        fig_violin.add_trace(go.Violin(
            y=metric_data['score'],
            name=metric,
            box_visible=True,
            meanline_visible=True,
            fillcolor='rgba(0,100,200,0.3)',
            line_color='rgb(0,100,200)',
            opacity=0.7,
            points='all',
            jitter=0.3,
            pointpos=-0.5,
            hovertemplate='<b>%{fullData.name}</b><br>Score: %{y:.2f}<extra></extra>'
        ))
    
    fig_violin.update_layout(
        title={
            'text': "🎻 Score Distribution by Metric (Violin Plot)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        yaxis_title="Score",
        xaxis_title="Metric",
        height=600,
        showlegend=False,
        xaxis={'tickangle': -45},
        font=dict(size=12)
    )
    
    displayHTML(pio.to_html(fig_violin, include_plotlyjs='cdn'))
    
    # ============================================================
    # 4. SAMPLE PERFORMANCE SCORECARD
    # ============================================================
    print("📊 4. Creating Sample Performance Scorecard...")
    
    sample_summary = results_df.groupby('sample_id').agg({
        'score': 'mean',
        'status': lambda x: (x == '✅').sum() / len(x) * 100
    }).round(2)
    
    sample_summary.columns = ['Avg Score', 'Pass Rate %']
    sample_summary = sample_summary.reset_index()
    sample_summary = sample_summary.sort_values('Pass Rate %', ascending=True)
    
    fig_samples = go.Figure()
    
    # Add bars
    fig_samples.add_trace(go.Bar(
        y=sample_summary['sample_id'].astype(str),
        x=sample_summary['Pass Rate %'],
        orientation='h',
        marker=dict(
            color=sample_summary['Pass Rate %'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Pass Rate %"),
            line=dict(color='black', width=1)
        ),
        text=sample_summary['Pass Rate %'].round(1),
        texttemplate='%{text}%',
        textposition='outside',
        hovertemplate='<b>Sample %{y}</b><br>Pass Rate: %{x:.1f}%<br>Avg Score: %{customdata:.2f}<extra></extra>',
        customdata=sample_summary['Avg Score']
    ))
    
    fig_samples.update_layout(
        title={
            'text': "📋 Sample Performance Scorecard",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        xaxis_title="Pass Rate (%)",
        yaxis_title="Sample ID",
        height=max(400, len(sample_summary) * 40),
        showlegend=False,
        font=dict(size=12)
    )
    
    displayHTML(pio.to_html(fig_samples, include_plotlyjs='cdn'))
    
    # ============================================================
    # 5. METRIC CORRELATION HEATMAP
    # ============================================================
    print("📊 5. Creating Metric Correlation Heatmap...")
    
    # Calculate correlation between metrics
    correlation_data = heatmap_data.corr()
    
    fig_corr = go.Figure(data=go.Heatmap(
        z=correlation_data.values,
        x=correlation_data.columns,
        y=correlation_data.columns,
        colorscale='RdBu',
        zmid=0,
        text=correlation_data.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation"),
        hoverongaps=False
    ))
    
    fig_corr.update_layout(
        title={
            'text': "🔗 Metric Correlation Matrix",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        xaxis_title="Metrics",
        yaxis_title="Metrics",
        height=max(500, len(correlation_data) * 50),
        width=max(700, len(correlation_data) * 50),
        xaxis={'tickangle': -45},
        font=dict(size=11)
    )
    
    displayHTML(pio.to_html(fig_corr, include_plotlyjs='cdn'))
    
    # ============================================================
    # 6. PASS/FAIL BREAKDOWN BY METRIC
    # ============================================================
    print("📊 6. Creating Pass/Fail Breakdown...")
    
    # Calculate pass/fail counts
    pass_fail = results_df.groupby(['metric_name', 'status']).size().unstack(fill_value=0)
    
    if '✅' not in pass_fail.columns:
        pass_fail['✅'] = 0
    if '❌' not in pass_fail.columns:
        pass_fail['❌'] = 0
    
    pass_fail = pass_fail.reset_index()
    
    fig_passfail = go.Figure()
    
    fig_passfail.add_trace(go.Bar(
        x=pass_fail['metric_name'],
        y=pass_fail['✅'],
        name='Pass ✅',
        marker_color='rgb(26,152,80)',
        text=pass_fail['✅'],
        textposition='inside',
        textfont=dict(color='white', size=12)
    ))
    
    fig_passfail.add_trace(go.Bar(
        x=pass_fail['metric_name'],
        y=pass_fail['❌'],
        name='Fail ❌',
        marker_color='rgb(215,48,39)',
        text=pass_fail['❌'],
        textposition='inside',
        textfont=dict(color='white', size=12)
    ))
    
    fig_passfail.update_layout(
        title={
            'text': "✅❌ Pass/Fail Breakdown by Metric",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        barmode='stack',
        xaxis_title="Metric",
        yaxis_title="Count",
        height=500,
        xaxis={'tickangle': -45},
        font=dict(size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    displayHTML(pio.to_html(fig_passfail, include_plotlyjs='cdn'))
    
    # ============================================================
    # 7. METRIC TYPE COMPARISON
    # ============================================================
    print("📊 7. Creating Metric Type Comparison...")
    
    type_summary = results_df.groupby('metric_type').agg({
        'score': 'mean',
        'status': lambda x: (x == '✅').sum() / len(x) * 100
    }).round(2)
    
    type_summary.columns = ['Avg Score', 'Pass Rate %']
    type_summary = type_summary.reset_index()
    
    fig_types = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "domain"}, {"type": "bar"}]],
        subplot_titles=('Evaluations by Metric Type', 'Pass Rate by Type')
    )
    
    # Pie chart
    type_counts = results_df['metric_type'].value_counts()
    fig_types.add_trace(
        go.Pie(
            labels=type_counts.index,
            values=type_counts.values,
            hole=0.4,
            marker=dict(colors=['#3498db', '#e74c3c', '#2ecc71']),
            textinfo='label+percent',
            textfont=dict(size=12)
        ),
        row=1, col=1
    )
    
    # Bar chart
    fig_types.add_trace(
        go.Bar(
            x=type_summary['metric_type'],
            y=type_summary['Pass Rate %'],
            marker=dict(
                color=type_summary['Pass Rate %'],
                colorscale='RdYlGn',
                showscale=False,
                line=dict(color='black', width=1)
            ),
            text=type_summary['Pass Rate %'].round(1),
            texttemplate='%{text}%',
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig_types.update_layout(
        title={
            'text': "📊 Metric Type Analysis",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        height=500,
        showlegend=False,
        font=dict(size=12)
    )
    
    fig_types.update_yaxes(title_text="Pass Rate (%)", row=1, col=2)
    
    displayHTML(pio.to_html(fig_types, include_plotlyjs='cdn'))
    
    # ============================================================
    # 8. SUMMARY STATISTICS TABLE
    # ============================================================
    print("📊 8. Creating Summary Statistics...")
    
    print("\n" + "="*80)
    print("📈 EVALUATION SUMMARY STATISTICS")
    print("="*80)
    
    total_evals = len(results_df)
    total_pass = (results_df['status'] == '✅').sum()
    total_fail = (results_df['status'] == '❌').sum()
    overall_pass_rate = (total_pass / total_evals * 100) if total_evals > 0 else 0
    
    print(f"\n🎯 Overall Performance:")
    print(f"   Total Evaluations: {total_evals}")
    print(f"   Passed: {total_pass} ({overall_pass_rate:.1f}%)")
    print(f"   Failed: {total_fail} ({100-overall_pass_rate:.1f}%)")
    print(f"   Average Score: {results_df['score'].mean():.2f}")
    print(f"   Score Std Dev: {results_df['score'].std():.2f}")
    
    print(f"\n📊 By Metric:")
    for metric in results_df['metric_name'].unique():
        metric_data = results_df[results_df['metric_name'] == metric]
        metric_pass = (metric_data['status'] == '✅').sum()
        metric_total = len(metric_data)
        metric_rate = (metric_pass / metric_total * 100) if metric_total > 0 else 0
        avg_score = metric_data['score'].mean()
        
        status_icon = "✅" if metric_rate >= 70 else "⚠️" if metric_rate >= 50 else "❌"
        print(f"   {status_icon} {metric:30s} - Pass: {metric_pass}/{metric_total} ({metric_rate:5.1f}%) | Avg: {avg_score:.2f}")
    
    print(f"\n📋 By Sample:")
    for sample in sorted(results_df['sample_id'].unique()):
        sample_data = results_df[results_df['sample_id'] == sample]
        sample_pass = (sample_data['status'] == '✅').sum()
        sample_total = len(sample_data)
        sample_rate = (sample_pass / sample_total * 100) if sample_total > 0 else 0
        
        status_icon = "✅" if sample_rate >= 70 else "⚠️" if sample_rate >= 50 else "❌"
        print(f"   {status_icon} Sample {sample:10s} - Pass: {sample_pass}/{sample_total} ({sample_rate:5.1f}%)")
    
    print("\n" + "="*80)
    print("✅ All visualizations generated successfully!")
    print("="*80)
```

---

## ✅ **Done!**

**You now have:**
- ✅ Cell 9 with 7 MLflow visualizations (historical tracking)
- ✅ Cell 10 with 8 current run visualizations (deep analysis)
- ✅ Total: 15 beautiful, scalable charts!
- ✅ Works with ANY number of custom metrics (2-50+)
- ✅ Automatically adjusts chart sizes
- ✅ Zero configuration needed

**Just copy Cell 9 and Cell 10 code into your notebook and run!** 📊🔥🚀
