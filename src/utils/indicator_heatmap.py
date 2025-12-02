"""Generate heatmap from indicator scores CSV"""
import tempfile
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path

from src.utils.cloudflare import read_csv_from_cloud, upload_file_to_public_cloud, R2_PUBLIC_URL


def generate_indicator_heatmap(
    cloud_path: str = "indicator/result.csv",
    figsize: tuple = None
) -> str:
    """
    Generate heatmap from indicator scores CSV.
    
    Args:
        cloud_path: Path to CSV file in R2
        figsize: Figure size (width, height). Default: auto-calculated
    
    Returns:
        Path to saved heatmap image
    """
    # Read CSV from R2
    df = read_csv_from_cloud(cloud_path)
    
    if df is None or df.empty:
        raise ValueError(f"No data found at {cloud_path}")
    
    # Validate date column exists
    if 'date' not in df.columns:
        raise ValueError(f"CSV must contain 'date' column. Found columns: {df.columns.tolist()}")
    
    # Set date as index
    df = df.set_index('date')
    
    # Validate index is not empty and contains valid dates
    if df.index.empty:
        raise ValueError(f"No valid dates found in CSV")

    # Sort by date (oldest first for chronological order)
    df = df.sort_index(ascending=True)
    
    # Keep only last 5 rows (most recent month)
    df = df.tail(5)
    
    # Convert all columns to numeric (handle any string values)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Calculate figure size if not provided
    if figsize is None:
        n_cols = len(df.columns)
        n_rows = len(df.index)
        # Base size with scaling
        width = max(20, min(40, n_cols * 0.5))
        height = max(6, min(20, n_rows * 0.5 + 2))
        figsize = (width, height)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create custom colormap (1=red, 3=yellow, 5=green)
    colors = ['#FF0000', '#FF8C00', '#FFFF00', '#9ACD32', '#008000']  # Red -> Orange -> Yellow -> Yellow-Green -> Green
    n_bins = 5
    cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)
    
    # Prepare data for heatmap
    # df: rows=dates, columns=indicators
    data = df.values
    
    # Create heatmap using imshow
    im = ax.imshow(data, cmap=cmap, aspect='auto', vmin=1, vmax=5, interpolation='nearest')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Score (1-5)', fontsize=11, fontweight='bold')
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(df.columns)))
    ax.set_yticks(np.arange(len(df.index)))
    ax.set_xticklabels(df.columns, rotation=45, ha='right')
    ax.set_yticklabels(df.index)  # Show dates on Y-axis
    
    # Add text annotations (values)
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            value = data[i, j]
            if not np.isnan(value):
                text = ax.text(j, i, f'{value:.1f}',
                             ha="center", va="center", color="black", fontsize=8)
    
    # Set labels
    ax.set_xlabel('Indicator', fontsize=12, fontweight='bold')
    ax.set_ylabel('Date', fontsize=12, fontweight='bold')
    
    # Get most recent date for filename
    most_recent_date = df.index[-1]
    
    # Convert to string if it's a Timestamp or other type
    if hasattr(most_recent_date, 'strftime'):
        # Timestamp object
        most_recent_date_str = most_recent_date.strftime('%Y-%m-%d')
    elif isinstance(most_recent_date, str):
        # Already a string
        most_recent_date_str = most_recent_date
    else:
        # Fallback: convert to string
        most_recent_date_str = str(most_recent_date)
    
    # Title
    title = f"Indicator Heatmap - Last One Month\nScores: 1 (Red) to 5 (Green)"
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Rotate x-axis labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    # Tight layout
    plt.tight_layout()
    
    # Save to temporary file first
    filename = f"indicator_heatmap_{most_recent_date_str.replace('-', '')}.png"
    
    # Create temp file
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir) / filename
    
    try:
        plt.savefig(temp_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        # Upload to cloud
        cloud_path = f"indicator/images/{filename}"
        if upload_file_to_public_cloud(temp_path, cloud_path):
            cloud_url = f"{R2_PUBLIC_URL}/{cloud_path}"
            print(f"✅ Heatmap uploaded to cloud: {cloud_url}")
            return cloud_url
        else:
            print(f"❌ Failed to upload to cloud: {temp_path}")
            raise ValueError(f"Failed to upload to cloud: {temp_path}")
    finally:
        # Always clean up temp files, even if upload fails
        try:
            if temp_path.exists():
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except Exception as cleanup_error:
            print(f"⚠️ Failed to clean up temp files: {cleanup_error}")


if __name__ == "__main__":
    try:
        output = generate_indicator_heatmap()
    except Exception as e:
        print(f"Error: {e}")
