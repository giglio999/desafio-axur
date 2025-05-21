import os
import base64
import json
import logging
import requests
from playwright.sync_api import sync_playwright

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper_inference.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Constants
TARGET_URL = "https://intern.aiaxuropenings.com/scrape/325bec94-ab50-452f-a0bf-74ecb815b25b"
API_URL = "https://intern.aiaxuropenings.com/v1/chat/completions"
SUBMIT_URL = "https://intern.aiaxuropenings.com/api/submit-response"
OUTPUT_DIR = "scraped_images"

class ImageScraper:
    def __init__(self, url, output_dir=OUTPUT_DIR):
        self.url = url
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def scrape_and_get_image(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0"
            )
            try:
                logger.info(f"Navigating to {self.url}")
                page.goto(self.url, wait_until="networkidle")
                page.wait_for_timeout(3000)

                image = page.query_selector("img")
                if not image:
                    logger.error("No image found on the page")
                    return None

                src = image.get_attribute("src")
                if not src:
                    logger.error("Image source not found")
                    return None

                filepath = os.path.join(self.output_dir, "scraped_image.jpg")

                if src.startswith("data:image"):
                    logger.info("Image is base64 encoded, decoding directly.")
                    header, base64_data = src.split(",", 1)
                    image_data = base64.b64decode(base64_data)
                    with open(filepath, 'wb') as f:
                        f.write(image_data)
                else:
                    logger.info(f"Downloading image from: {src}")
                    headers = {
                        "User-Agent": "Mozilla/5.0",
                        "Referer": self.url
                    }
                    response = requests.get(src, headers=headers, timeout=30)
                    response.raise_for_status()
                    with open(filepath, 'wb') as f:
                        f.write(response.content)

                logger.info(f"Image successfully saved to {filepath}")
                return filepath

            except Exception as e:
                logger.error(f"Error during scraping: {str(e)}")
                return None
            finally:
                browser.close()

class FlorenceInference:
    def __init__(self, api_url, auth_token):
        self.api_url = api_url
        self.auth_token = auth_token

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def get_detailed_caption(self, image_path):
        try:
            base64_image = self.encode_image(image_path)
            payload = {
                "model": "microsoft-florence-2-large",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Provide a <DETAILED_CAPTION> for this image."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ]
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.auth_token}"
            }
            logger.info("Submitting image for inference...")
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            logger.info("Inference completed successfully")
            return response.json()
        except Exception as e:
            logger.error(f"Error during inference: {str(e)}")
            return None

def submit_inference_result(response_json, auth_token):
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
        logger.info("Submitting inference result to the final endpoint...")
        response = requests.post(SUBMIT_URL, headers=headers, json=response_json, timeout=60)
        response.raise_for_status()
        logger.info("Response successfully submitted!")
        print("✔️ Inference result successfully submitted!")
    except Exception as e:
        logger.error(f"Failed to submit inference result: {str(e)}")
        print("❌ Error submitting the inference result.")

def main():
    auth_token = os.environ.get("AUTH_TOKEN")
    if not auth_token:
        auth_token = input("Enter your authorization token received by email: ")

    scraper = ImageScraper(TARGET_URL)
    image_path = scraper.scrape_and_get_image()

    if not image_path:
        logger.error("Failed to scrape and download the image. Exiting.")
        return

    florence_client = FlorenceInference(API_URL, auth_token)
    inference_result = florence_client.get_detailed_caption(image_path)

    if not inference_result:
        logger.error("Failed to get inference result. Exiting.")
        return

    with open("inference_result.json", "w") as f:
        json.dump(inference_result, f, indent=2)
    logger.info("Inference result saved to inference_result.json")

    submit_inference_result(inference_result, auth_token)

    try:
        caption = inference_result.get("choices", [{}])[0].get("message", {}).get("content", "")
        print("\nDetailed Caption Result:")
        print(caption)
    except (KeyError, IndexError):
        logger.error("Could not extract caption from inference result")

if __name__ == "__main__":
    main()
