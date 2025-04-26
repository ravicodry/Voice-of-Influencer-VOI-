import json
import os
from datetime import datetime

DATA_FILE = "segment_product_reviews.json"  # Consistent filename

def save_segment_product_analysis(analyzed_segments):
    """Saves the segment-level analysis with product names to a JSON file."""
    data = load_segment_product_analysis()
    data.extend(analyzed_segments)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_segment_product_analysis():
    """Loads the segment-level analysis data from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return []