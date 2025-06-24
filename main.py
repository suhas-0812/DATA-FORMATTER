import streamlit as st
from accommodation.accommodation_populator import populate_accommodation
from dining.dining_populator import populate_dining
import json

# Configure page
st.set_page_config(
    page_title="Metadata Formatter",
    page_icon="📋",
    layout="wide"
)


pages = st.sidebar.selectbox("Select a page", ["Accommodation", "Dining", "Activities"])

if pages == "Accommodation":
    st.title("🏨 Accommodation Metadata Populator")
    st.write("Enter accommodation details to get comprehensive metadata")

    # Input fields
    col1, col2, col3 = st.columns(3)
    with col1:
        accommodation_name = st.text_input("Accommodation Name", placeholder="e.g., The Ritz-Carlton")
    with col2:
        city = st.text_input("City", placeholder="e.g., New York")
    with col3:
        link = st.text_input("Link (Optional)", placeholder="https://example.com")

    if st.button("Get Metadata", type="primary"):
        if accommodation_name and city:
            with st.spinner("Fetching metadata..."):
                data = populate_accommodation(accommodation_name, city)

                if data and "error" not in data:
                    st.success("✅ Metadata retrieved successfully!")
                    
                    st.subheader("📋 Metadata Fields")
                    
                    # Define the preferred order of fields to display (if they exist)
                    preferred_field_order = [
                        ("Heading", "Heading"),
                        ("Destination", "Destination"),
                        ("User Message", "User Message"),
                        ("Name of Stay", "Name of Stay"),
                        ("Hotel Brand", "Hotel Brand"),
                        ("Price: In INR", "Price: In INR"),
                        ("Crew Exclusive Price", "Crew Exclusive Price"),
                        ("Why we love it", "Why we love it"),
                        ("Everything you need to know", "Everything you need to know"),
                        ("Product Details", "Product Details"),
                        ("Google Rating", "Google Rating"),
                        ("Location", "Location")
                    ]
                    
                    # Filter to only show fields that actually exist in the data
                    available_fields = [(display_name, key) for display_name, key in preferred_field_order if key in data]
                    
                    # Add any additional fields that might be in the data but not in our preferred list
                    for key, value in data.items():
                        if key not in [field[1] for field in available_fields] and key not in ['photo_urls', 'website', 'google_maps_url']:
                            # Format the key for display (replace underscores with spaces and title case)
                            display_name = key.replace('_', ' ').title()
                            available_fields.append((display_name, key))
                    
                    # Display each available field with copy functionality
                    for display_name, key in available_fields:
                        value = str(data[key])
                        
                        st.write(f"**{display_name}:**")
                        st.code(value, language="text")
                        st.divider()
                    
                    # Display images section
                    st.subheader("🖼️ Images")
                    if "photo_urls" in data and data["photo_urls"]:
                        photo_urls = data["photo_urls"]
                        
                        # Display up to 10 images
                        for i, photo_url in enumerate(photo_urls[:10]):
                            if photo_url and photo_url != "N/A":
                                st.write(f"**Image {i+1}:**")
                                
                                # Display the image
                                try:
                                    st.image(photo_url, caption=f"Image {i+1}", width=400)
                                except:
                                    st.write(f"Could not load image: {photo_url}")
                                
                                # Display the URL
                                st.write("**URL:**")
                                st.code(photo_url, language="text")
                                st.divider()
                            else:
                                st.write(f"**Image {i+1}:** Not available")
                                st.divider()
                    else:
                        st.write("No images available")
                    
                else:
                    error_msg = data.get("error", "Unknown error occurred") if data else "No data returned"
                    st.error(f"❌ Error: {error_msg}")
        else:
            st.warning("⚠️ Please enter both accommodation name and city")

elif pages == "Dining":
    st.title("🍽️ Dining Metadata Populator")
    st.write("Enter restaurant details to get comprehensive metadata")

    # Input fields
    col1, col2, col3 = st.columns(3)
    with col1:
        restaurant_name = st.text_input("Restaurant Name", placeholder="e.g., Toit Brewpub")
    with col2:
        city = st.text_input("City", placeholder="e.g., Bangalore")
    with col3:
        link = st.text_input("Link (Optional)", placeholder="https://example.com")

    if st.button("Get Metadata", type="primary"):
        if restaurant_name and city:
            with st.spinner("Fetching metadata..."):
                data = populate_dining(restaurant_name, city)

                if data and "error" not in data:
                    st.success("✅ Metadata retrieved successfully!")
                    
                    st.subheader("📋 Metadata Fields")
                    
                    # Define the preferred order of fields to display (if they exist)
                    preferred_field_order = [
                        ("Heading", "Heading"),
                        ("Destination", "Destination"),
                        ("User Message", "User Message"),
                        ("Restaurant Name", "Restaurant Name"),
                        ("Cuisines", "Cuisines"),
                        ("Price", "Price"),
                        ("Crew Exclusive Price", "Crew Exclusive Price"),
                        ("Why we love it", "Why we love it"),
                        ("Everything you need to know", "Everything you need to know"),
                        ("Timings", "Timings"),
                        ("Google Rating", "Google Rating"),
                        ("Location", "Location")
                    ]
                    
                    # Filter to only show fields that actually exist in the data
                    available_fields = [(display_name, key) for display_name, key in preferred_field_order if key in data]
                    
                    # Add any additional fields that might be in the data but not in our preferred list
                    for key, value in data.items():
                        if key not in [field[1] for field in available_fields] and key not in ['photo_urls', 'website', 'google_maps_url']:
                            # Format the key for display (replace underscores with spaces and title case)
                            display_name = key.replace('_', ' ').title()
                            available_fields.append((display_name, key))
                    
                    # Display each available field with copy functionality
                    for display_name, key in available_fields:
                        value = str(data[key])
                        
                        st.write(f"**{display_name}:**")
                        st.code(value, language="text")
                        st.divider()
                    
                    # Display images section
                    st.subheader("🖼️ Images")
                    if "photo_urls" in data and data["photo_urls"]:
                        photo_urls = data["photo_urls"]
                        
                        # Display up to 10 images
                        for i, photo_url in enumerate(photo_urls[:10]):
                            if photo_url and photo_url != "N/A":
                                st.write(f"**Image {i+1}:**")
                                
                                # Display the image
                                try:
                                    st.image(photo_url, caption=f"Image {i+1}", width=400)
                                except:
                                    st.write(f"Could not load image: {photo_url}")
                                
                                # Display the URL
                                st.write("**URL:**")
                                st.code(photo_url, language="text")
                                st.divider()
                            else:
                                st.write(f"**Image {i+1}:** Not available")
                                st.divider()
                    else:
                        st.write("No images available")
                    
                else:
                    error_msg = data.get("error", "Unknown error occurred") if data else "No data returned"
                    st.error(f"❌ Error: {error_msg}")
        else:
            st.warning("⚠️ Please enter both restaurant name and city")
