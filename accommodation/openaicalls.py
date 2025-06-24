import json
import requests
from typing import Dict, Any
import streamlit as st

def format_with_azure_openai(place_name: str, google_places_data: Dict[str, Any], perplexity_data: str) -> Dict[str, Any]:
    """
    Format the combined data using Azure OpenAI to create the final structured output
    
    Args:
        place_name: Original place name from user input
        google_places_data: Output from Google Places API
        perplexity_data: Raw response string from Perplexity
        
    Returns:
        Formatted dictionary with the new field structure or error
    """
    
    # Azure OpenAI configuration
    azure_endpoint = st.secrets["azure_openai"]["endpoint"]
    api_key = st.secrets["api_keys"]["azure_openai"]
    deployment_name = st.secrets["azure_openai"]["deployment_name"]
    api_version = st.secrets["azure_openai"]["api_version"]
    
    # Construct the formatting prompt
    prompt = f"""
You are a travel accommodation data formatting expert. Format the following data into a specific JSON structure for a travel crew's accommodation listings.

USER INPUT:
Place Name: {place_name}

GOOGLE PLACES DATA:
{json.dumps(google_places_data, indent=2)}

PERPLEXITY RECOMMENDATION DATA:
{perplexity_data if perplexity_data else 'No data available'}

FORMATTING INSTRUCTIONS:
Create a JSON object with exactly these fields in the new format:

1. Name of Stay: Use the original place name from user input
2. Hotel Brand: Extract hotel brand/chain name if available from the data, otherwise "To be filled"
3. Price: In INR: Always set to "To be filled" (pricing not available in source data)
4. Crew Exclusive Price: Always set to "To be filled"
5. Why we love it: Create a compelling recommendation based on Perplexity data and Google description - focus on what makes this place special and why someone should choose it
6. Everything you need to know: Combine all amenities, features, and inclusions from both Google and Perplexity data. Include information about pool, views, pet policy, family facilities, romantic features, etc. Format as a comprehensive list.
7. Product Details: Include room types, accommodation category, area/location details, and any specific property details. Use Category from Perplexity data and area information.

IMPORTANT RULES:
- "Name of Stay" should be the exact user input
- "Hotel Brand" should be extracted if it's a known chain (Marriott, Hilton, Taj, etc.), otherwise "To be filled"
- "Price: In INR" and "Crew Exclusive Price" are always "To be filled"
- "Why we love it" should be a compelling, personal recommendation (1-2 sentences)
- "Everything you need to know" should be comprehensive amenities/features list
- "Product Details" should include accommodation type, room details, location specifics
- If any field is missing or unclear, use appropriate defaults:
  - Text fields: "To be filled" or "Not available"

Return ONLY the JSON object, no additional text.

Expected JSON structure:
{{
    "Name of Stay": "string",
    "Hotel Brand": "string", 
    "Price: In INR": "To be filled",
    "Crew Exclusive Price": "To be filled",
    "Why we love it": "string",
    "Everything you need to know": "string",
    "Product Details": "string",
}}
"""

    # Azure OpenAI API call
    url = f"{azure_endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0,
        "max_tokens": 2000
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
            
            # Clean and parse the JSON response
            try:
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                formatted_data = json.loads(content)
                
                # Validate and ensure all required fields are present
                required_fields = [
                    "Name of Stay", "Hotel Brand", "Price: In INR", "Crew Exclusive Price",
                    "Why we love it", "Everything you need to know", "Product Details"
                ]
                
                # Ensure all required fields are present with defaults
                for field in required_fields:
                    if field not in formatted_data:
                        if field in ["Price: In INR", "Crew Exclusive Price"]:
                            formatted_data[field] = "To be filled"
                        elif field == "Name of Stay":
                            formatted_data[field] = place_name
                        else:
                            formatted_data[field] = "To be filled"
                
                return formatted_data
                
            except json.JSONDecodeError as e:
                return {"error": f"Failed to parse Azure OpenAI response as JSON: {str(e)}"}
                
        else:
            return {"error": "No valid response received from Azure OpenAI"}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Azure OpenAI API request failed: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                error_msg += f" - Details: {error_details}"
            except:
                error_msg += f" - Response: {e.response.text}"
        return {"error": error_msg}
    except Exception as e:
        return {"error": f"Unexpected error in Azure OpenAI formatting: {str(e)}"}

