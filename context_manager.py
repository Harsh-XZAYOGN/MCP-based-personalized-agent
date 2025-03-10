# context_manager.py
from anthropic import Anthropic
import json
from typing import Dict, List, Any

class ContextManager:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def generate_recommendation_message(self, user_context: Dict, job_listings: List[Dict]) -> str:
        """
        Creates a structured message for Claude with user context and job listings
        """
        # Format user context for Claude
        user_profile = (
            f"User Profile:\n"
            f"Skills: {', '.join(user_context.get('skills', []))}\n"
            f"Experience: {user_context.get('experience', 'Not specified')}\n"
            f"Job Preferences: {user_context.get('preferences', 'Not specified')}\n"
            f"Location: {user_context.get('location', 'Not specified')}\n"
        )
        
        # Format job listings
        job_listings_text = "Available Job Listings:\n"
        for i, job in enumerate(job_listings, 1):
            job_listings_text += (
                f"Job {i}:\n"
                f"Title: {job.get('title', 'Unknown')}\n"
                f"Company: {job.get('company', 'Unknown')}\n"
                f"Description: {job.get('description', 'No description available')[:300]}...\n"
                f"Location: {job.get('location', 'Remote/Not specified')}\n\n"
            )
        
        # Create the complete context message
        message = (
            f"{user_profile}\n\n"
            f"{job_listings_text}\n\n"
            "Based on the user's profile and the available job listings, recommend the most suitable jobs. "
            "Explain why each job matches the user's skills and preferences. "
            "Also suggest skills the user might want to develop to improve their job prospects."
        )
        
        return message
    
    def get_personalized_recommendations(self, user_context: Dict, job_listings: List[Dict]) -> Dict:
        """
        Get personalized job recommendations using Claude and the Model Context Protocol
        """
        message = self.generate_recommendation_message(user_context, job_listings)
        
        response = self.client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1000,
            system="You are an AI job recommendation assistant. Use the provided context to match users with the most relevant job listings.",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        
        return {
            "recommendations": job_listings,
            "claude_analysis": response.content[0].text
        }
