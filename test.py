from accommodation.accommodation_populator import populate_accommodation
import json

print(json.dumps(populate_accommodation("The Oberoi", "Bangalore"), indent=4))
