from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
from bs4 import BeautifulSoup
import base64
import datetime
import re
from openai import OpenAI
import urllib
import pandas as pd
import random
import sys # Keep sys for potential future use, but stdout redirection will be removed
import os
import requests
from werkzeug.utils import secure_filename

# Initialize Flask App
app = Flask(__name__, template_folder='.') # Serve templates from current dir

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'super secret key' # Change for production

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# GPT and DALL-E functions (mostly unchanged, removed Tkinter specific print handling)
def gpt(system_text ,user_text):
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_text},
            {"role": "user","content": user_text}
        ],
        model="gpt-4o",
    )
    return response.choices[0].message.content

def generate_image_with_dalle(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            quality="hd",
            size="1024x1024",
        )
        return response.data[0].url
    except Exception as e:
        print(f"An error occurred while generating image: {str(e)}")
        return None

def generate_image_prompt_with_gpt(title):
        prompt = gpt("You are a creative assistant who can generate prompt for img DALL-E",
                     f"writ a prompt for making a beautiful and realistic img for this title: {title} *be very specific and realistic* (dont add any thing to ansur only the  prompt )")
        return prompt

def write_text_with_gpt(text):
    return gpt(
        f""" write an 5000 words article about "{text}". make sure its humanize and it will be written from the writer perspective and opinion make sure add emotions in your writing, make sure its written in very simple English and include quirks, imperfections, or conversational tone typical of human writing. Avoid from using general setnances. 
        Please make sure all paraphrases are used with the above instructions (dont put the title in text and no head line in the first paregraf) keep the drama down. sign the headlines with ***  befor and after the headline""",
        text
    )

def humanize_text_with_gpt(text):
    return gpt(
        f""" please humanize the following text change the text so it will be written from the writer perspective and opinion make sure add emotions in your writing, make sure its written in very simple English and include quirks, imperfections, or conversational tone typical of human writing. keep the *** in the headlines.
        """,
        text
    )

def get_wordpress_headers(site, user, password):
    credentials = f"{user}:{password}"
    token = base64.b64encode(credentials.encode())
    headers = {
        'Authorization': f'Basic {token.decode("utf-8")}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
        'Content-Type': 'application/json'
    }
    return headers

def upload_image_to_wordpress(site, img_path, user, password):
    print("upload_image_to_wordpress (function entry)") # DEBUG LINE
    # Ensure site URL doesn't have a trailing slash for clean joining, then append endpoint
    base_url = site.rstrip('/')
    url = f'{base_url}/wp-json/wp/v2/media'
    print(f"DEBUG: Attempting to upload image to URL: {url}") # DEBUG LINE

    if os.path.exists(img_path):
        with open(img_path, 'rb') as img_file:
            img_data = img_file.read()
        file_name = os.path.basename(img_path)
        headers = get_wordpress_headers(site, user, password)
        headers['Content-Type'] = 'image/png' # Assuming PNG, adjust if other formats are used
        headers['Content-Disposition'] = f'attachment; filename="{file_name}"'
        try:
            res = requests.post(url=url, data=img_data, headers=headers, timeout=60)
            res.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
            print("upload_image_to_wordpress (request successful)") # DEBUG LINE
            
            return res.json().get('id')
        except requests.exceptions.RequestException as e:
            print(f"Failed to upload image. Error: {e}, Response: {res.text if 'res' in locals() else 'No response'}")
            return None
    print(f"Image path does not exist: {img_path}")
    return None

def save_image_to_local(image_url, title):
    # Create a safer filename from the title
    safe_title = re.sub(r'[^\\w\\s-]', '', title).strip().replace(' ', '_')
    safe_title = safe_title[:50] # Limit length
    img_file_name = f"images/{secure_filename(safe_title)}.png"
    os.makedirs(os.path.dirname(img_file_name), exist_ok=True)
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib.request.Request(url=image_url, headers=headers)
        with urllib.request.urlopen(req) as response, open(img_file_name, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Image saved locally: {img_file_name}")
        return img_file_name
    except Exception as e:
        print(f"Error saving image {image_url} locally: {e}")
        return None

def rand_date():
    now = datetime.datetime.now()
    ago_30 = now - datetime.timedelta(days=30)
    random_datetime = ago_30 + datetime.timedelta(
        seconds=random.randint(0, int((now - ago_30).total_seconds())))
    return random_datetime.isoformat() # Return ISO format string for JSON

def upload_to_wordpress(site, user, password, title, content, category_id, featured_image_id):
    # Ensure site URL doesn't have a trailing slash for clean joining, then append endpoint
    base_url = site.rstrip('/')
    url = f"{base_url}/wp-json/wp/v2/posts"
    print(f"DEBUG: Attempting to upload post to URL: {url}") # DEBUG LINE
    author = 2 # Ensure these author IDs are valid on your WP site
    post_data = {
        "date": datetime.datetime.now().isoformat() #rand_date(),
        "author": author,
        "title": title,
        "content": content,
        "status": "publish",
        "categories": [category_id]
    }
    if featured_image_id:
        post_data['featured_media'] = featured_image_id
    
    headers = get_wordpress_headers(site, user, password)
    try:
        res = requests.post(url=url, headers=headers, json=post_data, timeout=60)
        res.raise_for_status()
        print(f"Post '{title}' successfully uploaded to {site}.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to upload post '{title}' to {site}. Error: {e}, Response: {res.text if 'res' in locals() else 'No response'}")

def process_csv_data(file_path):
    # This function will contain the logic from the original process_csv
    # It will be called by the Flask route after a file is uploaded
    # For now, it will print messages that would appear in gunicorn logs
    results_log = []
    try:
        df = pd.read_csv(file_path, encoding="utf-8-sig")
        print(f"CSV columns identified by pandas: {df.columns.tolist()}") # DEBUG LINE
        results_log.append(f"Successfully read CSV: {os.path.basename(file_path)}")
        results_log.append(f"Columns found: {df.columns.tolist()}") # Also add to log for UI if needed later
        for index, row in df.iterrows():
            try:
                
                title = str(row['Title'])
                site = str(row['Domain'])
                user = str(row['User'])
                password = str(row['Pass'])
                category_id = int(row['CategoryID'])
                # api_key = row["api"] # api key from CSV, current code uses global client
                print(f"DEBUG: Starting processing for row index {index}, Title: {title}") # DEBUG LINE
                results_log.append(f"Processing title: {title}")

                print(f"DEBUG: Calling write_text_with_gpt for title: '{title}'") # DEBUG LINE
                text = write_text_with_gpt(title)
                print(f"DEBUG: Finished write_text_with_gpt for title: '{title}'") # DEBUG LINE

                print(f"DEBUG: Calling humanize_text_with_gpt for title: '{title}'") # DEBUG LINE
                humanize_text = humanize_text_with_gpt(text)
                print(f"DEBUG: Finished humanize_text_with_gpt for title: '{title}'") # DEBUG LINE
                humanize_text = humanize_text.replace("#", "").replace("***\n", "</h4>").replace("***", "<h4>")
                results_log.append(f"Generated and humanized text for: {title}")

                print(f"DEBUG: Calling generate_image_prompt_with_gpt for title: '{title}'") # DEBUG LINE
                image_prompt = generate_image_prompt_with_gpt(title)
                print(f"DEBUG: Finished generate_image_prompt_with_gpt. Prompt: {image_prompt[:100]}...") # DEBUG LINE
                
                print(f"DEBUG: Calling generate_image_with_dalle for title: '{title}'") # DEBUG LINE
                image_url = generate_image_with_dalle(image_prompt)
                print(f"DEBUG: Finished generate_image_with_dalle. Image URL: {image_url}") # DEBUG LINE
                
                if image_url:
                    print(f"DEBUG: Calling save_image_to_local for image_url: {image_url}, title: '{title}'") # DEBUG LINE
                    img_file_path = save_image_to_local(image_url, title)
                    print(f"DEBUG: Finished save_image_to_local. Path: {img_file_path}") # DEBUG LINE
                    if img_file_path:
                        results_log.append(f"Image saved locally: {img_file_path}")
                        print(f"DEBUG: Preparing to call upload_image_to_wordpress for site: {site}, img_path: {img_file_path}, user: {user}") # DEBUG LINE
                        image_id = upload_image_to_wordpress(site, img_file_path, user, password)
                        print(f"DEBUG: Finished upload_image_to_wordpress. Image ID: {image_id}") # DEBUG LINE
                        if image_id:
                            results_log.append(f"Image uploaded to WordPress, ID: {image_id}")
                        else:
                            results_log.append(f"Failed to upload image for: {title}")
                    else:
                        results_log.append(f"Failed to save image locally for: {title}")
                        image_id = None
                    img_file_path = None # ensure it's defined

                print(f"DEBUG: Calling upload_to_wordpress for site: {site}, title: '{title}'") # DEBUG LINE
                upload_to_wordpress(site, user, password, title, humanize_text, category_id, image_id)
                print(f"DEBUG: Finished upload_to_wordpress for title: '{title}'") # DEBUG LINE
                
                # Clean up local image file after upload (optional)
                if img_file_path and os.path.exists(img_file_path):
                    try:
                        os.remove(img_file_path)
                        results_log.append(f"Cleaned up local image: {img_file_path}")
                    except OSError as e:
                        results_log.append(f"Error deleting image {img_file_path}: {e}")

            except Exception as e:
                error_message = f"Error processing row {index} ({title if 'title' in locals() else 'N/A'}): {str(e)}"
                print(error_message) # Also print to server log for immediate visibility
                results_log.append(error_message)
        results_log.append("Finished processing all rows.")
    except Exception as e:
        error_message = f"Critical error in process_csv_data: {str(e)}"
        print(error_message)
        results_log.append(error_message)
    
    # For now, we just print the log. Later this could be returned to the user.
    for log_entry in results_log:
        print(log_entry) 
    return "\n".join(results_log)


@app.route('/', methods=['GET'])
def index():
    # Serve the landing page
    # Ensure 'landing_paage.html' is in the 'templates' folder or adjust path
    return render_template('index.html')

@app.route('/upload_csv', methods=['POST'])
def upload_csv_file():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Save the uploaded file to the UPLOAD_FOLDER
        # Note: ensure UPLOAD_FOLDER is relative to main.py or an absolute path
        # If main.py is in wp-content, UPLOAD_FOLDER will be wp-content/uploads
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            flash(f'File "{filename}" uploaded successfully. Processing...', 'info')
            
            # Process the CSV file (this might take time)
            # Consider running this in a background thread for better UX
            processing_log = process_csv_data(filepath)
            
            # Clean up the uploaded CSV file after processing
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    print(f"Cleaned up uploaded CSV: {filepath}")
                except OSError as e:
                    print(f"Error deleting uploaded CSV {filepath}: {e}")

            # For now, just flash a success message with a snippet of the log.
            # A more robust solution would be to stream logs or use WebSockets.
            flash('CSV processing finished. Check server logs for details.', 'success')
            # flash(f'Processing Log:\n{processing_log[:500]}...', 'info') # Example of showing some log
            return redirect(url_for('index')) # Redirect back to home page
            
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload a CSV file.', 'error')
        return redirect(url_for('index'))

@app.route('/download_sample_csv')
def download_sample():
    try:
        return send_from_directory(app.root_path, 'static/sample.csv', as_attachment=True, download_name='sample_wordpress_posts.csv')
    except FileNotFoundError:
        flash('Sample CSV file not found.', 'error')
        return redirect(url_for('index'))

# Removed Tkinter related functions:
# RedirectText class
# open_file function
# start_process function
# create_ui function

# Restore stdout if it was changed (it wasn't in the Flask context, but good practice)
# sys.stdout = sys.__stdout__ # Not strictly necessary here as we removed the redirection

if __name__ == '__main__':
    # Make sure to run with gunicorn in production, not Flask's dev server
    # For development:
    app.run(debug=True, host='0.0.0.0', port=5001) # Running on port 5001 for dev
