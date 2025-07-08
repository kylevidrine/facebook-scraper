#!/usr/bin/env python3
"""
Enhanced Facebook Event Scraper with OCR for Flyer Text Extraction
Monitors Facebook pages for event posts and extracts details from flyers
"""

import asyncio
import json
import re
import requests
import os
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from PIL import Image
import pytesseract
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FacebookEventScraper:
    def __init__(self):
        # Load configuration from environment variables
        self.webhook_url = os.getenv('N8N_WEBHOOK_URL', 'https://n8n.example.com/webhook/facebook-events')
        
        # Artists configuration - loaded from environment
        self.artists = self._load_artist_config()
        
        # Event-related keywords
        self.event_keywords = [
            'tonight', 'show', 'live', 'performance', 'gig', 'concert',
            'playing', 'music', 'venue', 'bar', 'club', 'festival',
            'friday', 'saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday'
        ]
        
        # Common venues - configurable via environment
        self.venues = self._load_venue_config()

    def _load_artist_config(self):
        """Load artist configuration from environment variables"""
        artists = {}
        
        # Try to load from JSON environment variable first
        artists_json = os.getenv('FACEBOOK_ARTISTS_CONFIG')
        if artists_json:
            try:
                return json.loads(artists_json)
            except json.JSONDecodeError:
                logger.error("Failed to parse FACEBOOK_ARTISTS_CONFIG JSON")
        
        # Fallback to individual environment variables
        artist_count = int(os.getenv('FACEBOOK_ARTIST_COUNT', '3'))
        
        for i in range(1, artist_count + 1):
            page_url = os.getenv(f'FACEBOOK_ARTIST_{i}_URL')
            name = os.getenv(f'FACEBOOK_ARTIST_{i}_NAME')
            category_id = os.getenv(f'FACEBOOK_ARTIST_{i}_CATEGORY_ID')
            
            if page_url and name and category_id:
                artists[page_url] = {
                    "name": name,
                    "category_id": int(category_id)
                }
        
        # Default configuration if no environment variables set
        if not artists:
            logger.warning("No artist configuration found in environment, using defaults")
            artists = {
                "facebook.com/example.artist.1": {
                    "name": "Example Artist 1",
                    "category_id": 4
                },
                "facebook.com/example.artist.2": {
                    "name": "Example Artist 2", 
                    "category_id": 5
                },
                "facebook.com/example.artist.3": {
                    "name": "Example Artist 3",
                    "category_id": 6
                }
            }
            
        return artists

    def _load_venue_config(self):
        """Load venue configuration from environment variables"""
        venues_config = os.getenv('FACEBOOK_VENUES_CONFIG')
        if venues_config:
            try:
                return json.loads(venues_config)
            except json.JSONDecodeError:
                logger.error("Failed to parse FACEBOOK_VENUES_CONFIG JSON")
        
        # Default venues if not configured
        return [
            'blue moon saloon', 'whiskey tales', 'artmosphere', 'feed and seed',
            'hurricane bar', 'social southern table', 'the grouse room',
            'legends bar', 'acadiana bar', 'cowboy country', 'chophouse',
            'el sid o', 'rock n bowl', 'spankys', 'jefferson street pub'
        ]

    def extract_text_from_image(self, img_url):
        """Extract text from an image URL using OCR"""
        try:
            if not img_url or 'scontent' not in img_url:
                return None
                
            logger.info(f"Processing image: {img_url[:100]}...")
            
            # Download image
            response = requests.get(img_url, timeout=10)
            response.raise_for_status()
            
            # Open image with PIL
            image = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(image, config='--psm 6')
            
            if extracted_text.strip():
                logger.info(f"Extracted text: {extracted_text[:200]}...")
                return extracted_text.strip()
                
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            
        return None

    def parse_flyer_text(self, text):
        """Parse extracted text from flyers for event details"""
        if not text:
            return {}
            
        text_lower = text.lower()
        details = {}
        
        # Date patterns
        date_patterns = [
            r'(\w+day),?\s+(\w+)\s+(\d+)(?:st|nd|rd|th)?',  # "Saturday, July 8th"
            r'(\w+)\s+(\d+)(?:st|nd|rd|th)?,?\s+(\d{4})',   # "July 8th, 2025"
            r'(\d+)/(\d+)/(\d{4})',                         # "7/8/2025"
            r'(\d+)-(\d+)-(\d{4})',                         # "7-8-2025"
            r'(\w+)\s+(\d+)(?:st|nd|rd|th)?'                # "July 8th"
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['extracted_date'] = match.group(0)
                logger.info(f"Found date in flyer: {match.group(0)}")
                break
        
        # Time patterns
        time_patterns = [
            r'(\d+):(\d+)\s*(pm|am)',                       # "8:30 PM"
            r'(\d+)\s*(pm|am)',                             # "8 PM"
            r'(\d+):(\d+)',                                 # "20:30"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['extracted_time'] = match.group(0)
                logger.info(f"Found time in flyer: {match.group(0)}")
                break
        
        # Venue detection
        for venue in self.venues:
            if venue in text_lower:
                details['extracted_venue'] = venue.title()
                logger.info(f"Found venue in flyer: {venue.title()}")
                break
        
        # Cover charge
        cover_patterns = [
            r'\$(\d+)\s*cover',
            r'cover\s*\$(\d+)',
            r'\$(\d+)\s*admission'
        ]
        
        for pattern in cover_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['cover_charge'] = f"${match.group(1)}"
                break
        
        return details

    async def process_post_images(self, page, post):
        """Process all images in a Facebook post"""
        try:
            # Look for images in the post
            img_elements = await post.query_selector_all('img')
            
            for img in img_elements:
                try:
                    # Get image source
                    img_url = await img.get_attribute('src')
                    
                    if img_url and 'scontent' in img_url:
                        # Extract text from image
                        extracted_text = self.extract_text_from_image(img_url)
                        
                        if extracted_text:
                            # Parse the extracted text
                            flyer_details = self.parse_flyer_text(extracted_text)
                            
                            if flyer_details:
                                logger.info(f"Found event details in flyer: {flyer_details}")
                                return flyer_details, extracted_text
                                
                except Exception as e:
                    logger.error(f"Error processing individual image: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing post images: {e}")
            
        return {}, ""

    def is_event_post(self, text):
        """Check if a post contains event-related content"""
        if not text:
            return False
            
        text_lower = text.lower()
        
        # Check for event keywords
        keyword_found = any(keyword in text_lower for keyword in self.event_keywords)
        
        # Check for venue mentions
        venue_found = any(venue in text_lower for venue in self.venues)
        
        # Check for time indicators
        time_found = bool(re.search(r'\d+\s*(pm|am)|tonight|today|\d+:\d+', text_lower))
        
        return keyword_found or venue_found or time_found

    async def scrape_facebook_page(self, page, page_url, artist_info):
        """Scrape a single Facebook page for event posts"""
        try:
            logger.info(f"Scraping {artist_info['name']} page: {page_url}")
            
            await page.goto(f"https://{page_url}")
            await page.wait_for_timeout(3000)
            
            # Find posts
            posts = await page.query_selector_all('[data-pagelet="FeedUnit_0"], [role="article"]')
            
            events_found = 0
            
            for i, post in enumerate(posts[:10]):  # Check first 10 posts
                try:
                    # Get post text
                    post_text_elem = await post.query_selector('[data-ad-preview="message"]')
                    post_text = ""
                    if post_text_elem:
                        post_text = await post_text_elem.inner_text()
                    
                    # Check if it's an event post
                    if not self.is_event_post(post_text):
                        continue
                    
                    logger.info(f"Found potential event post: {post_text[:100]}...")
                    
                    # Process images for flyer details
                    flyer_details, flyer_text = await self.process_post_images(page, post)
                    
                    # Prepare event data
                    event_data = {
                        "artist": artist_info['name'],
                        "category_id": artist_info['category_id'],
                        "post_text": post_text,
                        "flyer_text": flyer_text,
                        **flyer_details
                    }
                    
                    # Set title based on available information
                    if flyer_details.get('extracted_venue'):
                        event_data['title'] = f"{artist_info['name']} at {flyer_details['extracted_venue']}"
                    elif 'extracted_date' in flyer_details:
                        event_data['title'] = f"{artist_info['name']} Live Show - {flyer_details['extracted_date']}"
                    else:
                        event_data['title'] = f"{artist_info['name']} Live Show"
                    
                    # Set description
                    description_parts = []
                    if post_text:
                        description_parts.append(f"Facebook Post: {post_text}")
                    if flyer_text:
                        description_parts.append(f"Flyer Details: {flyer_text}")
                    if flyer_details.get('cover_charge'):
                        description_parts.append(f"Cover: {flyer_details['cover_charge']}")
                    
                    event_data['description'] = "\\n\\n".join(description_parts)
                    
                    # Send to webhook
                    await self.send_to_webhook(event_data)
                    events_found += 1
                    
                except Exception as e:
                    logger.error(f"Error processing post {i}: {e}")
                    continue
            
            logger.info(f"Found {events_found} events for {artist_info['name']}")
            return events_found
            
        except Exception as e:
            logger.error(f"Error scraping {artist_info['name']} page: {e}")
            return 0

    async def send_to_webhook(self, event_data):
        """Send event data to N8N webhook"""
        try:
            logger.info(f"Sending event to webhook: {event_data['title']}")
            
            response = requests.post(
                self.webhook_url,
                json=event_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully sent event: {event_data['title']}")
            else:
                logger.error(f"Webhook error {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending to webhook: {e}")

    async def run(self):
        """Main scraper execution"""
        logger.info("Starting Facebook Event Scraper with OCR")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            try:
                total_events = 0
                
                for page_url, artist_info in self.artists.items():
                    page = await browser.new_page()
                    
                    try:
                        events_count = await self.scrape_facebook_page(page, page_url, artist_info)
                        total_events += events_count
                        
                    finally:
                        await page.close()
                        await asyncio.sleep(2)  # Rate limiting
                
                logger.info(f"Scraping completed. Total events found: {total_events}")
                
            finally:
                await browser.close()

if __name__ == "__main__":
    scraper = FacebookEventScraper()
    asyncio.run(scraper.run())