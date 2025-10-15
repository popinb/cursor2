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
