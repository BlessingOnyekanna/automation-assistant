"""
Automation Assistant - CSV Version (Secure)
============================================
A professional data collection automation tool that fetches data from public APIs
and saves it to CSV files for easy analysis and reporting.

This version uses environment variables for secure API key management.

Author: Blessing Onyekanna
Date: 2025
"""

import requests
import csv
import json
from datetime import datetime
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class AutomationAssistant:
    """
    Main class for automating data collection from various public APIs.
    Supports weather data, cryptocurrency prices, and latest news.
    """
    
    def __init__(self, data_folder="data"):
        """
        Initialize the Automation Assistant.
        
        Args:
            data_folder (str): Folder name where CSV files will be saved
        """
        self.data_folder = data_folder
        # Create data folder if it doesn't exist
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
            print(f"✓ Created '{data_folder}' folder for storing data")
    
    
    def fetch_weather_data(self, city="London"):
        """
        Fetch current weather data from Open-Meteo API (free, no key required).
        
        Args:
            city (str): City name to get weather for
            
        Returns:
            dict: Weather data or None if request fails
        """
        print(f"\n📡 Fetching weather data for {city}...")
        
        # Using Open-Meteo free API (no key required for basic access)
        url = f"https://api.open-meteo.com/v1/forecast"
        
        # First, we need to geocode the city name
        geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        
        try:
            # Get city coordinates
            geo_response = requests.get(geocode_url, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data.get('results'):
                print(f"❌ City '{city}' not found")
                return None
            
            lat = geo_data['results'][0]['latitude']
            lon = geo_data['results'][0]['longitude']
            
            # Get weather data
            params = {
                'latitude': lat,
                'longitude': lon,
                'current_weather': 'true',
                'temperature_unit': 'celsius'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract and format the data
            weather = data['current_weather']
            result = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'city': city,
                'temperature_celsius': weather['temperature'],
                'windspeed_kmh': weather['windspeed'],
                'weather_code': weather['weathercode'],
                'latitude': lat,
                'longitude': lon
            }
            
            print(f"✓ Successfully fetched weather data for {city}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching weather data: {e}")
            return None
    
    
    def fetch_crypto_prices(self, coins=None):
        """
        Fetch cryptocurrency prices from CoinGecko API (free, no key required).
        
        Args:
            coins (list): List of cryptocurrency IDs (default: bitcoin, ethereum, cardano)
            
        Returns:
            list: List of crypto price data or None if request fails
        """
        if coins is None:
            coins = ['bitcoin', 'ethereum', 'cardano']
        
        print(f"\n📡 Fetching cryptocurrency prices for {', '.join(coins)}...")
        
        # CoinGecko free API endpoint
        url = "https://api.coingecko.com/api/v3/simple/price"
        
        params = {
            'ids': ','.join(coins),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Format the data into a list of dictionaries
            results = []
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            for coin_id, coin_data in data.items():
                results.append({
                    'timestamp': timestamp,
                    'cryptocurrency': coin_id.title(),
                    'price_usd': coin_data.get('usd', 0),
                    'market_cap_usd': coin_data.get('usd_market_cap', 0),
                    'change_24h_percent': coin_data.get('usd_24h_change', 0)
                })
            
            print(f"✓ Successfully fetched prices for {len(results)} cryptocurrencies")
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching crypto data: {e}")
            return None
    
    
    def fetch_news(self, category="technology", country="us"):
        """
        Fetch latest news headlines from NewsAPI.org.
        Requires NEWS_API_KEY environment variable to be set.
        
        Get your free API key from https://newsapi.org/register
        Then add it to your .env file: NEWS_API_KEY=your-key-here
        
        Args:
            category (str): News category (business, technology, science, etc.)
            country (str): Country code (us, gb, ca, etc.)
            
        Returns:
            list: List of news articles or None if request fails
        """
        print(f"\n📡 Fetching latest {category} news from {country.upper()}...")
        
        # Get API key from environment variable
        api_key = os.getenv('NEWS_API_KEY')
        
        if not api_key:
            print("\n⚠️  NEWS_API_KEY not found!")
            print("   To use the News API:")
            print("   1. Get a free API key from https://newsapi.org/register")
            print("   2. Create a .env file in your project folder")
            print("   3. Add this line: NEWS_API_KEY=your-actual-key")
            print("   4. Run the script again")
            return None
        
        url = "https://newsapi.org/v2/top-headlines"
        
        params = {
            'apiKey': api_key,
            'category': category,
            'country': country,
            'pageSize': 10  # Get top 10 articles
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] != 'ok':
                print(f"❌ API returned error: {data.get('message', 'Unknown error')}")
                print("   Check your API key is valid and not expired")
                return None
            
            # Format the articles
            results = []
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            for article in data['articles']:
                results.append({
                    'timestamp': timestamp,
                    'title': article['title'],
                    'source': article['source']['name'],
                    'author': article.get('author', 'Unknown'),
                    'published_at': article['publishedAt'],
                    'url': article['url'],
                    # NEW:
                    'description': (article.get('description') or '')[:200]
                })
            
            print(f"✓ Successfully fetched {len(results)} news articles")
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching news data: {e}")
            return None
    
    
    def save_to_csv(self, data, filename):
        """
        Save data to a CSV file in the data folder.
        
        Args:
            data (list or dict): Data to save (list of dicts or single dict)
            filename (str): Name of the CSV file
        """
        if data is None:
            print("❌ No data to save")
            return
        
        # Convert single dict to list for consistent processing
        if isinstance(data, dict):
            data = [data]
        
        if not data:
            print("❌ Empty data list")
            return
        
        filepath = os.path.join(self.data_folder, filename)
        
        try:
            # Check if file exists to determine if we need to write headers
            file_exists = os.path.exists(filepath)
            
            with open(filepath, 'a', newline='', encoding='utf-8') as csvfile:
                # Get column names from the first data item
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header only if file is new
                if not file_exists:
                    writer.writeheader()
                
                # Write all data rows
                writer.writerows(data)
            
            print(f"✓ Data saved to '{filepath}'")
            print(f"  ({len(data)} record(s) added)")
            
        except Exception as e:
            print(f"❌ Error saving to CSV: {e}")
    
    
    def run_weather_automation(self, cities=None):
        """
        Run weather data collection automation.
        
        Args:
            cities (list): List of cities to fetch weather for
        """
        if cities is None:
            cities = ["London", "New York", "Tokyo"]
        
        print("\n" + "="*60)
        print("🌤️  WEATHER DATA AUTOMATION")
        print("="*60)
        
        for city in cities:
            weather_data = self.fetch_weather_data(city)
            if weather_data:
                self.save_to_csv(weather_data, "weather_data.csv")
            time.sleep(1)  # Be nice to the API
    
    
    def run_crypto_automation(self):
        """Run cryptocurrency price collection automation."""
        print("\n" + "="*60)
        print("₿  CRYPTOCURRENCY AUTOMATION")
        print("="*60)
        
        crypto_data = self.fetch_crypto_prices()
        if crypto_data:
            self.save_to_csv(crypto_data, "crypto_prices.csv")
    
    
    def run_news_automation(self, category="technology"):
        """
        Run news collection automation.
        
        Args:
            category (str): News category to fetch
        """
        print("\n" + "="*60)
        print("📰 NEWS AUTOMATION")
        print("="*60)
        
        news_data = self.fetch_news(category=category)
        if news_data:
            self.save_to_csv(news_data, "latest_news.csv")


def main():
    """
    Main function to run the automation assistant.
    Demonstrates all three API options.
    """
    print("\n" + "="*60)
    print("🤖 AUTOMATION ASSISTANT - CSV VERSION")
    print("="*60)
    print("\nThis tool automates data collection from public APIs")
    print("and saves the results to organized CSV files.\n")
    
    # Initialize the assistant
    assistant = AutomationAssistant()
    
    # Display menu
    print("\nChoose which automation to run:")
    print("1. Weather Data (Free, no API key needed)")
    print("2. Cryptocurrency Prices (Free, no API key needed)")
    print("3. Latest News (Requires NEWS_API_KEY in .env file)")
    print("4. Run All Automations")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-4): ").strip()
    
    if choice == "1":
        assistant.run_weather_automation()
    elif choice == "2":
        assistant.run_crypto_automation()
    elif choice == "3":
        assistant.run_news_automation()
    elif choice == "4":
        assistant.run_weather_automation()
        assistant.run_crypto_automation()
        assistant.run_news_automation()
    elif choice == "0":
        print("\n👋 Goodbye!")
        return
    else:
        print("\n❌ Invalid choice. Please run the script again.")
        return
    
    print("\n" + "="*60)
    print("✅ AUTOMATION COMPLETED!")
    print("="*60)
    print(f"\n📁 Check the '{assistant.data_folder}' folder for your CSV files")
    print("   You can open them in Excel, Google Sheets, or any spreadsheet app")


if __name__ == "__main__":
    main()