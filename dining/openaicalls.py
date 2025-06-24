import requests
import json
from typing import Dict, Any
import streamlit as st

def format_with_azure_openai(place_name: str, google_places_data: Dict[str, Any], perplexity_data: str) -> Dict[str, Any]:
    """
    Format the combined data using Azure OpenAI to create the final structured output for dining
    
    Args:
        place_name: Original restaurant name from user input
        google_places_data: Output from Google Places API
        perplexity_data: Raw response string from Perplexity
        
    Returns:
        Formatted dictionary with the new dining field structure or error
    """
    
    # Azure OpenAI configuration
    azure_endpoint = st.secrets["azure_openai"]["endpoint"]
    api_key = st.secrets["api_keys"]["azure_openai"]
    deployment_name = st.secrets["azure_openai"]["deployment_name"]
    api_version = st.secrets["azure_openai"]["api_version"]
    
    # Construct the formatting prompt
    prompt = f"""
You are a restaurant data formatting expert. Format the following data into a specific JSON structure for a travel crew's dining recommendations.

USER INPUT:
Restaurant Name: {place_name}

GOOGLE PLACES DATA:
{json.dumps(google_places_data, indent=2)}

PERPLEXITY RECOMMENDATION DATA:
{perplexity_data if perplexity_data else 'No data available'}

FORMATTING INSTRUCTIONS:
Create a JSON object with exactly these fields in the new simplified format:

1. Restaurant Name: Use the original restaurant name from user input
2. Cuisines: Extract cuisine types from the data (e.g., "Indian, Continental, Asian")
3. Price: Always set to "To be filled" (pricing not available in source data)
4. Crew Exclusive Price: Always set to "To be filled"
5. Why we love it: Create a compelling recommendation based on Perplexity data and Google description - focus on what makes this restaurant special and why someone should dine here
6. Everything you need to know: Combine all important restaurant information from both Google and Perplexity data. Include menu highlights, signature dishes, ambiance, service style, dietary options, hours, reservation policies, special features, etc.

IMPORTANT RULES:
- "Restaurant Name" should be the exact user input
- "Cuisines" should be extracted from available data, otherwise "To be filled"
- "Price" and "Crew Exclusive Price" are always "To be filled"
- "Why we love it" should be a compelling, personal recommendation (1-2 sentences)
- "Everything you need to know" should be comprehensive restaurant information
- If any field is missing or unclear, use appropriate defaults:
  - Text fields: "To be filled" or "Not available"

Return ONLY the JSON object, no additional text.

Expected JSON structure:
{{
    "Restaurant Name": "string",
    "Cuisines": "string", 
    "Price": "To be filled",
    "Crew Exclusive Price": "To be filled",
    "Why we love it": "string",
    "Everything you need to know": "string"
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
                    "Restaurant Name", "Cuisines", "Price", "Crew Exclusive Price",
                    "Why we love it", "Everything you need to know"
                ]
                
                # Ensure all required fields are present with defaults
                for field in required_fields:
                    if field not in formatted_data:
                        if field in ["Price", "Crew Exclusive Price"]:
                            formatted_data[field] = "To be filled"
                        elif field == "Restaurant Name":
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

