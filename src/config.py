"""Global configuration settings for the market analysis agent"""

import os

# Language settings for report generation
# Options: "English" or "Korean"
REPORT_LANGUAGE = "Korean"

# Directory paths
CHART_OUTPUT_DIR = os.path.join(os.getcwd(), "charts")
os.makedirs(CHART_OUTPUT_DIR, exist_ok=True)

