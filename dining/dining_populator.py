from .google_places import search_places_with_details
from .perplexity_analyzer import analyze_place_with_perplexity
from .openaicalls import format_with_azure_openai
import json

def populate_dining(restaurant_name, city):
    print("[DINING] Starting dining populator")
    places_api_output = search_places_with_details(restaurant_name, city)
    if "error" in places_api_output:
        return places_api_output
    
    print("[DINING] Google Places API call successful")

    places_context_for_llms = {
        "Formatted Address": places_api_output["Formatted Address"],
        "Description": places_api_output["Description"],
        "google_rating": places_api_output["google_rating"],
        "Category": places_api_output["Category"],
    }

    perplexity_output = analyze_place_with_perplexity(restaurant_name, city, places_context_for_llms)
    if "error" in perplexity_output:
        return {"error": "No perplexity data available"}
    
    print("[DINING] Perplexity API call successful")
    
    formatted_output = format_with_azure_openai(restaurant_name, places_context_for_llms, perplexity_output)
    if "error" in formatted_output:
        return {"error": "No formatted output available"}
    print("[DINING] Azure OpenAI API call successful")
    
    formatted_output["Heading"] = "Dining Options"
    formatted_output["Destination"] = city
    formatted_output["User Message"] = "Hi <Name>, these are the handpicked dining options by our curators for you"
    formatted_output["Timings"] = "\n".join(places_api_output["opening_hours"])
    formatted_output["Google Rating"] = places_api_output["google_rating"]
    formatted_output["Location"] = places_api_output["google_maps_url"]
    formatted_output["photo_urls"] = places_api_output["photo_urls"]
    return formatted_output


if __name__ == "__main__":
    print(json.dumps(populate_dining("Toit", "Bangalore"), indent=4))