import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from config import API_KEYS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_jobs_from_apis(keywords=None, location=None, limit=100):
    """
    Fetch jobs from multiple APIs based on keywords and location
    
    Args:
        keywords: Job search keywords (e.g., "software engineer")
        location: Job location (e.g., "New York")
        limit: Maximum number of jobs to return
        
    Returns:
        List of job dictionaries
    """
    if keywords is None:
        keywords = "software developer"
        
    all_jobs = []
    
    # Try each API source and handle potential failures gracefully
    apis = [
        fetch_from_jooble,
        fetch_from_careerjet,
        fetch_from_greenhouse,
        fetch_from_web3career
    ]
    
    for api_func in apis:
        try:
            jobs = api_func(keywords, location)
            all_jobs.extend(jobs)
            logger.info(f"Retrieved {len(jobs)} jobs from {api_func.__name__}")
        except Exception as e:
            logger.error(f"Error fetching from {api_func.__name__}: {str(e)}")
    
    # If no jobs found from APIs, try web scraping as fallback
    if len(all_jobs) == 0:
        logger.warning("No jobs found from APIs, trying web scraping fallback")
        all_jobs = scrape_jobs_from_public_sites(keywords, location)
        
    # Standardize job format and remove duplicates
    standardized_jobs = standardize_job_data(all_jobs)
    
    # Return requested number of jobs
    return standardized_jobs[:limit]

def fetch_from_jooble(keywords, location=None):
    """Fetch jobs from Jooble API"""
    if not API_KEYS.get('jooble'):
        logger.warning("Jooble API key not found, skipping")
        return []
        
    params = {"keywords": keywords}
    if location:
        params["location"] = location
        
    try:
        jooble_url = f"https://jooble.org/api/{API_KEYS['jooble']}"
        response = requests.post(jooble_url, json=params)
        
        if response.status_code == 200:
            return response.json().get("jobs", [])
        else:
            logger.error(f"Jooble API error: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Jooble API exception: {str(e)}")
        return []

def fetch_from_careerjet(keywords, location=None):
    """Fetch jobs from CareerJet API"""
    if not API_KEYS.get('careerjet'):
        logger.warning("CareerJet API key not found, skipping")
        return []
        
    params = {
        "keywords": keywords,
        "affid": API_KEYS['careerjet'],
        "user_ip": "11.22.33.44",  # Required by CareerJet
        "url": "https://www.example.com",  # Required by CareerJet
        "user_agent": "Mozilla/5.0"  # Required by CareerJet
    }
    
    if location:
        params["location"] = location
        
    try:
        careerjet_url = "http://public.api.careerjet.net/search"
        response = requests.get(careerjet_url, params=params)
        
        if response.status_code == 200:
            return response.json().get("jobs", [])
        else:
            logger.error(f"CareerJet API error: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"CareerJet API exception: {str(e)}")
        return []

def fetch_from_greenhouse(keywords, location=None):
    """Fetch jobs from Greenhouse API"""
    try:
        # Greenhouse's public API doesn't require authentication for basic job board data
        greenhouse_url = "https://boards-api.greenhouse.io/v1/boards/example/jobs"
        params = {"content": keywords}
        
        if location:
            params["location"] = location
            
        response = requests.get(greenhouse_url, params=params)
        
        if response.status_code == 200:
            return response.json().get("jobs", [])
        else:
            logger.error(f"Greenhouse API error: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Greenhouse API exception: {str(e)}")
        return []

def fetch_from_web3career(keywords, location=None):
    """Fetch jobs from Web3Career API"""
    try:
        web3_url = "https://api.web3.career/jobs"
        params = {"query": keywords}
        
        if location:
            params["location"] = location
            
        response = requests.get(web3_url, params=params)
        
        if response.status_code == 200:
            return response.json().get("jobs", [])
        else:
            logger.error(f"Web3Career API error: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Web3Career API exception: {str(e)}")
        return []

def scrape_jobs_from_public_sites(keywords, location=None):
    """
    Fallback method: Scrape job listings from public job sites
    that don't require authentication
    """
    jobs = []
    
    # Example: Scrape from Indeed (for demonstration - actual implementation would need to respect TOS)
    try:
        search_query = keywords.replace(" ", "+")
        location_query = f"&l={location.replace(' ', '+')}" if location else ""
        
        url = f"https://www.indeed.com/jobs?q={search_query}{location_query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        
        job_cards = soup.find_all("div", class_="jobsearch-SerpJobCard")
        
        for card in job_cards:
            title_elem = card.find("h2", class_="title")
            company_elem = card.find("span", class_="company")
            location_elem = card.find("div", class_="recJobLoc")
            summary_elem = card.find("div", class_="summary")
            
            if not title_elem:
                continue
                
            job = {
                "title": title_elem.text.strip() if title_elem else "Unknown",
                "company": company_elem.text.strip() if company_elem else "Unknown",
                "location": location_elem.get("data-rc-loc", "Remote") if location_elem else "Remote",
                "description": summary_elem.text.strip() if summary_elem else "No description available",
                "source": "Indeed (scraped)"
            }
            
            jobs.append(job)
            
        logger.info(f"Scraped {len(jobs)} jobs from Indeed")
    except Exception as e:
        logger.error(f"Error scraping from Indeed: {str(e)}")
    
    return jobs

def standardize_job_data(jobs):
    """
    Standardize job data format from different sources
    and remove duplicates
    """
    standardized = []
    seen_jobs = set()
    
    for job in jobs:
        # Create a unique identifier for deduplication
        job_id = f"{job.get('title', '')}-{job.get('company', '')}"
        
        if job_id in seen_jobs:
            continue
            
        seen_jobs.add(job_id)
        
        # Standardize fields across different API formats
        standardized_job = {
            "title": job.get("title", job.get("job_title", "Unknown Position")),
            "company": job.get("company", job.get("company_name", "Unknown Company")),
            "location": job.get("location", job.get("job_location", "Remote/Not Specified")),
            "description": job.get("description", job.get("snippet", "No description available")),
            "url": job.get("url", job.get("job_url", "#")),
            "date_posted": job.get("date_posted", job.get("updated", "Unknown")),
            "source": job.get("source", "API")
        }
        
        standardized.append(standardized_job)
        
    return standardized
