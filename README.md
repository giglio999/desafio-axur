
# 🖼️ Axur Challenge: Image Scraping and Captioning with Microsoft Florence

This project automates the process of scraping an image from a web page, generating a detailed caption using **Microsoft Florence 2 Large**, and submitting the result to a validation API.

## 📁 Project Structure

* **`axur_challenge.py`**: Main script to perform scraping, image captioning, and submission.
* **`scraped_images/`**: Directory where the scraped image is saved.
* **`inference_result.json`**: Output file containing the captioning result.

## 🔧 Technologies Used

* [Python 3.8+](https://www.python.org/)
* [Playwright](https://playwright.dev/python/) – for browser automation and scraping
* [Requests](https://docs.python-requests.org/) – for API interaction
* [Microsoft Florence 2 Large](https://learn.microsoft.com/en-us/semantic-kernel/) – for image captioning
* Standard libraries: `os`, `json`, `base64`, `logging`

## 🚀 How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
playwright install
```

### 2. Set your authentication token

You can provide the token via environment variable:

```bash
export AUTH_TOKEN=your_token_here
```

Alternatively, the script will prompt you to enter it during execution.

### 3. Run the script

```bash
python axur_challenge.py
```

The script will:

1. Navigate to the target URL.
2. Scrape the first image found on the page.
3. Submit the image to Microsoft Florence for detailed captioning.
4. Save the result locally as `inference_result.json`.
5. Print the generated caption.
6. Submit the result to the final API endpoint.

## ✅ Expected Output

* Image saved to: `scraped_images/scraped_image.jpg`
* Inference result saved to: `inference_result.json`
* Console output with the caption
* Final confirmation message:

  ```
  ✔️ Inference result successfully submitted!
  ```

## 🛠️ Error Handling

This script logs all major actions and handles exceptions related to:

* Missing image or broken selectors
* HTTP request failures
* API errors or malformed responses

Logs are saved to: `scraper_inference.log`

## 🧪 Example Output

```bash
Detailed Caption Result:
A group of people walking in the rain with umbrellas near a large glass building...
```

## 📩 Notes

* The authorization token must be obtained beforehand (via email or assignment instructions).
* This script uses headless Chromium via Playwright for scraping.

