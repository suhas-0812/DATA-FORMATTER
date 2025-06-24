import requests
from typing import Dict, Any
import streamlit as st

def analyze_place_with_perplexity(place_name: str, city: str, places_api_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze place information using Perplexity Sonar Pro model for the new accommodation format
    
    Args:
        place_name: Name of the place to search for
        city: City where the place is located
        places_api_output: Single place dictionary from Google Places API
        
    Returns:
        Dictionary with analyzed place information for new format
    """
    api_key = st.secrets["api_keys"]["perplexity"]
    
    # Validate API key format
    if not api_key.startswith('pplx-'):
        return {"error": "Invalid Perplexity API key format"}
    
    # Handle the case where no place data is provided
    if not places_api_output:
        return {"error": "No places data provided"}
    
    # Extract relevant information from places API output
    google_description = places_api_output.get('Description', 'N/A')
    google_category = places_api_output.get('Category', 'N/A')
    google_rating = places_api_output.get('google_rating', 'N/A')
    reviews = places_api_output.get('reviews', [])
    formatted_address = places_api_output.get('Formatted Address', 'N/A')
    
    # Prepare reviews text for analysis (first 5 reviews)
    reviews_text = ""
    if reviews:
        reviews_sample = reviews[:5]  # Take first 5 reviews
        for review in reviews_sample:
            if isinstance(review, dict) and 'text' in review:
                reviews_text += review['text'] + " | "
            elif isinstance(review, str):
                reviews_text += review + " | "
    
    # Construct the prompt for new format
    prompt = f"""
Please research and provide comprehensive information for the following accommodation using reliable and up-to-date sources. Focus on creating compelling content for a travel crew's accommodation listings.

Place Name: {place_name}
City: {city}
Google Category: {google_category}
Google Description: {google_description}
Google Rating: {google_rating}
Sample Reviews: {reviews_text}
Formatted Address: {formatted_address}

RESEARCH INSTRUCTIONS:
Research through multiple reliable sources including:
- Official website of the establishment
- TripAdvisor, Booking.com, Hotels.com, Expedia, Airbnb
- Travel blogs and professional travel guides
- Local tourism websites and recommendation sites
- Recent visitor reviews and testimonials
- Travel recommendation articles and "best of" lists
- Hotel brand information and chain details

FOCUS AREAS FOR NEW FORMAT:
1. **Hotel Brand Information**: Identify if this is part of a hotel chain/brand (Marriott, Hilton, Taj, ITC, Oberoi, etc.)

2. **Why We Love It Content**: Focus on what makes this place special, unique experiences, standout features, and compelling reasons to stay here

3. **Comprehensive Amenities**: Research all amenities, inclusions, services, facilities that guests can expect

4. **Product Details**: Room types, suites, villas, accommodation categories, special features, property layout

5. **Location Context**: Area details, neighborhood information, proximity to attractions

Based on your comprehensive research, provide information in JSON format:

{{
    "name_of_stay": "Extract the name of the accommodation from the place name if available, or 'To be filled' if unclear",
    "hotel_brand": "Extract hotel brand/chain name if available (e.g., Marriott, Hilton, Taj, ITC, Oberoi, Radisson, etc.) or 'Independent' if not part of a chain, or 'To be filled' if unclear",
    "price_inr": "Extract the price in INR if available, or 'To be filled' if unclear",
    "crew_exclusive_price": "Should be marked as 'To be filled' for now",
    "why_we_love_it": "Compelling 1-2 sentence recommendation focusing on what makes this place special and why someone should choose it. Make it personal and engaging.",
    "everything_you_need_to_know": "Comprehensive list of amenities, inclusions, services, and facilities. Include: dining options, spa/wellness, pool details, business facilities, connectivity, recreational activities, special services, policies, etc. Format as detailed description.",
    "product_details": "Detailed information about accommodation types, room categories, suites, villas, property layout, special features, room amenities, bed types, occupancy, etc. Include area/location specifics."
}}

IMPORTANT: 
- Focus on factual, verified information from reputable sources
- Make "why_we_love_it" compelling and personal
- Be comprehensive in "everything_you_need_to_know" - include all relevant amenities
- Provide specific details in "product_details" about accommodation types and features
- If information is not available or unclear, use "To be filled" for that field

Please respond with ONLY the JSON object, no additional text or source citations.
"""

    # Perplexity API endpoint
    url = "https://api.perplexity.ai/chat/completions"
    
    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Request payload
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0,
        "max_tokens": 4000
    }
    
    try:
        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        # Parse response
        response_data = response.json()
        
        # Extract the content from the response
        if 'choices' in response_data and len(response_data['choices']) > 0:
            content = response_data['choices'][0]['message']['content']
            
            # Return the raw content for Azure OpenAI to process
            return {
                "raw_response": content,
                "status": "success"
            }
                
        else:
            print("No valid response from Perplexity API")
            return {"error": "No valid response from Perplexity API"}
            
    except requests.exceptions.RequestException as e:
        print(f"Error calling Perplexity API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                print(f"API Error Details: {error_details}")
            except:
                print(f"Response content: {e.response.text}")
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}
