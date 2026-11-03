# 🐝 NewsHive - AI-Powered News Intelligence Platform

> *Collect. Process. Organize. Like a hive of intelligent bees gathering news from across the web.*

An enterprise-grade news aggregation and intelligence system that scrapes, processes, and categorizes business news from multiple sources using AWS Bedrock AI, Google Search API, RSS feeds, and advanced NLP techniques.

## 🎯 Overview

This platform automates the collection and analysis of business news articles from various Indian news sources. It leverages AI-powered summarization, keyword extraction, and semantic similarity detection to organize news content into a structured PostgreSQL database with vector embeddings for intelligent deduplication and search capabilities.

## ✨ Key Features

### 🔍 **Multi-Source News Collection**
- **RSS Feed Integration**: 20+ Indian news sources including Economic Times, Live Mint, The Hindu, India Today, and more
- **Google Search API**: Custom search engines for targeted news discovery across multiple publications
- **Tor Network Support**: Privacy-focused web scraping with rotating identities
- **Playwright Integration**: JavaScript-enabled dynamic content extraction

### 🤖 **AI-Powered Processing**
- **AWS Bedrock Integration**: Leverages large language models for:
  - **Intelligent Summarization**: Generates concise summaries of articles
  - **Keyword Extraction**: Identifies key topics and terms from content
  - **Automated Classification**: Categorizes news into taxonomy-based categories and subcategories
  - **Business Lead Classification**: Identifies potential business opportunities

### 🧠 **Semantic Intelligence**
- **Vector Embeddings**: Uses GTE (General Text Embeddings) for semantic representation
- **Similarity Detection**: Identifies duplicate and similar articles across sources
- **FAISS Integration**: Efficient similarity search with bi-encoder models
- **Configurable Thresholds**: Fine-tuned similarity matching (85% exact, 75% somewhat similar)

### 💾 **Robust Database Architecture**
- **PostgreSQL with pgvector**: Vector similarity search capabilities
- **Normalized Schema**: Efficient storage with 8 specialized tables
  - Primary/Secondary article tables for deduplication
  - Vector embeddings table for semantic search
  - Category and keywords tables for organization
  - Scraping reports for monitoring and analytics
- **Automated Retry Logic**: Resilient database operations

### 📊 **Monitoring & Reporting**
- **JSON Structured Logging**: Comprehensive event tracking
- **Scraping Reports**: Detailed statistics on success/failure rates
- **Search Term Tracking**: Prevents redundant processing
- **Failed URL Tracking**: Identifies problematic sources

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     News Sources                            │
│  RSS Feeds │ Google Search │ Custom Search Engines         │
└──────────────────┬──────────────────────────────────────────┘
                   │
         ┌─────────▼─────────┐
         │  Web Scraping     │
         │  - Playwright     │
         │  - Tor Network    │
         │  - BeautifulSoup  │
         └─────────┬─────────┘
                   │
         ┌─────────▼──────────┐
         │  Content Cleaning  │
         │  & Extraction      │
         └─────────┬──────────┘
                   │
         ┌─────────▼──────────┐
         │   AWS Bedrock AI   │
         │  - Summarization   │
         │  - Classification  │
         │  - Keyword Extract │
         └─────────┬──────────┘
                   │
         ┌─────────▼──────────┐
         │ Embedding Generation│
         │  (GTE-base)        │
         └─────────┬──────────┘
                   │
         ┌─────────▼──────────┐
         │ Similarity Check   │
         │  (FAISS + Vector)  │
         └─────────┬──────────┘
                   │
         ┌─────────▼──────────┐
         │   PostgreSQL       │
         │   (with pgvector)  │
         └────────────────────┘
```

## 📁 Project Structure

```
NewsHive/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
│
├── config/                     # Configuration management
│   ├── settings.py            # Environment variables & configs
│   ├── models.py              # Pydantic/dataclass models
│   ├── schema.py              # Data validation schemas
│   ├── taxonomy_parser.py     # Category taxonomy handler
│   └── cat.txt                # Category definitions
│
├── web_scrapping/             # Web scraping modules
│   ├── scrap_specific_04.py   # Source-specific scrapers
│   ├── scarping_03.py         # Main scraper manager
│   ├── playwright_scraper.py  # JavaScript-enabled scraping
│   ├── get_content.py         # Content extraction
│   └── scrape_metadata.py     # Metadata extraction
│
├── rss/                       # RSS feed processors
│   ├── ALL_RSS.py             # Generic RSS parser
│   ├── economictimes.py       # Economic Times handler
│   ├── etnow.py               # ET Now handler
│   └── [20+ source-specific handlers]
│
├── bedrock/                   # AWS Bedrock AI integration
│   ├── summary.py             # Text summarization
│   ├── keyword_extractor.py   # Keyword extraction
│   ├── news_classifier.py     # Category classification
│   ├── lead_classifier.py     # Business lead detection
│   └── bedrock_process.py     # Core Bedrock interface
│
├── processing/                # Data processing pipeline
│   ├── processing_flow.py     # Main processing orchestration
│   ├── process_rss.py         # RSS-specific processing
│   ├── embedding_similarity.py # Semantic similarity
│   └── search_term_tracker.py # Search term management
│
├── DATABASE/                  # Database operations
│   ├── create.py              # Schema creation
│   ├── insertion.py           # Data insertion logic
│   ├── fetch.py               # Data retrieval
│   ├── getDatabase.py         # Connection management
│   └── INSERT/                # Specialized inserters
│       ├── scraped_data_db.py
│       ├── keywords_table.py
│       ├── search_term_table.py
│       └── reports.py
│
├── fetch/                     # External data fetching
│   └── google_search.py       # Google Custom Search API
│
├── tor/                       # Tor network integration
│   └── tor_session_manager.py # Tor connection management
│
├── logs/                      # Logging utilities
│   └── json_log.py            # Structured JSON logging
│
├── data/                      # Output data storage
│   ├── search_results.json    # Google search results
│   ├── processed_terms.json   # Processed search terms
│   └── [source]_[category].json # RSS feed data
│
└── reports/                   # Generated reports
    └── [date].txt             # Daily scraping reports
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **PostgreSQL 12+** with pgvector extension
- **Tor** (for anonymous scraping)
- **AWS Account** with Bedrock access
- **Google Cloud Account** with Custom Search API enabled

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/NewsHive.git
cd NewsHive
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Playwright browsers**
```bash
playwright install chromium
```

4. **Set up PostgreSQL with pgvector**
```sql
CREATE EXTENSION vector;
CREATE EXTENSION "uuid-ossp";
```

5. **Configure environment variables**

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/news_db

# AWS Bedrock
AWS_MODEL_REGION=us-east-1
LLM_MODEL_NEWSHIVE=anthropic.claude-3-sonnet-20240229-v1:0

# Google Search API
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_CLOUD_LOCATION=global
GOOGLE_API_KEY=your-api-key
NEWSHIVE_GOOGLE_ENGINE_ID=your-engine-id

# Source-Specific Engine IDs
BS_ENGINE_ID=business-standard-engine-id
ECO_ENGINE_ID=economic-times-engine-id
HINDU_ENGINE_ID=the-hindu-engine-id
# ... [add all other engine IDs]

# Database Connection Settings
MAX_DB_RETRIES=5
RETRY_DELAY_SECONDS=2
DB_CONN_TIMEOUT=10
```

6. **Initialize the database**
```bash
python DATABASE/create.py
```

### Usage

**Run the main scraper**
```bash
python app.py
```

The application will:
1. Initialize Tor connection and Playwright
2. Fetch search terms from the database
3. Scrape news from Google Search results
4. Process RSS feeds from configured sources
5. Apply AI processing (summarization, classification, keywords)
6. Check for duplicates using semantic similarity
7. Store unique articles in the database
8. Generate scraping reports

## 🔧 Configuration

### Scraping Settings (`config/settings.py`)

```python
class Config:
    REQUEST_DELAY = (1, 4)           # Random delay between requests
    TIMEOUT = 45                      # Request timeout in seconds
    MAX_RETRIES = 5                   # Retry attempts for failed requests
    MAX_WORKERS = 4                   # Concurrent scraping workers
    MIN_CONTENT_LENGTH = 200          # Minimum article length
    MAX_CONTENT_LENGTH = 50000        # Maximum article length
    QUALITY_THRESHOLD = 0.6           # Quality score threshold
    SIMILARITY_THRESHOLD = 0.85       # Exact duplicate threshold
    SOMEWHAT_SIMILAR_THRESHOLD = 0.75 # Partial duplicate threshold
```

### Supported News Sources

**RSS Feeds:**
- Economic Times (Industry, Markets, Business)
- ET Now (Companies, Infrastructure, Market, Real Estate)
- Hindustan Times (Business)
- Indian Express (Business, Companies)
- India Times (Economy)
- India Today (Economics)
- India TV News (Business)
- Live Mint (Companies, Market)
- PR Newswire (Manufacturing)
- The Hindu (Business, Economy, Industry, Markets)
- Times of India (Business)
- Zee News (Business)
- CNBC
- And more...

**Google Custom Search Engines:** Configured for each major publication

## 🗄️ Database Schema

### Core Tables

**PRIMARY_TABLE**: Stores unique articles
```sql
- PRIMARY_ARTICLE_ID (UUID)
- TITLE, URL, DESCRIPTION
- NEWS_SOURCE, SOURCE_TYPE
- PUBLISH_DATE
```

**SECOND_TABLE**: Stores all article versions (including duplicates)
```sql
- PRIMARY_ARTICLE_ID (FK), ARTICLE_ID (UUID)
- TITLE, URL, DESCRIPTION
- PUBLISH_DATE, ARTICLE_SOURCE
- SCRAPED_DATE, SCRAP_VERSION
```

**VECTORS_TABLE**: Vector embeddings for similarity search
```sql
- ARTICLE_ID (UUID)
- EMBEDDINGS (VECTOR(768))
- METADATA (JSON)
```

**CATEGORY_TABLE**: Article classifications
```sql
- ARTICLE_ID (FK)
- CATEGORY, SUBCATEGORY
```

**KEYWORDS_TABLE**: Extracted keywords
```sql
- ARTICLE_ID (FK)
- KEYWORD (TEXT[])
```

**scraping_reports**: Performance metrics
```sql
- source_identifier, source_type
- total_links_found, total_links_scraped
- duplicate_url[], failed_url[]
- processing_time
```

## 🔑 Key Components

### AI Processing Pipeline

1. **Content Cleaning**: Removes HTML tags, scripts, and excess whitespace
2. **Summarization**: Generates ~55-word summaries using AWS Bedrock
3. **Keyword Extraction**: Identifies top 5 keywords from title + summary
4. **Classification**: Categorizes into taxonomy-based categories
5. **Embedding Generation**: Creates 768-dimensional semantic vectors
6. **Similarity Detection**: Checks against existing articles using FAISS

### Deduplication Strategy

- **Exact Duplicates** (85% similarity): Linked to existing article
- **Somewhat Similar** (75-85% similarity): Linked as related article
- **Unique** (<75% similarity): Created as new primary article

## 📊 Monitoring & Logging

The system uses structured JSON logging with the following levels:
- **INFO**: Normal operations
- **WARNING**: Skipped items or minor issues
- **ERROR**: Failed operations with retry potential
- **CRITICAL**: Fatal errors requiring intervention

Logs include contextual metadata for debugging and analysis.

## 🛡️ Error Handling

- **Automatic Retries**: Failed requests retry up to 5 times with exponential backoff
- **Failed URL Tracking**: Problematic URLs logged to `failed_urls.json`
- **Database Resilience**: Connection pooling with automatic reconnection
- **Graceful Degradation**: Processing continues even if individual sources fail

## 🔒 Security Features

- **Tor Integration**: Anonymous scraping to avoid IP blocking
- **Rotating User Agents**: Mimics different browsers
- **Rate Limiting**: Respectful delays between requests
- **Environment Variables**: Sensitive credentials kept secure
- **AWS IAM**: Bedrock access controlled through IAM roles

## 🎯 Use Cases

- **Market Intelligence**: Track business news across multiple sources
- **Competitive Analysis**: Monitor company mentions and industry trends
- **News Aggregation**: Centralized dashboard for business news
- **Research & Analysis**: Semantic search across news archives
- **Lead Generation**: Identify business opportunities from news
- **Content Curation**: Automated news categorization and tagging

## 🚧 Future Enhancements

- [ ] Real-time streaming processing
- [ ] GraphQL API for data access
- [ ] Web dashboard for visualization
- [ ] Machine learning-based source quality scoring
- [ ] Multi-language support
- [ ] Sentiment analysis integration
- [ ] Named entity recognition (NER)
- [ ] Time-series trend analysis

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **AWS Bedrock**: For powerful AI capabilities
- **Sentence Transformers**: For embedding models
- **Playwright**: For JavaScript-enabled scraping
- **PostgreSQL + pgvector**: For vector similarity search
- **Beautiful Soup**: For HTML parsing
- **All news sources**: For providing valuable content

## 📧 Contact

For questions, issues, or collaboration opportunities, please open an issue on GitHub.

---

**Built with ❤️ by NewsHive - Where News Intelligence Meets AI**
