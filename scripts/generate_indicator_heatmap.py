#!/usr/bin/env python3
"""Generate indicator heatmap from scores CSV"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tempfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path

from src.utils.cloudflare import read_csv_from_cloud, upload_file_to_public_cloud, R2_PUBLIC_URL


class HeatmapGenerator:
    """Generates indicator heatmap from scores CSV"""
    
    COLORS = ['#FF0000', '#FF8C00', '#FFFF00', '#9ACD32', '#008000']
    
    def __init__(self, cloud_path: str = "indicator/result.csv"):
        self.cloud_path = cloud_path
        self.df = None
        self.figsize = None
    
    def _load_data(self):
        """Load and validate CSV data from cloud"""
        self.df = read_csv_from_cloud(self.cloud_path)
        
        if self.df is None or self.df.empty:
            raise ValueError(f"No data found at {self.cloud_path}")
        
        if 'date' not in self.df.columns:
            raise ValueError(f"CSV must contain 'date' column")
        
        self.df = self.df.set_index('date').sort_index(ascending=True).tail(5)
        
        # Convert to numeric
        for col in self.df.columns:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
    
    def _calculate_figsize(self):
        """Calculate optimal figure size"""
        n_cols = len(self.df.columns)
        n_rows = len(self.df.index)
        width = max(20, min(40, n_cols * 0.5))
        height = max(6, min(20, n_rows * 0.5 + 2))
        self.figsize = (width, height)
    
    def _create_plot(self) -> plt.Figure:
        """Create heatmap plot"""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Create colormap
        cmap = LinearSegmentedColormap.from_list('custom', self.COLORS, N=5)
        
        # Create heatmap
        im = ax.imshow(self.df.values, cmap=cmap, aspect='auto', 
                      vmin=1, vmax=5, interpolation='nearest')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Score (1-5)', fontsize=11, fontweight='bold')
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(self.df.columns)))
        ax.set_yticks(np.arange(len(self.df.index)))
        ax.set_xticklabels(self.df.columns, rotation=45, ha='right')
        ax.set_yticklabels(self.df.index)
        
        # Add value annotations
        for i in range(len(self.df.index)):
            for j in range(len(self.df.columns)):
                value = self.df.values[i, j]
                if not np.isnan(value):
                    ax.text(j, i, f'{value:.1f}', ha="center", va="center", 
                           color="black", fontsize=8)
        
        # Labels and title
        ax.set_xlabel('Indicator', fontsize=12, fontweight='bold')
        ax.set_ylabel('Date', fontsize=12, fontweight='bold')
        ax.set_title("Indicator Heatmap - Last Week\nScores: 1 (Red) to 5 (Green)", 
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return fig
    
    def _get_filename(self) -> str:
        """Generate filename based on most recent date"""
        most_recent = self.df.index[-1]
        
        if hasattr(most_recent, 'strftime'):
            date_str = most_recent.strftime('%Y-%m-%d')
        else:
            date_str = str(most_recent)
        
        return f"indicator_heatmap_{date_str.replace('-', '')}.png"
    
    def _save_and_upload(self, fig: plt.Figure) -> str:
        """Save figure and upload to cloud"""
        filename = self._get_filename()
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir) / filename
        
        try:
            # Save figure
            fig.savefig(temp_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            # Upload to cloud
            cloud_path = f"indicator/images/{filename}"
            if not upload_file_to_public_cloud(temp_path, cloud_path):
                raise ValueError("Failed to upload to cloud")
            
            cloud_url = f"{R2_PUBLIC_URL}/{cloud_path}"
            print(f"✅ Heatmap uploaded to cloud: {cloud_url}")
            return cloud_url
            
        finally:
            # Cleanup
            try:
                if temp_path.exists():
                    os.remove(temp_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                print(f"⚠️ Failed to clean up temp files: {e}")
    
    def generate(self) -> str:
        """Generate heatmap and return cloud URL"""
        self._load_data()
        self._calculate_figsize()
        fig = self._create_plot()
        return self._save_and_upload(fig)


def generate_indicator_heatmap(cloud_path: str = "indicator/result.csv") -> str:
    """
    Generate heatmap from indicator scores CSV.
    
    Args:
        cloud_path: Path to CSV file in R2
    
    Returns:
        Cloud URL of saved heatmap image
    """
    generator = HeatmapGenerator(cloud_path)
    return generator.generate()


if __name__ == "__main__":
    try:
        output = generate_indicator_heatmap()
        print(f"Heatmap URL: {output}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
