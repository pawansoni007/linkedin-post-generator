from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM
import os
import time
from dotenv import load_dotenv
from IPython.display import Markdown
from linkedin_poster import post_content_to_linkedin

load_dotenv()

# Get available API keys
api_keys = [
    os.getenv("GROQ_API_KEY"),
    os.getenv("GROQ_API_KEY_2")
]

linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID"),
linkedin_client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
   
api_keys = [key for key in api_keys if key]  # Remove None values

current_api_key_index = 0

# Initialize Groq LLM with DeepSeek-R1-Distill-Llama-70B
def create_llm(api_key):
    return LLM(
        model="groq/deepseek-r1-distill-llama-70b",
        api_key=api_key
    )

llm = create_llm(api_keys[current_api_key_index])

planner = Agent(
    role="Content Planner",
    goal="Plan engaging and factually accurate LinkedIn posts on technical topics that are easy to digest.",
    backstory="You specialize in creating engaging, bite-sized LinkedIn posts for technical topics. Your mission is to make complex concepts accessible and interesting, especially for beginners. You focus on quick, actionable insights that spark curiosity and encourage learning, ensuring each post is both informative and easy to understand. Your content planning is tailored to help readers gain valuable knowledge without feeling overwhelmed. Your work is the basis for the Content Writer to write an article on this topic.",
    allow_delegation=False, 
    verbose=True,
    llm=llm
)

writer = Agent(
    role="Content Writer",
    goal="Write a LinkedIn post on {topic} based on the plan provided by the Content Planner, possibly including character-based diagrams and simple analogies.",
    backstory="You are a skilled technical writer with expertise in crafting clear, engaging LinkedIn posts. You have a special talent for simplifying complex topics using character-based diagrams (like flowcharts) and relatable analogies and concise writing. Your mission is to take the plan provided by the Content Planner and transform it into a well-structured, informative, and interesting short-form LinkedIn post. You focus on delivering valuable insights in a punchy and concise format, ideal for grabbing attention quickly, ensuring each post is both informative and easy to understand.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

reviewer = Agent(
    role="Content Reviewer",
    goal="Review the LinkedIn post for quality, accuracy, and engagement, providing feedback for improvement.",
    backstory="You are an experienced content reviewer with a keen eye for detail and a deep understanding of what makes a LinkedIn post successful. Your mission is to ensure that every post is polished, professional, and aligns with the intended goals. You check for clarity, tone, factual accuracy, and overall impact, providing constructive feedback to elevate the content to its highest potential.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

# Create tasks for each agent
plan_task = Task(
    description=(
        "Create a detailed content plan for a LinkedIn post on the topic: {topic}. "
        "The plan should be engaging, factually accurate, and easy for beginners to digest. Include key points, a suggested structure, and any relevant hashtags. "
        "Also, suggest if a simple character-based diagram or a short analogy would be beneficial for explaining the topic."
    ),
    expected_output="A comprehensive content plan in markdown format, including an outline, key talking points, relevant hashtags, and a suggestion on whether to use a character-based diagram or analogy.",
    agent=planner
)

write_task = Task(
    description=(
        "Using the content plan from the planner, write a compelling LinkedIn post on {topic}. The post should be clear, engaging, and well-structured. "
        "If the topic is complex, consider using a simple character-based diagram or a short analogy to make it easier to understand. "
        "Make sure to follow the provided plan and maintain a professional yet accessible tone."
    ),
    expected_output="A short, punchy LinkedIn post as a markdown text, ready to be published. The post should be concise, ideally 1-2 paragraphs long, and may include a simple character-based diagram or analogy if it helps with clarity.",
    agent=writer,
    context=[plan_task],
)

review_task = Task(
    description=(
        "Review the LinkedIn post written by the Content Writer. "
        "Check for quality, accuracy, clarity, and engagement. "
        "Provide constructive feedback and make necessary edits to ensure the post is polished and ready for publication."
    ),
    expected_output="ONLY the final LinkedIn post content in markdown format, ready for publishing. Do NOT include any thinking process, commentary, analysis, or remarks. Just the clean post content that can be directly copied and pasted to LinkedIn.",
    agent=reviewer,
    context=[write_task],
)


crew = Crew(
    agents=[planner, writer, reviewer],
    tasks=[plan_task, write_task, review_task], 
    verbose=True,
    process=Process.sequential,
)

def switch_api_key():
    global current_api_key_index, llm, planner, writer, reviewer
    current_api_key_index = (current_api_key_index + 1) % len(api_keys)
    print(f"🔄 Switching to API key {current_api_key_index + 1}/{len(api_keys)}")
    
    # Create new LLM with different API key
    llm = create_llm(api_keys[current_api_key_index])
    
    # Update all agents with new LLM
    planner.llm = llm
    writer.llm = llm
    reviewer.llm = llm
    
    return llm

if __name__ == "__main__":
    max_retries = len(api_keys) * 2  # Try each API key twice
    retry_delay = 5  # seconds
    
    print(f"🚀 Starting with {len(api_keys)} API keys available")
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries} using API key {current_api_key_index + 1}/{len(api_keys)}")
            result = crew.kickoff(inputs={"topic": "I just built an AI-powered content creation system using CrewAI with 3 specialized agents (Content Planner, Writer, and Reviewer) that automatically generates LinkedIn posts and posts them via LinkedIn API. The system includes smart API key rotation for handling rate limits and produces engaging, technical content. Talk about the power of multi-agent AI systems and automation in content creation."})
            
            # Clean up the output by removing <think> content
            clean_content = result.raw
            if "</think>" in clean_content:
                # Find the end of </think> and take everything after it
                think_end = clean_content.find("</think>") + len("</think>")
                clean_content = clean_content[think_end:].strip()
                print("🧹 Cleaned up thinking content from output")
            
            print("✅ SUCCESS! Task completed successfully!")
            print(Markdown(clean_content))
            with open("output.md", "w", encoding="utf-8") as f:
                f.write(clean_content)
            print("💾 Output saved to output.md")
            
            # Post to LinkedIn
            print("📱 Posting to LinkedIn...")
            linkedin_result = post_content_to_linkedin(clean_content)
            
            if linkedin_result["success"]:
                print(f"🎉 {linkedin_result['message']}")
                print(f"📝 Post ID: {linkedin_result.get('post_id', 'Unknown')}")
            else:
                print(f"❌ LinkedIn posting failed: {linkedin_result['error']}")
            
            break
        except Exception as e:
            if "429" in str(e):
                print(f"❌ RATE LIMIT HIT on API key {current_api_key_index + 1}")
                if attempt < max_retries - 1:
                    switch_api_key()
                    print(f"⏳ Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                else:
                    print("💥 ALL API KEYS EXHAUSTED! Cannot continue.")
                    break
            else:
                print(f"💥 UNEXPECTED ERROR: {e}")
                if attempt < max_retries - 1:
                    switch_api_key()
                    print(f"⏳ Trying with next API key in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("💥 ALL RETRY ATTEMPTS FAILED!")
                    break