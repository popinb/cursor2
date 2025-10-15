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
