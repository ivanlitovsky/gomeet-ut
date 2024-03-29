import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.graph_objs as go
import plotly.express as px
import json
import streamlit as st
import time


# Function to convert hex color to RGBA
def hex_to_rgba(hex_color, alpha=1.0):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    return 'rgba(' + ', '.join(str(int(hex_color[i:i + lv // 3], 16)) for i in range(0, lv, lv // 3)) + f', {alpha})'


def plot_map(email, db, my_bar, progress_text):

    embeddings_raw = db.table('embeddings').select("*").execute()
    my_bar.progress(60, text=progress_text)
    time.sleep(0.01)

    embeddings = []
    for data in embeddings_raw.data:
        embeddings.append({
            'email': data['email'],
            'embeddings': json.loads(data['embeddings']),
            'cluster': data['cluster'],
        })

    # The email you want to highlight
    email_to_highlight = email

    # Extract embeddings and emails into lists
    embeddings_matrix = [entry['embeddings'] for entry in embeddings]
    emails = [entry['email'] for entry in embeddings]
    clusters = [entry['cluster'] for entry in embeddings]

    # Convert embeddings_matrix to a NumPy array
    embeddings_matrix = np.array(embeddings_matrix)

    my_bar.progress(70, text=progress_text)
    time.sleep(0.01)

    # Perform KMeans clustering
    num_clusters = 5

    # Perform PCA
    pca = PCA(n_components=2)
    embeddings_2d = pca.fit_transform(embeddings_matrix)

    my_bar.progress(80, text=progress_text)
    time.sleep(0.01)

    # Create a DataFrame for the reduced embeddings
    df = pd.DataFrame(embeddings_2d, columns=['x', 'y'])
    df['email'] = emails
    df['cluster'] = clusters
    df['highlight'] = df['email'] == email_to_highlight

    # Define the specific color codes for each cluster
    cluster_colors = {
        0: '#0d0788',
        1: '#7d08a6',
        2: '#fa4289',
        3: '#f99640',
        4: '#f2f921'
    }

    cluster_names = {
        #0: 'Engineers & Tech Leaders',
        0: 'Multidisciplinary & versatile minds',
        #1: 'Medical and Academic Experts ',
        1: 'Academics, Researchers & Medical Professionals',
        #2: 'Geopolitics & Social Sciences Professionals',
        2: 'Geopolitics & Global Issues Experts',
        #3: 'Entrepreneurs & Business Leaders',
        3: 'Execs & Business leaders',
        #4: 'Multidisciplinary & versatile minds'
        #4: 'Climate, Geopolitics & Global Issues Experts'
        4: 'Engineers in AI & Technology',
    }

    # Define marker colors with transparency for non-highlighted points and non-transparent for highlighted points
    colors = [hex_to_rgba(cluster_colors[i], alpha=0.7) for i in range(num_clusters)]  # 60% transparent
    colors_non_transparent = [hex_to_rgba(cluster_colors[i], alpha=1) for i in range(num_clusters)]  # Non-transparent

    # Plot using Plotly

    my_bar.progress(90, text=progress_text)
    time.sleep(0.01)

    fig = go.Figure()

    # Add a scatter plot for each cluster
    for cluster_num in range(num_clusters):
        cluster_df = df[(df['cluster'] == cluster_num) & (df['highlight'] == False)]
        fig.add_trace(go.Scatter(
            x=cluster_df['x'],
            y=cluster_df['y'],
            mode='markers',
            marker=dict(size=7, color=colors[cluster_num]),  # Use cluster-specific color
            name=cluster_names[cluster_num],  # Name for the legend
            hoverinfo='none'
        ))

    # Add the scatter plot for the highlighted email
    highlighted_df = df[df['highlight'] == True]
    fig.add_trace(go.Scatter(
        x=highlighted_df['x'],
        y=highlighted_df['y'],
        mode='markers+text',  # Enable markers and text
        marker=dict(size=20, color=[colors_non_transparent[i] for i in highlighted_df['cluster']]),  # same color as cluster, not transparent
        text=[f'<b>{email}</b>' for email in highlighted_df['email']],  # Show the email as text
        textposition="middle right",
        hoverinfo='none',
        textfont=dict(size=16, color='black', family="Arial, sans-serif"),  # Set font size, color, and weight for the highlighted email text
        showlegend=False
    ))

    # Update layout and plot
    fig.update_layout(height=400, legend_title_text='Cluster')
    #fig.update_traces(textfont_size=15)
    fig.update_xaxes(showline=False, showticklabels=False, showgrid=False)
    fig.update_yaxes(showline=False, showticklabels=False, showgrid=False)

    # Update the legend position to be below the chart
    fig.update_layout(legend=dict(
        x=0.5,  # Center the legend horizontally
        y=-0.1,  # Position the legend below the chart
        xanchor='center',  # Center the legend horizontally
        yanchor='top',  # Anchor the legend to the top
        bgcolor='rgba(255, 255, 255, 0.5)',  # Set a background color for the legend
        bordercolor='rgba(0, 0, 0, 0.5)',  # Set a border color for the legend
        orientation='h',
        title=''
    ))
    fig.update_layout(margin=dict(t=10))

    # Disable zooming in and out on the graph
    fig.update_layout(
        uirevision=True  # Ensure that the configuration is not overridden
    )

    my_bar.progress(100, text=progress_text)
    time.sleep(0.5)
    my_bar.empty()

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'Zoom' : False, 'staticPlot': True})