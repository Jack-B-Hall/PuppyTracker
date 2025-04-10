import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import timedelta

# 1. Daily potty events chart - FIXED COUNTING
def create_potty_charts(potty_events):
    plots = {}
    
    # Create dataframe from events
    potty_data = []
    for event in potty_events:
        potty_data.append({
            'date': event.timestamp.date(),
            'hour': event.timestamp.hour,
            'timestamp': event.timestamp,
            'event_type': 'Urination' if event.event_type == 'U' else 'Defecation',
            'is_accident': event.is_accident,
            'on_cue': event.on_cue,
            'recorded_by': event.recorded_by
        })
    
    if not potty_data:
        return {}
    
    df_potty = pd.DataFrame(potty_data)
    
    # 1. Daily potty events chart - CORRECT COUNTING
    # First count by date and type correctly
    daily_counts = df_potty.groupby(['date', 'event_type']).size().reset_index(name='count')
    
    # Verify the counts are correct before plotting
    total_by_date = {}
    for date, group in df_potty.groupby('date'):
        total_by_date[date] = {
            'Urination': len(group[group['event_type'] == 'Urination']),
            'Defecation': len(group[group['event_type'] == 'Defecation'])
        }
    
    # Create clean dataframe with verified counts
    verified_counts = []
    for date in sorted(total_by_date.keys()):
        for event_type in ['Urination', 'Defecation']:
            verified_counts.append({
                'date': date,
                'event_type': event_type,
                'count': total_by_date[date][event_type]
            })
    
    verified_df = pd.DataFrame(verified_counts)
    
    # Calculate daily totals
    daily_totals = df_potty.groupby('date').size().reset_index(name='Total')
    
    # Create improved bar chart with verified data
    fig1 = px.bar(
        verified_df, 
        x='date', 
        y='count', 
        color='event_type', 
        barmode='group',
        title='Daily Potty Events',
        labels={'date': 'Date', 'count': 'Number of Events', 'event_type': 'Type'},
        height=400,
        color_discrete_map={
            'Urination': '#4F77AA',  # Darker blue
            'Defecation': '#55A868'   # Darker green
        }
    )
    
    # Add a line for the daily total
    fig1.add_trace(
        go.Scatter(
            x=daily_totals['date'],
            y=daily_totals['Total'],
            mode='lines+markers',
            name='Total Events',
            line=dict(color='#DD5555', width=3),
            marker=dict(size=8)
        )
    )
    
    fig1.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Events",
        legend_title="Event Type",
        font=dict(size=14),
        yaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=1,  # Force integer ticks
            range=[0, verified_df['count'].max() + 1]  # Ensure y-axis starts at 0
        ),
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    plots['daily_events'] = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    
    # 2. Hourly events chart
    hour_range = list(range(24))
    
    # Get event counts by hour for each type
    u_counts = df_potty[df_potty['event_type'] == 'Urination'].groupby('hour').size()
    d_counts = df_potty[df_potty['event_type'] == 'Defecation'].groupby('hour').size()
    
    # Create complete hourly data
    hourly_data = []
    for hour in hour_range:
        hourly_data.append({
            'hour': hour,
            'Urination': u_counts.get(hour, 0),
            'Defecation': d_counts.get(hour, 0)
        })
    
    hourly_df = pd.DataFrame(hourly_data)
    
    # Create a more informative hourly plot
    fig3 = go.Figure()
    
    # Add Urination bars
    fig3.add_trace(go.Bar(
        x=hourly_df['hour'],
        y=hourly_df['Urination'],
        name='Urination',
        marker_color='#4F77AA'
    ))
    
    # Add Defecation bars
    fig3.add_trace(go.Bar(
        x=hourly_df['hour'],
        y=hourly_df['Defecation'],
        name='Defecation',
        marker_color='#55A868'
    ))
    
    # Find and mark peak hours
    peak_hour_u = hourly_df['Urination'].idxmax()
    peak_hour_d = hourly_df['Defecation'].idxmax()
    
    # Add annotations for peak hours
    annotations = []
    if hourly_df.loc[peak_hour_u, 'Urination'] > 0:
        annotations.append(dict(
            x=hourly_df.loc[peak_hour_u, 'hour'],
            y=hourly_df.loc[peak_hour_u, 'Urination'],
            text=f"Peak: {hourly_df.loc[peak_hour_u, 'hour']}:00",
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-40
        ))
    
    if hourly_df.loc[peak_hour_d, 'Defecation'] > 0:
        annotations.append(dict(
            x=hourly_df.loc[peak_hour_d, 'hour'],
            y=hourly_df.loc[peak_hour_d, 'Defecation'],
            text=f"Peak: {hourly_df.loc[peak_hour_d, 'hour']}:00",
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-40
        ))
    
    fig3.update_layout(
        title='Events by Hour of Day',
        xaxis=dict(
            title='Hour',
            tickmode='linear',
            tick0=0,
            dtick=2,
            ticktext=[f"{h}:00" for h in range(0, 24, 2)],
            tickvals=list(range(0, 24, 2)),
            range=[-0.5, 23.5]
        ),
        yaxis=dict(
            title='Number of Events',
            tickmode='linear',
            tick0=0,
            dtick=1
        ),
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        annotations=annotations,
        height=400
    )
    plots['hourly_events'] = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    
    # 3. Success/Accident rates
    daily_metrics = df_potty.groupby(df_potty['date']).agg({
        'is_accident': 'mean',
        'on_cue': 'mean'
    }).reset_index()
    
    daily_metrics['accident_rate'] = daily_metrics['is_accident'] * 100
    daily_metrics['success_rate'] = daily_metrics['on_cue'] * 100
    
    # Combined rates chart
    fig_combined = go.Figure()
    
    # Add success rate
    fig_combined.add_trace(go.Scatter(
        x=daily_metrics['date'],
        y=daily_metrics['success_rate'],
        mode='lines+markers',
        name='Success Rate (%)',
        line=dict(color='#55A868', width=3),
        marker=dict(size=8)
    ))
    
    # Add accident rate
    fig_combined.add_trace(go.Scatter(
        x=daily_metrics['date'],
        y=daily_metrics['accident_rate'],
        mode='lines+markers',
        name='Accident Rate (%)',
        line=dict(color='#DD5555', width=3),
        marker=dict(size=8)
    ))
    
    # Calculate and display 7-day moving average if enough data
    if len(daily_metrics) >= 7:
        daily_metrics['success_ma'] = daily_metrics['success_rate'].rolling(window=7).mean()
        daily_metrics['accident_ma'] = daily_metrics['accident_rate'].rolling(window=7).mean()
        
        fig_combined.add_trace(go.Scatter(
            x=daily_metrics['date'],
            y=daily_metrics['success_ma'],
            mode='lines',
            name='Success Rate (7-day avg)',
            line=dict(color='#55A868', width=2, dash='dash'),
            opacity=0.7
        ))
        
        fig_combined.add_trace(go.Scatter(
            x=daily_metrics['date'],
            y=daily_metrics['accident_ma'],
            mode='lines',
            name='Accident Rate (7-day avg)',
            line=dict(color='#DD5555', width=2, dash='dash'),
            opacity=0.7
        ))
    
    fig_combined.update_layout(
        title='Success vs. Accident Rates Over Time',
        xaxis_title='Date',
        yaxis_title='Rate (%)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(
            range=[0, 100],
            tickmode='linear',
            tick0=0,
            dtick=20
        ),
        hovermode='x unified',
        height=400
    )
    plots['combined_rates'] = json.dumps(fig_combined, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Individual rate charts
    # Accident rate chart
    fig2 = px.line(
        daily_metrics, 
        x='date', 
        y='accident_rate',
        title='Accident Rate (%) Over Time',
        labels={'date': 'Date', 'accident_rate': 'Accident Rate (%)'},
        height=400,
        markers=True,
        line_shape='spline'  # Smoother line
    )
    fig2.update_traces(line=dict(color='#DD5555', width=3), marker=dict(size=8))
    fig2.update_layout(
        xaxis_title="Date",
        yaxis_title="Accident Rate (%)",
        font=dict(size=14),
        yaxis=dict(
            range=[0, 100],
            tickmode='linear',
            tick0=0,
            dtick=20
        )
    )
    plots['accident_rate'] = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Success rate chart
    fig4 = px.line(
        daily_metrics, 
        x='date', 
        y='success_rate',
        title='Success Rate (On Cue %) Over Time',
        labels={'date': 'Date', 'success_rate': 'Success Rate (%)'},
        height=400,
        markers=True,
        line_shape='spline'  # Smoother line
    )
    fig4.update_traces(line=dict(color='#55A868', width=3), marker=dict(size=8))
    fig4.update_layout(
        xaxis_title="Date",
        yaxis_title="Success Rate (%)",
        font=dict(size=14),
        yaxis=dict(
            range=[0, 100],
            tickmode='linear',
            tick0=0,
            dtick=20
        )
    )
    plots['success_rate'] = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Time between events chart
    if len(potty_data) > 3:
        df_potty_sorted = df_potty.sort_values('timestamp')
        
        # Calculate time differences between events
        df_potty_sorted['next_event'] = df_potty_sorted['timestamp'].shift(-1)
        df_potty_sorted['time_to_next'] = (df_potty_sorted['next_event'] - df_potty_sorted['timestamp']).dt.total_seconds() / 60
        
        # Filter out unreasonable gaps (e.g., overnight)
        df_potty_sorted = df_potty_sorted[df_potty_sorted['time_to_next'] < 8*60]  # Less than 8 hours
        
        # Create histogram of time between events
        fig_intervals = px.histogram(
            df_potty_sorted,
            x='time_to_next',
            nbins=15,
            title='Time Between Potty Events',
            labels={'time_to_next': 'Minutes Until Next Event', 'count': 'Frequency'},
            height=400,
            color_discrete_sequence=['#4F77AA']
        )
        
        fig_intervals.update_layout(
            xaxis_title='Minutes Between Events',
            yaxis_title='Count',
            bargap=0.1
        )
        
        plots['potty_intervals'] = json.dumps(fig_intervals, cls=plotly.utils.PlotlyJSONEncoder)
    
    return plots

def create_walk_charts(walk_events):
    """Create charts for walk events."""
    plots = {}
    
    # Format walk data
    walk_data = []
    for event in walk_events:
        if event.duration is not None:
            walk_data.append({
                'date': event.start_time.date(),
                'duration': event.duration,
                'start_time': event.start_time
            })
    
    if not walk_data:
        return {}
    
    df_walks = pd.DataFrame(walk_data)
    
    # Sum up walk durations by day
    daily_walks = df_walks.groupby('date')['duration'].agg(['sum', 'count']).reset_index()
    daily_walks.rename(columns={'sum': 'total_duration', 'count': 'walk_count'}, inplace=True)
    
    # Calculate average walk time
    daily_walks['avg_duration'] = daily_walks['total_duration'] / daily_walks['walk_count']
    
    # Create improved walk chart
    fig5 = go.Figure()
    
    # Add total duration bars
    fig5.add_trace(go.Bar(
        x=daily_walks['date'],
        y=daily_walks['total_duration'],
        name='Total Walk Time',
        marker_color='#4F77AA',
        hovertemplate='Date: %{x}<br>Total: %{y} minutes<br>Walks: %{text}<extra></extra>',
        text=daily_walks['walk_count'].apply(lambda x: f"{x} walk{'s' if x > 1 else ''}")
    ))
    
    # Add average line
    if len(daily_walks) > 1:
        fig5.add_trace(go.Scatter(
            x=daily_walks['date'],
            y=daily_walks['avg_duration'],
            mode='lines+markers',
            name='Avg per Walk',
            line=dict(color='#FF8C94', width=2),
            marker=dict(size=8)
        ))
    
    # Weekly goal line
    fig5.add_trace(go.Scatter(
        x=daily_walks['date'],
        y=[30] * len(daily_walks),  # 30 minutes daily recommendation
        mode='lines',
        name='Recommended Daily',
        line=dict(color='#55A868', width=2, dash='dash')
    ))
    
    fig5.update_layout(
        title='Daily Walking Time',
        xaxis_title='Date',
        yaxis_title='Minutes',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=15
        ),
        hovermode='x unified',
        height=400
    )
    plots['walk_duration'] = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Day of week chart
    if len(df_walks) > 7:  # Only show if we have enough data
        df_walks['day_of_week'] = df_walks['start_time'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Aggregate by day of week
        dow_stats = df_walks.groupby('day_of_week')['duration'].agg(['mean', 'sum', 'count']).reset_index()
        
        # Reorder days
        dow_stats['day_index'] = dow_stats['day_of_week'].apply(lambda x: day_order.index(x))
        dow_stats = dow_stats.sort_values('day_index')
        
        # Create day of week pattern chart
        fig_dow = go.Figure()
        
        fig_dow.add_trace(go.Bar(
            x=dow_stats['day_of_week'],
            y=dow_stats['sum'],
            name='Total Minutes',
            marker_color='#4F77AA',
            hovertemplate='Day: %{x}<br>Total: %{y} minutes<br>Walks: %{text}<extra></extra>',
            text=dow_stats['count']
        ))
        
        fig_dow.update_layout(
            title='Walking Patterns by Day of Week',
            xaxis_title='Day of Week',
            yaxis_title='Total Minutes',
            height=400,
            xaxis={'categoryorder': 'array', 'categoryarray': day_order}
        )
        
        plots['walk_day_patterns'] = json.dumps(fig_dow, cls=plotly.utils.PlotlyJSONEncoder)
    
    return plots