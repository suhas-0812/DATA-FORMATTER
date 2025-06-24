import requests
import json
from typing import List, Dict, Any
import streamlit as st

def search_places_with_details(place_name: str, city: str) -> Dict[str, str]:
    """
    Single function to search places and return structured data with required fields
    
    Args:
        place_name: Name of the place to search for
        city: City to search in
        
    Returns:
        Dictionary with keys: Country, Destination L1 (State), Destination L2 (City), 
        Destination L3 (Area), Category, Description, google_rating, website, google_maps_url,
        opening_hours, photo_urls (list of 3), reviews (newest 100 review texts)
        Returns the first place found, or empty dict if no places found
    """
    
    # Construct the search query
    query = f"{place_name} in {city}"
    
    # API endpoint for text search (New Places API)
    url = "https://places.googleapis.com/v1/places:searchText"
    
    # Headers for the new API - Updated field mask to include reviews and rating
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': st.secrets["api_keys"]["google_places"],
        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.types,places.primaryType,places.rating,places.userRatingCount,places.priceLevel,places.businessStatus,places.websiteUri,places.regularOpeningHours,places.photos,places.googleMapsUri,places.editorialSummary'
    }
    
    # Request body for the new API
    data = {
        'textQuery': query,
        'maxResultCount': 20
    }
    
    try:
        # Make the API request
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        # Parse JSON response
        results = response.json()

        
        # Check if we have places in the response
        places = results.get('places', [])
        
        if not places:
            print(f"No places found for '{place_name}' in '{city}'")
            return {}
        
        # Process only the first place
        place = places[0]
        
        # Extract address components for location hierarchy
        location_info = place.get('formattedAddress', 'N/A')
        
        # Extract category from types
        types = place.get('types', [])
        category = ", ".join(types) if types else 'N/A'
        
        # Extract description
        description = 'N/A'
        if 'editorialSummary' in place:
            description = place['editorialSummary'].get('text', 'N/A')
        elif 'generativeSummary' in place:
            description = place['generativeSummary'].get('text', 'N/A')
        
        # Extract Google rating
        google_rating = place.get('rating', 'N/A')
        
        # Extract website
        website = place.get('websiteUri', 'N/A')
        
        # Clean website URL - remove query parameters and keep only base URL
        if website != 'N/A' and website:
            try:
                # Split by '?' to remove query parameters
                if '?' in website:
                    website = website.split('?')[0]
                # Remove trailing slash if present
                website = website.rstrip('/')
            except Exception:
                pass  # Keep original if cleaning fails
        
        # Extract Google Maps URL
        google_maps_url = place.get('googleMapsUri', 'N/A')
        
        # Extract opening hours
        opening_hours = 'N/A'
        regular_opening_hours = place.get('regularOpeningHours', {})
        if regular_opening_hours:
            # Get weekday descriptions which provide formatted opening hours
            weekday_descriptions = regular_opening_hours.get('weekdayDescriptions', [])
            if weekday_descriptions:
                # Clean up Unicode characters in opening hours
                cleaned_hours = []
                for hour_text in weekday_descriptions:
                    # Replace common Unicode characters with regular ones
                    cleaned_text = hour_text.replace('\u2009', ' ')  # Thin space -> regular space
                    cleaned_text = cleaned_text.replace('\u2013', '-')  # En dash -> hyphen
                    cleaned_text = cleaned_text.replace('\u202f', ' ')  # Narrow no-break space -> regular space
                    cleaned_text = cleaned_text.replace('\u00a0', ' ')  # Non-breaking space -> regular space
                    cleaned_hours.append(cleaned_text)
                opening_hours = cleaned_hours
            else:
                opening_hours = 'N/A'
        
        # Extract and construct photo URLs
        photos_data = place.get('photos', [])
        photo_urls = []
        api_key = st.secrets["api_keys"]["google_places"]
        
        for photo in photos_data[:10]:  # Get only first 10 photos
            photo_name = photo.get('name', '')
            if photo_name:
                # Construct photo URL using the Photo API
                photo_url = f"https://places.googleapis.com/v1/{photo_name}/media?maxHeightPx=800&maxWidthPx=800&key={api_key}"
                photo_urls.append(photo_url)
        
        # Ensure we have exactly 3 photo URLs (pad with N/A if needed)
        while len(photo_urls) < 10:
            photo_urls.append('N/A')
        
        # Extract and process reviews - just the text content
        reviews_data = place.get('reviews', [])
        review_texts = []
      
        for review in reviews_data:
            review_text = review.get('text', {}).get('text', '')
            publish_time = review.get('publishTime', 'N/A')
            
            if review_text:  # Only include non-empty review texts
                review_texts.append({
                    'text': review_text,
                    'publish_time': publish_time
                })
        
        
        # Create structured result with all required fields - return single object
        place_data = {
            "Formatted Address": location_info,
            'Category': category,
            'Description': description,
            'google_rating': google_rating,
            'website': website,
            'google_maps_url': google_maps_url,
            'opening_hours': opening_hours,
            'photo_urls': photo_urls,
            'reviews': review_texts
        }
        
        return place_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return {"Error making Google Places API request": e}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return {"Error parsing JSON response in Google Places API": e}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"Unexpected error in Google Places API": e}
    
if __name__ == "__main__":
    print(search_places_with_details("The Oberoi", "Bangalore"))