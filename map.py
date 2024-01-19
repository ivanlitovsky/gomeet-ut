import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.graph_objs as go
import plotly.express as px
import json
import streamlit as st


# Function to convert hex color to RGBA
def hex_to_rgba(hex_color, alpha=1.0):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    return 'rgba(' + ', '.join(str(int(hex_color[i:i + lv // 3], 16)) for i in range(0, lv, lv // 3)) + f', {alpha})'


def plot_map(email, db):

    embeddings_raw = db.table('embeddings').select("*").execute()
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

    # Perform KMeans clustering
    num_clusters = 5

    # Perform PCA
    pca = PCA(n_components=2)
    embeddings_2d = pca.fit_transform(embeddings_matrix)

    # Create a DataFrame for the reduced embeddings
    df = pd.DataFrame(embeddings_2d, columns=['x', 'y'])
    df['email'] = emails
    df['cluster'] = clusters
    df['highlight'] = df['email'] == email_to_highlight

    # Define the specific color codes for each cluster
    cluster_colors = {
        0: '#0d0788',
        1: '#7d08a6',
        2: '#cc477a',
        3: '#f99640',
        4: '#f2f921'
    }

    cluster_names = {
        0: 'Engineers & Tech Leaders',
        1: 'Medical and Academic Experts ',
        2: 'Geopolitics & Social Sciences Professionals',
        3: 'Entrepreneurs',
        4: 'Curious & versatile minds'
    }

    # Define marker colors with transparency for non-highlighted points and non-transparent for highlighted points
    colors = [hex_to_rgba(cluster_colors[i], alpha=0.6) for i in range(num_clusters)]  # 60% transparent
    colors_non_transparent = [hex_to_rgba(cluster_colors[i], alpha=1) for i in range(num_clusters)]  # Non-transparent

    # Plot using Plotly

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
    fig.update_layout(height=500, legend_title_text='Cluster')
    #fig.update_traces(textfont_size=15)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})