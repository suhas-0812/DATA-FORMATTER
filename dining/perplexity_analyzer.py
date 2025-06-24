import requests
from typing import Dict, Any
import streamlit as st

def analyze_place_with_perplexity(place_name: str, city: str, places_api_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze restaurant information using Perplexity Sonar Pro model for the new dining format
    
    Args:
        place_name: Name of the restaurant to search for
        city: City where the restaurant is located
        places_api_output: Single place dictionary from Google Places API
        
    Returns:
        Dictionary with analyzed restaurant information for new format
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
    
    # Construct the prompt for new simplified format
    prompt = f"""
Please research and provide comprehensive information for the following restaurant using reliable and up-to-date sources. Focus on creating compelling content for a travel crew's dining recommendations.

Restaurant Name: {place_name}
City: {city}
Google Category: {google_category}
Google Description: {google_description}
Google Rating: {google_rating}
Sample Reviews: {reviews_text}
Formatted Address: {formatted_address}

RESEARCH INSTRUCTIONS:
Research through multiple reliable sources including:
- Official restaurant website and social media
- Zomato, Swiggy, EazyDiner, OpenTable, TripAdvisor
- Food blogs and professional restaurant reviews
- Local dining guides and food critics
- Recent customer reviews and menu information
- Travel recommendation articles and "best of" lists

FOCUS AREAS FOR NEW FORMAT:
1. **Cuisines**: Identify all types of cuisine served (e.g., Indian, Continental, Asian, Italian, etc.)

2. **Why We Love It Content**: Focus on what makes this restaurant special, unique dishes, standout features, and compelling reasons to dine here

3. **Everything You Need to Know**: Research all important information including menu highlights, signature dishes, ambiance, service style, dietary options, reservation policies, operating hours, special features, etc.

Based on your comprehensive research, provide information in JSON format:

{{
    "restaurant_name": "Extract the name of the restaurant from the place name if available, or 'To be filled' if unclear",
    "cuisines": "List all types of cuisine served (e.g., 'Indian, Continental, Asian') or 'To be filled' if unclear",
    "price": "Extract the price range or average cost if available, or 'To be filled' if unclear",
    "crew_exclusive_price": "Should be marked as 'To be filled' for now",
    "why_we_love_it": "Compelling 1-2 sentence recommendation focusing on what makes this restaurant special and why someone should dine here. Make it personal and engaging.",
    "everything_you_need_to_know": "Comprehensive information including: menu highlights, signature dishes, ambiance, service style, dietary options (veg/non-veg/vegan), reservation requirements, operating hours, special features, location details, etc. Format as detailed description."
}}

IMPORTANT: 
- Focus on factual, verified information from reputable sources
- Make "why_we_love_it" compelling and personal
- Be comprehensive in "everything_you_need_to_know" - include all relevant restaurant information
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

def get_dining_info(place_name: str, city: str, places_api_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simplified function to get dining establishment information
    
    Args:
        place_name: Name of the restaurant/dining place
        city: City where the restaurant is located
        places_api_output: Google Places API output from search_places_with_details function
        
    Returns:
        Dictionary with dining information or error
    """
    result = analyze_place_with_perplexity(place_name, city, places_api_output)
    
    if "error" in result:
        return result
    
    # Return parsed data if available, otherwise raw response
    if "parsed_data" in result:
        return result["parsed_data"]
    else:
        return {"raw_response": result.get("raw_response", "No data available")}