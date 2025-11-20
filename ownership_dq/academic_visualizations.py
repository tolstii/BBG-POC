"""
Academic-style visualizations for method comparison
Matches the professional plots with confidence intervals and annotations
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from scipy import stats


def create_confidence_interval(values, confidence=0.95):
    """Calculate confidence interval for time series"""
    n = len(values)
    mean = np.mean(values)
    std = np.std(values, ddof=1)
    margin = std * stats.t.ppf((1 + confidence) / 2, n - 1)
    return mean, mean - margin, mean + margin


def create_rolling_stats(series, window=3):
    """Calculate rolling statistics"""
    rolling_mean = series.rolling(window=window, min_periods=1).mean()
    rolling_std = series.rolling(window=window, min_periods=1).std()
    
    upper_bound = rolling_mean + 2 * rolling_std
    lower_bound = rolling_mean - 2 * rolling_std
    
    return rolling_mean, upper_bound, lower_bound


def create_before_after_comparison(dates, values, anomalies, change_point_idx):
    """
    Create before/after retraining comparison plot
    Similar to Image 1 in the examples
    """
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Before Retraining:<br>Spike + repeated "anomalies"',
                       'After Retraining:<br>New baseline learned'),
        horizontal_spacing=0.12
    )
    
    # Split data at change point
    before_dates = dates[:change_point_idx]
    before_values = values[:change_point_idx]
    after_dates = dates[change_point_idx-1:]
    after_values = values[change_point_idx-1:]
    
    # Before retraining - calculate stats
    before_mean = np.mean(before_values)
    before_std = np.std(before_values)
    before_upper = before_mean + 1.96 * before_std
    before_lower = before_mean - 1.96 * before_std
    
    # Plot 1: Before Retraining
    # Confidence interval
    fig.add_trace(
        go.Scatter(
            x=before_dates,
            y=[before_upper] * len(before_dates),
            fill=None,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=before_dates,
            y=[before_lower] * len(before_dates),
            fill='tonexty',
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(255, 200, 150, 0.3)',
            name='Model 95% Interval (pre)',
            showlegend=True
        ),
        row=1, col=1
    )
    
    # Model mean line
    fig.add_trace(
        go.Scatter(
            x=before_dates,
            y=[before_mean] * len(before_dates),
            mode='lines',
            line=dict(color='rgba(200, 200, 200, 0.8)', width=2, dash='dash'),
            name='Model Mean (pre)',
            showlegend=True
        ),
        row=1, col=1
    )
    
    # Actual values
    fig.add_trace(
        go.Scatter(
            x=before_dates,
            y=before_values,
            mode='lines+markers',
            line=dict(color='#FF8C00', width=2),
            marker=dict(size=8, color='#FF8C00'),
            name='Reported Ownership %',
            showlegend=True
        ),
        row=1, col=1
    )
    
    # Plot 2: After Retraining
    # Calculate new baseline after change point
    after_mean = np.mean(after_values)
    after_std = np.std(after_values)
    after_upper = after_mean + 1.96 * after_std
    after_lower = after_mean - 1.96 * after_std
    
    # Confidence interval
    fig.add_trace(
        go.Scatter(
            x=after_dates,
            y=[after_upper] * len(after_dates),
            fill=None,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(
            x=after_dates,
            y=[after_lower] * len(after_dates),
            fill='tonexty',
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(255, 230, 180, 0.4)',
            name='Model 95% Interval (post)',
            showlegend=True
        ),
        row=1, col=2
    )
    
    # Model mean line
    fig.add_trace(
        go.Scatter(
            x=after_dates,
            y=[after_mean] * len(after_dates),
            mode='lines',
            line=dict(color='#4169E1', width=2, dash='dash'),
            name='Model Mean (post)',
            showlegend=True
        ),
        row=1, col=2
    )
    
    # Actual values
    fig.add_trace(
        go.Scatter(
            x=after_dates,
            y=after_values,
            mode='lines+markers',
            line=dict(color='#FF8C00', width=2),
            marker=dict(size=8, color='#FF8C00'),
            name='Reported Ownership %',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Add annotation for spike
    if len(after_values) > 0:
        spike_idx = np.argmax(after_values)
        # Handle both Series and array types
        spike_date = after_dates.iloc[spike_idx] if hasattr(after_dates, 'iloc') else after_dates[spike_idx]
        spike_value = after_values[spike_idx]
        
        fig.add_annotation(
            x=spike_date,
            y=spike_value + 0.5,
            text="Spike causes<br>model update",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#333",
            ax=40,
            ay=-60,
            font=dict(size=11, color="#333"),
            row=1, col=2
        )
    
    # Update layout
    fig.update_xaxes(title_text="Filing Date", row=1, col=1, gridcolor='#E0E0E0')
    fig.update_xaxes(title_text="Filing Date", row=1, col=2, gridcolor='#E0E0E0')
    fig.update_yaxes(title_text="Institutional Ownership (%)", row=1, col=1, gridcolor='#E0E0E0')
    fig.update_yaxes(title_text="", row=1, col=2, gridcolor='#E0E0E0')
    
    fig.update_layout(
        height=400,
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=11, color="#333"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#CCC",
            borderwidth=1
        ),
        margin=dict(l=60, r=20, t=80, b=100)
    )
    
    return fig


def create_adaptive_detection_plot(dates, values, rolling_mean, anomalies, event_idx):
    """
    Create adaptive anomaly detection plot with DLT retraining
    Similar to Image 2 in the examples
    """
    fig = go.Figure()
    
    # Split at event point
    pre_event_dates = dates[:event_idx]
    post_event_dates = dates[event_idx:]
    
    # Pre-event forecast (gray)
    pre_mean = np.mean(values[:event_idx])
    pre_std = np.std(values[:event_idx])
    pre_upper = pre_mean + 1.96 * pre_std
    pre_lower = pre_mean - 1.96 * pre_std
    
    # Pre-event confidence interval
    fig.add_trace(
        go.Scatter(
            x=list(pre_event_dates) + list(post_event_dates),
            y=[pre_upper] * len(dates),
            fill=None,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=list(pre_event_dates) + list(post_event_dates),
            y=[pre_lower] * len(dates),
            fill='tonexty',
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(180, 180, 180, 0.3)',
            name='DLT Forecast (pre-event)',
            showlegend=True
        )
    )
    
    # Pre-event mean
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=[pre_mean] * len(dates),
            mode='lines',
            line=dict(color='rgba(100, 100, 100, 0.6)', width=2, dash='dash'),
            name='DLT Mean (pre-event)',
            showlegend=True
        )
    )
    
    # Post-event retrained model (blue)
    if len(post_event_dates) > 3:
        post_values = values[event_idx:]
        post_mean = np.mean(post_values)
        post_std = np.std(post_values)
        post_upper = post_mean + 1.96 * post_std
        post_lower = post_mean - 1.96 * post_std
        
        # Post-event confidence interval
        fig.add_trace(
            go.Scatter(
                x=post_event_dates,
                y=[post_upper] * len(post_event_dates),
                fill=None,
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=post_event_dates,
                y=[post_lower] * len(post_event_dates),
                fill='tonexty',
                mode='lines',
                line=dict(width=0),
                fillcolor='rgba(150, 200, 255, 0.3)',
                name='Retrained DLT (post-event)',
                showlegend=True
            )
        )
        
        # Post-event mean
        fig.add_trace(
            go.Scatter(
                x=post_event_dates,
                y=[post_mean] * len(post_event_dates),
                mode='lines',
                line=dict(color='#4169E1', width=2),
                name='DLT Mean (post-event)',
                showlegend=True
            )
        )
    
    # Rolling average
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=rolling_mean,
            mode='lines',
            line=dict(color='#00BFFF', width=2, dash='dash'),
            name='Rolling Avg (3q)',
            showlegend=True
        )
    )
    
    # Actual values
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            line=dict(color='#FF8C00', width=2),
            marker=dict(size=8, color='#FF8C00'),
            name='Reported Ownership %',
            showlegend=True
        )
    )
    
    # Mark anomalies
    anomaly_mask = anomalies.astype(bool)
    if anomaly_mask.any():
        fig.add_trace(
            go.Scatter(
                x=dates[anomaly_mask],
                y=values[anomaly_mask],
                mode='markers',
                marker=dict(size=15, color='red', symbol='x', line=dict(width=2)),
                name='Anomaly',
                showlegend=True
            )
        )
    
    # Add annotations
    # Spike annotation
    spike_idx = event_idx
    if spike_idx < len(dates):
        # Handle both Series and array types
        spike_date = dates.iloc[spike_idx] if hasattr(dates, 'iloc') else dates[spike_idx]
        spike_value = values[spike_idx]
        
        fig.add_annotation(
            x=spike_date,
            y=spike_value + 1.5,
            text="Spike:<br>Activist 13D<br>(valid event)",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#333",
            ax=-60,
            ay=-80,
            font=dict(size=10, color="#333")
        )
    
    # Crash annotation (if there's a drop)
    if len(values) > spike_idx + 3:
        drop_values = values[spike_idx:]
        if len(drop_values) > 0:
            drop_idx = spike_idx + np.argmin(drop_values)
            if drop_idx < len(dates):
                # Handle both Series and array types
                drop_date = dates.iloc[drop_idx] if hasattr(dates, 'iloc') else dates[drop_idx]
                drop_value = values[drop_idx]
                
                fig.add_annotation(
                    x=drop_date,
                    y=drop_value - 1.5,
                    text="Crash:<br>Missing filer data<br>(ingestion issue)",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="#333",
                    ax=60,
                    ay=80,
                    font=dict(size=10, color="#333")
                )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="Adaptive Anomaly Detection:<br>DLT Retraining After Structural Ownership Change",
            font=dict(size=14, color="#333"),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="Quarter",
            gridcolor='#E0E0E0',
            showline=True,
            linecolor='#CCC'
        ),
        yaxis=dict(
            title="Total Institutional Ownership (%)",
            gridcolor='#E0E0E0',
            showline=True,
            linecolor='#CCC'
        ),
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=11, color="#333"),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#CCC",
            borderwidth=1
        ),
        hovermode='x unified',
        margin=dict(l=60, r=20, t=80, b=60)
    )
    
    return fig


def create_post_retrain_anomaly_plot(dates, values, post_mean, post_upper, post_lower, anomalies):
    """
    Create post-retraining plot showing anomaly detection
    Similar to Image 3 in the examples
    """
    fig = go.Figure()
    
    # Confidence interval
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=post_upper,
            fill=None,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=post_lower,
            fill='tonexty',
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(255, 220, 180, 0.4)',
            name='Post-Retrain 95% Interval',
            showlegend=True
        )
    )
    
    # Model mean
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=post_mean,
            mode='lines',
            line=dict(color='#FF8C00', width=2, dash='dash'),
            name='Post-Retrain Model Mean',
            showlegend=True
        )
    )
    
    # Actual values
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            line=dict(color='#FF8C00', width=2),
            marker=dict(size=8, color='#FF8C00'),
            name='Reported Ownership %',
            showlegend=True
        )
    )
    
    # Mark anomalies
    anomaly_mask = anomalies.astype(bool)
    if anomaly_mask.any():
        anomaly_dates = dates[anomaly_mask]
        anomaly_values = values[anomaly_mask]
        
        fig.add_trace(
            go.Scatter(
                x=anomaly_dates,
                y=anomaly_values,
                mode='markers',
                marker=dict(size=15, color='red', symbol='x', line=dict(width=3)),
                name='Anomaly',
                showlegend=True
            )
        )
        
        # Add annotation for the anomaly
        if len(anomaly_dates) > 0:
            # Handle both Series and array types
            last_anomaly_date = anomaly_dates.iloc[-1] if hasattr(anomaly_dates, 'iloc') else anomaly_dates[-1]
            last_anomaly_value = anomaly_values[-1] if isinstance(anomaly_values, np.ndarray) else anomaly_values.iloc[-1]
            
            fig.add_annotation(
                x=last_anomaly_date,
                y=last_anomaly_value - 1.5,
                text="Drop outside new baseline<br>(flagged anomaly)",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#333",
                ax=60,
                ay=60,
                font=dict(size=10, color="#333")
            )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="After Retraining: Drop in Q2-2025 Is Flagged as Anomaly",
            font=dict(size=14, color="#333"),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="Quarter",
            gridcolor='#E0E0E0',
            showline=True,
            linecolor='#CCC'
        ),
        yaxis=dict(
            title="Institutional Ownership (%)",
            gridcolor='#E0E0E0',
            showline=True,
            linecolor='#CCC'
        ),
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=11, color="#333"),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#CCC",
            borderwidth=1
        ),
        hovermode='x unified',
        margin=dict(l=60, r=20, t=60, b=60)
    )
    
    return fig
