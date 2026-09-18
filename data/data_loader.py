import json
import os
from typing import Dict, List, Any

# Path to the JSON data file relative to this loader module
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "goa_data.json")

def load_data() -> Dict[str, Any]:
    """
    Loads and returns the entire structured Goa travel data from JSON file.
    """
    if not os.path.exists(DATA_FILE_PATH):
        raise FileNotFoundError(f"Data file not found at: {DATA_FILE_PATH}")
        
    with open(DATA_FILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

def filter_by_area(area_name: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Filters places across all categories by area name (case-insensitive search).
    Example: filter_by_area("Anjuna") or filter_by_area("North Goa")
    """
    data = load_data()
    area_clean = area_name.strip().lower()
    
    filtered_results: Dict[str, List[Dict[str, Any]]] = {
        "restaurants": [],
        "beaches": [],
        "activities": [],
        "transport": []
    }
    
    for category in ["restaurants", "beaches", "activities"]:
        if category in data:
            for item in data[category]:
                item_area = item.get("area", "").lower()
                if area_clean in item_area or item_area in area_clean:
                    filtered_results[category].append(item)
                    
    # Include general transport options
    filtered_results["transport"] = data.get("transport", [])
    
    return filtered_results

def filter_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Returns items belonging to a specific category.
    Supported categories: 'restaurants', 'beaches', 'activities', 'transport'.
    """
    data = load_data()
    cat_clean = category.strip().lower()
    
    if cat_clean in data:
        return data[cat_clean]
    
    # Handle singular/plural variations
    cat_mapping = {
        "restaurant": "restaurants",
        "beach": "beaches",
        "activity": "activities",
        "transports": "transport"
    }
    
    mapped_cat = cat_mapping.get(cat_clean, cat_clean)
    return data.get(mapped_cat, [])

if __name__ == "__main__":
    # Quick test execution
    all_data = load_data()
    print(f"Total categories loaded: {list(all_data.keys())}")
    
    anjuna_places = filter_by_area("Anjuna")
    print(f"Anjuna Restaurants: {len(anjuna_places['restaurants'])}")
    print(f"Anjuna Activities: {len(anjuna_places['activities'])}")
    
    beaches = filter_by_category("beaches")
    print(f"Total Beaches loaded: {len(beaches)}")
