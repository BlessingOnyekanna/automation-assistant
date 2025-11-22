"""
Automation Assistant - Google Sheets Version
=============================================
A professional data collection automation tool that fetches data from public APIs
and saves it directly to Google Sheets for real-time collaboration and reporting.

Author: Your Name
Date: 2025
"""

import requests
import json
from datetime import datetime
import time
import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class AutomationAssistantGSheets:
    """
    Main class for automating data collection from various public APIs
    and saving to Google Sheets.
    """
    
    def __init__(self, credentials_file, spreadsheet_id):
        """
        Initialize the Automation Assistant with Google Sheets integration.
        
        Args:
            credentials_file (str): Path to Google service account JSON file
            spreadsheet_id (str): Google Sheets spreadsheet ID
        """
        # Load environment variables
        load_dotenv()  # ← ADD THIS LINE
        
        self.spreadsheet_id = spreadsheet_id
        self.service = self._authenticate_google_sheets(credentials_file)
        print("✓ Connected to Google Sheets successfully")
        
    def _authenticate_google_sheets(self, credentials_file):
        """
        Authenticate with Google Sheets API using service account.
        
        Args:
            credentials_file (str): Path to service account credentials JSON
            
        Returns:
            Resource: Google Sheets API service object
        """
        try:
            # Define the scopes
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            
            # Load credentials from the service account file
            creds = Credentials.from_service_account_file(
                credentials_file, 
                scopes=SCOPES
            )
            
            # Build the service
            service = build('sheets', 'v4', credentials=creds)
            
            return service
            
        except Exception as e:
            print(f"❌ Error authenticating with Google Sheets: {e}")
            raise
    
    
    def fetch_weather_data(self, city="London"):
        """
        Fetch current weather data from Open-Meteo API (free, no key required).
        
        Args:
            city (str): City name to get weather for
            
        Returns:
            dict: Weather data or None if request fails
        """
        print(f"\n📡 Fetching weather data for {city}...")
        
        url = f"https://api.open-meteo.com/v1/forecast"
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
            coins (list): List of cryptocurrency IDs
            
        Returns:
            list: List of crypto price data or None if request fails
        """
        if coins is None:
            coins = ['bitcoin', 'ethereum', 'cardano']
        
        print(f"\n📡 Fetching cryptocurrency prices for {', '.join(coins)}...")
        
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
        Fetch latest news headlines from NewsAPI.org (requires free API key).
        
        Args:
            category (str): News category
            country (str): Country code
            
        Returns:
            list: List of news articles or None if request fails
        """
        print(f"\n📡 Fetching latest {category} news from {country.upper()}...")
        
        # Get API key from environment variable
        api_key = os.getenv('NEWS_API_KEY')

        if not api_key:
            print("⚠️  NEWS_API_KEY not found!")
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
            'pageSize': 10
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] != 'ok':
                print(f"❌ API returned error: {data.get('message', 'Unknown error')}")
                return None
            
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
                    'description': article.get('description', '')[:200]
                })
            
            print(f"✓ Successfully fetched {len(results)} news articles")
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching news data: {e}")
            return None
    
    
    def save_to_sheet(self, data, sheet_name):
        """
        Save data to a Google Sheet.
        Creates a new sheet if it doesn't exist, appends if it does.
        
        Args:
            data (list or dict): Data to save
            sheet_name (str): Name of the sheet tab
        """
        if data is None:
            print("❌ No data to save")
            return
        
        # Convert single dict to list
        if isinstance(data, dict):
            data = [data]
        
        if not data:
            print("❌ Empty data list")
            return
        
        try:
            # Get existing sheets
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            existing_sheets = [sheet['properties']['title'] 
                             for sheet in spreadsheet.get('sheets', [])]
            
            # Create sheet if it doesn't exist
            if sheet_name not in existing_sheets:
                self._create_sheet(sheet_name)
                # Add headers
                headers = list(data[0].keys())
                self._write_to_sheet(sheet_name, [headers], "A1")
                print(f"✓ Created new sheet: '{sheet_name}'")
            
            # Prepare data rows
            rows = []
            for item in data:
                # Ensure all values are strings or numbers
                row = [str(v) if v is not None else '' for v in item.values()]
                rows.append(row)
            
            # Append data
            self._append_to_sheet(sheet_name, rows)
            
            print(f"✓ Added {len(rows)} row(s) to '{sheet_name}' in Google Sheets")
            
        except HttpError as e:
            print(f"❌ Error saving to Google Sheets: {e}")
    
    
    def _create_sheet(self, sheet_name):
        """Create a new sheet in the spreadsheet."""
        try:
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=request_body
            ).execute()
            
        except HttpError as e:
            print(f"❌ Error creating sheet: {e}")
            raise
    
    
    def _write_to_sheet(self, sheet_name, values, range_start):
        """Write values to a specific range in the sheet."""
        try:
            range_name = f"{sheet_name}!{range_start}"
            body = {'values': values}
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
        except HttpError as e:
            print(f"❌ Error writing to sheet: {e}")
            raise
    
    
    def _append_to_sheet(self, sheet_name, values):
        """Append values to the end of the sheet."""
        try:
            range_name = f"{sheet_name}!A:A"
            body = {'values': values}
            
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
        except HttpError as e:
            print(f"❌ Error appending to sheet: {e}")
            raise
    
    
    def run_weather_automation(self, cities=None):
        """Run weather data collection automation."""
        if cities is None:
            cities = ["London", "New York", "Tokyo"]
        
        print("\n" + "="*60)
        print("🌤️  WEATHER DATA AUTOMATION")
        print("="*60)
        
        for city in cities:
            weather_data = self.fetch_weather_data(city)
            if weather_data:
                self.save_to_sheet(weather_data, "Weather Data")
            time.sleep(1)
    
    
    def run_crypto_automation(self):
        """Run cryptocurrency price collection automation."""
        print("\n" + "="*60)
        print("₿  CRYPTOCURRENCY AUTOMATION")
        print("="*60)
        
        crypto_data = self.fetch_crypto_prices()
        if crypto_data:
            self.save_to_sheet(crypto_data, "Crypto Prices")
    
    
    def run_news_automation(self, category="technology"):
        """Run news collection automation."""
        print("\n" + "="*60)
        print("📰 NEWS AUTOMATION")
        print("="*60)
        
        news_data = self.fetch_news(category=category)
        if news_data:
            self.save_to_sheet(news_data, "Latest News")


def main():
    """
    Main function to run the automation assistant with Google Sheets.
    """
    print("\n" + "="*60)
    print("🤖 AUTOMATION ASSISTANT - GOOGLE SHEETS VERSION")
    print("="*60)
    print("\nThis tool automates data collection from public APIs")
    print("and saves the results directly to Google Sheets.\n")
    
    # Configuration
    CREDENTIALS_FILE = "credentials.json"  # Your service account JSON file
    SPREADSHEET_ID =  "1ou84Bg_HXvRx45cwc4xyh7Yza-b-uPkXJdqo7EiC3RE"  # Your Google Sheets ID
    
    # Check configuration
    if SPREADSHEET_ID == "YOUR_SPREADSHEET_ID":
        print("⚠️  SETUP REQUIRED:")
        print("1. Create a Google Cloud project and enable Sheets API")
        print("2. Create a service account and download credentials.json")
        print("3. Create a Google Sheet and share it with the service account email")
        print("4. Update SPREADSHEET_ID in this script")
        print("\nSee README.md for detailed setup instructions")
        return
    
    try:
        # Initialize the assistant
        assistant = AutomationAssistantGSheets(CREDENTIALS_FILE, SPREADSHEET_ID)
        
        # Display menu
        print("\nChoose which automation to run:")
        print("1. Weather Data (Free, no API key needed)")
        print("2. Cryptocurrency Prices (Free, no API key needed)")
        print("3. Latest News (Requires free API key from newsapi.org)")
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
        print(f"\n📊 Check your Google Sheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()
