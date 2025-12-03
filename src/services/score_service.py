"""Score collection and persistence service"""

from datetime import datetime
import pandas as pd
from src.types.analysis_report import AnalysisReport
from src.utils.cloudflare import write_csv_to_cloud, read_csv_from_cloud


def collect_scores(results: list[AnalysisReport]) -> dict[str, float]:
    """
    Collect scores from analysis results.
    
    Args:
        results: List of AnalysisReport objects from sub-agents
        
    Returns:
        Dictionary mapping 'agent_indicator' to score value
    """
    scores_data = {}
    for result in results:
        # Extract score from AnalysisReport (only if score exists and is not empty)
        if hasattr(result, 'score') and result.score:
            for score_item in result.score:
                # Create column name: agent_indicator
                if score_item.agent == score_item.indicator:
                    column_name = score_item.agent
                else:
                    column_name = f"{score_item.agent}_{score_item.indicator}"
                scores_data[column_name] = score_item.value
    return scores_data


def save_scores_to_csv(results: list[AnalysisReport], cloud_path: str = "indicator/result.csv"):
    """
    Collect and save scores from analysis results to CSV in cloud storage.
    
    This function is designed to be used as a hook in orchestrator agents
    or called directly from other parts of the application.
    
    Args:
        results: List of AnalysisReport objects from sub-agents
        cloud_path: Path in cloud storage (default: "indicator/result.csv")
    """
    try:
        # Collect all scores
        scores_data = collect_scores(results)
        
        if not scores_data:
            # No scores to save
            return
        
        # Create DataFrame with today's date as index
        today = datetime.now().strftime("%Y-%m-%d")
        df_new = pd.DataFrame([scores_data], index=[today])
        df_new.index.name = "date"
        
        # Try to read existing CSV and append
        df_existing = read_csv_from_cloud(cloud_path)
        
        if df_existing is not None:
            # Set date as index if it exists as a column
            if 'date' in df_existing.columns:
                df_existing = df_existing.set_index('date')
            
            # Append new row, avoiding duplicates
            if today not in df_existing.index:
                df_main = pd.concat([df_existing, df_new]) # concat the two dataframes -> concat rows
            else:
                # Merge existing row with new row (combine both columns)
                # New values take precedence, existing values fill missing columns
                s1 = df_existing.loc[today].copy() # convert to series
                s2 = df_new.loc[today] # convert to series
                s1.update(s2)
                
                new_only = s2[~s2.index.isin(s1.index)]
                merged = pd.concat([s1, new_only]) # concat the two series -> concat columns
                
                df_existing.loc[today, merged.index] = merged
                df_main = df_existing
        else:
            # No existing file, create new one
            df_main = df_new
        
        # Reset index to have date as a column for CSV
        df_main = df_main.reset_index()
        
        # Save to cloud
        write_csv_to_cloud(df_main, cloud_path)
        print(f"✅ Scores saved to CSV: {cloud_path}")
        
    except Exception as e:
        # Silently fail - don't break the main flow if CSV saving fails
        print(f"Warning: Failed to save scores to CSV: {e}")

