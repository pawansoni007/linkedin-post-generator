#!/usr/bin/env python3
"""
Simple test script for LinkedIn posting functionality
"""

from linkedin_poster import post_content_to_linkedin

def test_linkedin_posting():
    """Test LinkedIn posting with sample content"""
    
    test_content = """
🚀 **Test Post from API**

This is a test post generated automatically using Python and the LinkedIn API!

Key features tested:
• Automatic content cleaning
• Markdown to text conversion  
• API authentication
• Post publishing

#Python #LinkedIn #API #Automation #TechTest
    """
    
    print("🧪 Testing LinkedIn posting functionality...")
    print(f"📝 Content to post:\n{test_content}")
    print("-" * 50)
    
    result = post_content_to_linkedin(test_content)
    
    if result["success"]:
        print(f"✅ SUCCESS! {result['message']}")
        print(f"📝 Post ID: {result.get('post_id', 'Unknown')}")
        print("🔗 Check your LinkedIn profile to see the post!")
    else:
        print(f"❌ FAILED: {result['error']}")
        print("\n💡 Troubleshooting tips:")
        print("   • Check your LINKEDIN_ACCESS_TOKEN in .env file")
        print("   • Ensure token hasn't expired (2 months validity)")
        print("   • Verify app has 'Share on LinkedIn' permissions")

if __name__ == "__main__":
    test_linkedin_posting()
