from .google_places import search_places_with_details
from .perplexity_analyzer import analyze_place_with_perplexity
from .openaicalls import format_with_azure_openai
import json
def populate_accommodation(accommodation_name, city):
    print("[ACCOMMODATION] Starting accommodation populator")
    places_api_output = search_places_with_details(accommodation_name, city)
    if "error" in places_api_output:
        return places_api_output
    
    print("[ACCOMMODATION] Google Places API call successful")

    places_context_for_llms = {
        "Formatted Address": places_api_output["Formatted Address"],
        "Description": places_api_output["Description"],
        "google_rating": places_api_output["google_rating"],
        "Category": places_api_output["Category"],
    }

    perplexity_output = analyze_place_with_perplexity(accommodation_name, city, places_context_for_llms)
    if "error" in perplexity_output:
        return {"error": "No perplexity data available"}
    
    print("[ACCOMMODATION] Perplexity API call successful")
    
    
    formatted_output = format_with_azure_openai(accommodation_name, places_context_for_llms, perplexity_output)
    if "error" in formatted_output:
        return {"error": "No formatted output available"}
    print("[ACCOMMODATION] Azure OpenAI API call successful")
    
    formatted_output["Heading"] = "Stay Options"
    formatted_output["Destination"] = city
    formatted_output["User Message"] = "Hi <Name>, these are the handpicked options by our curators for you"
    formatted_output["Google Rating"] = places_api_output["google_rating"]
    formatted_output["Location"] = places_api_output["google_maps_url"]
    formatted_output["photo_urls"] = places_api_output["photo_urls"]
    return formatted_output


if __name__ == "__main__":
    print(json.dumps(populate_accommodation("The Oberoi", "Bangalore"), indent=4))