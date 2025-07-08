# 🎵 Facebook Event Scraper with OCR

An intelligent Facebook scraper that monitors artist pages for event announcements and extracts detailed information from event flyers using OCR technology.

## ✨ Features

- **🔍 Smart Event Detection**: Automatically identifies event-related posts on Facebook pages
- **📸 OCR Flyer Analysis**: Extracts dates, times, venues, and details from event flyers
- **🎯 Artist-Specific Monitoring**: Configurable artist pages with category assignments
- **🔗 N8N Integration**: Sends structured event data to N8N workflows
- **⏰ Automated Scheduling**: Runs on configurable intervals
- **🐳 Docker Ready**: Containerized for easy deployment

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/facebook-scraper.git
cd facebook-scraper
```

### 2. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your settings
```

### 3. Deploy with Docker

```bash
chmod +x deploy.sh
./deploy.sh
```

### 4. Test Manual Run

```bash
docker exec -it facebook-event-scraper python scraper.py
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

#### Required Settings

```bash
# N8N Webhook URL - where to send event data
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/facebook-events

# Artist Configuration (JSON format)
FACEBOOK_ARTISTS_CONFIG={
  "facebook.com/artist-page": {
    "name": "Artist Name",
    "category_id": 4
  }
}
```

#### Optional Settings

```bash
# Scraping interval (seconds, default: 21600 = 6 hours)
SCRAPE_INTERVAL=21600

# Venue list for detection in flyers
FACEBOOK_VENUES_CONFIG=["venue1", "venue2", "venue3"]
```

### Artist Configuration

Two methods to configure artists:

#### Method 1: JSON Configuration (Recommended)

```bash
FACEBOOK_ARTISTS_CONFIG={
  "facebook.com/mike.broussard.627050": {
    "name": "Mike Broussard",
    "category_id": 4
  },
  "facebook.com/dustinsonniermusic": {
    "name": "Dustin Sonnier",
    "category_id": 6
  }
}
```

#### Method 2: Individual Variables

```bash
FACEBOOK_ARTIST_COUNT=2
FACEBOOK_ARTIST_1_URL=facebook.com/mike.broussard.627050
FACEBOOK_ARTIST_1_NAME=Mike Broussard
FACEBOOK_ARTIST_1_CATEGORY_ID=4
FACEBOOK_ARTIST_2_URL=facebook.com/dustinsonniermusic
FACEBOOK_ARTIST_2_NAME=Dustin Sonnier
FACEBOOK_ARTIST_2_CATEGORY_ID=6
```

## 🏗️ Architecture

### Components

1. **Facebook Scraper**: Uses Playwright to navigate Facebook pages
2. **OCR Engine**: Tesseract extracts text from event flyers
3. **Event Parser**: Intelligent parsing of dates, times, and venues
4. **N8N Integration**: Sends structured data to workflow automation
5. **Docker Container**: Isolated, reproducible environment

### Data Flow

```
Facebook Pages → Playwright Scraper → OCR Analysis → Event Parser → N8N Webhook → WordPress
```

### Event Data Structure

The scraper sends this JSON structure to your N8N webhook:

```json
{
  "artist": "Artist Name",
  "category_id": 4,
  "title": "Artist Name at Venue Name",
  "post_text": "Original Facebook post text",
  "flyer_text": "OCR extracted text from flyer",
  "extracted_date": "Saturday, July 8th",
  "extracted_time": "8:00 PM",
  "extracted_venue": "Blue Moon Saloon",
  "cover_charge": "$10",
  "description": "Combined description with all details"
}
```

## 🔧 Manual Operations

### Test Scraper

```bash
docker exec -it facebook-event-scraper python scraper.py
```

### View Logs

```bash
docker-compose logs -f facebook-event-scraper
```

### Restart Container

```bash
docker-compose restart facebook-event-scraper
```

### Update Configuration

```bash
nano .env
docker-compose restart facebook-event-scraper
```

## 📊 Monitoring

### Check Container Status

```bash
docker-compose ps
```

### Monitor Resource Usage

```bash
docker stats facebook-event-scraper
```

### Debug OCR Issues

```bash
docker exec -it facebook-event-scraper tesseract --version
```

## 🛠️ Development

### Local Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

### Run Locally

```bash
# Set environment variables
export N8N_WEBHOOK_URL="http://localhost:5678/webhook/facebook-events"
export FACEBOOK_ARTISTS_CONFIG='{"facebook.com/test": {"name": "Test", "category_id": 1}}'

# Run scraper
python scraper.py
```

## 🎯 N8N Integration

### Webhook Setup

1. Create webhook node in N8N
2. Set URL in `N8N_WEBHOOK_URL` environment variable
3. Process incoming event data
4. Create WordPress events with extracted information

### Example N8N Workflow

```
Webhook → Process Data → Create WordPress Event → Send Notification
```

## 📝 Customization

### Adding New Artists

Edit `.env` file:

```bash
FACEBOOK_ARTISTS_CONFIG={
  "existing-artists": "...",
  "facebook.com/new-artist-page": {
    "name": "New Artist",
    "category_id": 7
  }
}
```

Restart container:

```bash
docker-compose restart facebook-event-scraper
```

### Adding New Venues

Update venue list in `.env`:

```bash
FACEBOOK_VENUES_CONFIG=["existing venues", "new venue name"]
```

### Adjusting Scraping Frequency

Change interval in `.env`:

```bash
SCRAPE_INTERVAL=7200  # 2 hours
```

## 🔒 Security

- **No sensitive data in repository**: All configuration via environment variables
- **Private .env file**: Never committed to Git
- **Minimal permissions**: Container runs with non-root user
- **Rate limiting**: Built-in delays to respect Facebook's servers

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Troubleshooting

### Common Issues

**Container won't start**

- Check `.env` file exists and is configured
- Verify Docker and docker-compose are installed

**No events detected**

- Check artist Facebook URLs are accessible
- Verify N8N webhook URL is reachable
- Check logs: `docker-compose logs facebook-event-scraper`
- Test manually: `docker exec -it facebook-event-scraper python scraper.py`

**OCR not working**

- Verify Tesseract is installed: `docker exec -it facebook-event-scraper tesseract --version`
- Check image URLs in logs
- Ensure images contain readable text

**Facebook blocking requests**

- Scraper uses realistic delays to avoid blocking
- If blocked, wait and try again later
- Consider adjusting scraping frequency

### Debug Commands

```bash
# Check container status
docker ps | grep facebook-event-scraper

# View recent logs
docker-compose logs --tail=50 facebook-event-scraper

# Interactive container access
docker exec -it facebook-event-scraper /bin/bash

# Test OCR functionality
docker exec -it facebook-event-scraper python -c "import pytesseract; print('OCR working')"

# Test webhook connectivity
curl -X POST $N8N_WEBHOOK_URL -H "Content-Type: application/json" -d '{"test": "data"}'
```

## 📈 Performance Tips

- **Adjust scraping interval** based on artist posting frequency
- **Monitor resource usage** with `docker stats`
- **Limit concurrent processing** for stability
- **Use SSD storage** for better Docker performance

## 🔄 Updates

### Updating the Scraper

```bash
git pull origin main
./deploy.sh
```

### Backup Configuration

```bash
# Backup your .env file
cp .env .env.backup.$(date +%Y%m%d)

# Store in secure location outside repository
```

## 🌟 Advanced Features

### Custom Event Keywords

Modify `event_keywords` in scraper.py to detect different types of posts:

```python
self.event_keywords = [
    'tonight', 'show', 'live', 'performance', 'gig', 'concert',
    'playing', 'music', 'venue', 'bar', 'club', 'festival',
    # Add custom keywords here
    'acoustic', 'unplugged', 'showcase'
]
```

### Venue Detection

Add local venues to your configuration:

```bash
FACEBOOK_VENUES_CONFIG=[
  "your local venue",
  "another music spot",
  "community center"
]
```

### Multiple Webhook Endpoints

Modify scraper to send to different endpoints based on artist or event type.

## 🎵 Use Cases

- **Music Venue Websites**: Automatically populate event calendars
- **Artist Management**: Track all artists' events in one place
- **Music Blogs**: Generate content about upcoming shows
- **Fan Notifications**: Alert fans about new events
- **Event Aggregation**: Combine multiple sources into unified calendar

## 📞 Support

- **Issues**: Create GitHub issue with logs and configuration details
- **Feature Requests**: Open GitHub discussion
- **Security Issues**: Email privately (don't create public issues)

## 🙏 Acknowledgments

- **Playwright Team**: For excellent browser automation
- **Tesseract OCR**: For powerful text recognition
- **Python Community**: For amazing libraries and tools
- **Acadiana Music Scene**: For the inspiration

---

**Made with ❤️ for the music community**
