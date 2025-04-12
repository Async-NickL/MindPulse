import requests
import math
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key from environment variable
OPENCAGE_API_KEY = os.getenv('OPENCAGE_API_KEY')

# Function to get latitude & longitude from city name
def get_coordinates(location):
    """Convert user location (city/address) to latitude & longitude using OpenCage API"""
    url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={OPENCAGE_API_KEY}"
    response = requests.get(url).json()
    
    if response and response.get("results"):
        lat = response["results"][0]["geometry"]["lat"]
        lon = response["results"][0]["geometry"]["lng"]
        print(f"📍 Detected Location: {response['results'][0]['formatted']} ({lat}, {lon})")  # DEBUGGING
        return lat, lon
    else:
        print("❌ Location not found.")
        return None, None

# Function to fetch nearby medical facilities
def get_nearby_medical_places(lat, lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
        node(around:5000,{lat},{lon})["amenity"="Mental Health"];
        node(around:5000,{lat},{lon})["amenity"="clinic"];
        node(around:5000,{lat},{lon})["amenity"="doctors"];
        node(around:5000,{lat},{lon})["amenity"="pharmacy"];
        node(around:5000,{lat},{lon})["healthcare"];
    );
    out body;
    """
    
    response = requests.get(overpass_url, params={"data": query})
    
    try:
        data = response.json()
        return data.get("elements", [])  
    except requests.exceptions.JSONDecodeError:
        print("ERROR: Overpass API request failed.")
        return []

# Function to format the output of facilities
def format_facilities(facilities, user_lat, user_lon):
    formatted_list = []
    total_distance = 0
    for facility in facilities:
        name = facility.get("tags", {}).get("name", "Unnamed")
        amenity = facility.get("tags", {}).get("amenity", "Unknown")
        lat = facility.get("lat", "Unknown")
        lon = facility.get("lon", "Unknown")
        
        # Calculate distance to the clinic
        distance = haversine(user_lat, user_lon, lat, lon)
        total_distance += distance
        
        formatted_list.append(f"📍 {name} (Type: {amenity}) - Location: ({lat}, {lon}) - Distance: {distance:.2f} km")
    
    return formatted_list, total_distance

# Function to calculate distance between two coordinates
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c  # Distance in km

# Function to describe relative position
def get_direction(lat1, lon1, lat2, lon2):
    dlat, dlon = lat2 - lat1, lon2 - lon1
    if abs(dlat) > abs(dlon):
        return "North" if dlat > 0 else "South"
    else:
        return "East" if dlon > 0 else "West"

if __name__ == "__main__":
    location = input("Enter your location (city name or address): ")
    lat, lon = get_coordinates(location)
    if lat and lon:
        facilities = get_nearby_medical_places(lat, lon)
        formatted_facilities, total_distance = format_facilities(facilities, lat, lon)
        
        if formatted_facilities:
            print("Nearby Medical Facilities:")
            for facility in formatted_facilities:
                print(facility)
            print(f"\nTotal Distance to Clinics: {total_distance:.2f} km")
        else:
            print("No medical facilities found nearby.")