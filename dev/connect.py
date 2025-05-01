import os

from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",  # Use the latest API version
)


# Example function to send a request
def get_completion(
    prompt, deployment_name="gpt-4-deployment"
):  # Change parameter name and default value
    try:
        response = client.chat.completions.create(
            deployment_name=deployment_name,  # Use deployment_name instead of model
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None


# # Example function to send a request
# def get_completion(prompt, model="gpt-4"):
#     try:
#         response = client.chat.completions.create(
#             model=model,
#             messages=[
#                 {"role": "user", "content": prompt}
#             ]
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         print(f"Error: {e}")
#         return None

# Example usage
if __name__ == "__main__":
    response = get_completion("Hello, how are you?", "gpt-4o-mini-0718-eu")
    print(response)
