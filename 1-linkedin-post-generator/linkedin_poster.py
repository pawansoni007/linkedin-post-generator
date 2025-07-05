import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()

class LinkedInPoster:
    def __init__(self):
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.base_url = "https://api.linkedin.com/v2"
        
    def get_user_urn(self):
        """Get user URN from LinkedIn API"""
        try:
            url = f"{self.base_url}/userinfo"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            user_info = response.json()
            return user_info.get("sub")
        except Exception as e:
            print(f"❌ Error getting user URN: {e}")
            return None
    
    def clean_content(self, content):
        """Clean markdown content for LinkedIn"""
        # Remove markdown headers
        content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
        
        # Remove markdown bold/italic
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
        content = re.sub(r'\*(.*?)\*', r'\1', content)
        
        # Remove markdown code blocks
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`([^`]+)`', r'\1', content)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()
        
        return content
    
    def post_to_linkedin(self, content):
        """Post content to LinkedIn"""
        try:
            user_urn = self.get_user_urn()
            if not user_urn:
                return {"success": False, "error": "Could not get user URN"}
            
            # Clean the content
            clean_content = self.clean_content(content)
            
            url = f"{self.base_url}/ugcPosts"
            headers = {
                "LinkedIn-Version": "202210",
                "X-Restli-Protocol-Version": "2.0.0",
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Escape quotes in content
            escaped_content = clean_content.replace('"', '\\"')
            
            data = {
                "author": f"urn:li:person:{user_urn}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": escaped_content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            post_id = result.get("id", "Unknown")
            
            return {
                "success": True,
                "post_id": post_id,
                "message": "Successfully posted to LinkedIn!"
            }
            
        except requests.exceptions.HTTPError as e:
            error_details = ""
            try:
                error_details = f" - {e.response.json()}"
            except:
                pass
            
            return {
                "success": False,
                "error": f"HTTP Error: {e}{error_details}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {e}"
            }

def post_content_to_linkedin(content):
    """Simple function to post content to LinkedIn"""
    poster = LinkedInPoster()
    return poster.post_to_linkedin(content)
