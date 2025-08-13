# app.py
import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract


# Initialize the Flask application
app = Flask(__name__)

# Configure the upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Checks if the file's extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_and_process():
    """
    Handles file uploads and OCR processing.
    - On GET request, it displays the upload form.
    - On POST request, it processes the uploaded image and displays the result.
    """
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        
        file = request.files['file']

        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            return render_template('index.html', error='No selected file')

        if file and allowed_file(file.filename):
            # Secure the filename to prevent security issues
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # Use Pillow to open the image and pytesseract to extract text
                img = Image.open(filepath)
                extracted_text = pytesseract.image_to_string(img)
                
                # Render the template with the results
                return render_template('index.html', 
                                       extracted_text=extracted_text, 
                                       img_path=filepath)
            except Exception as e:
                return render_template('index.html', error=f"An error occurred: {e}")

    # For a GET request, just show the upload page
    return render_template('index.html')

if __name__ == '__main__':
    # Create a templates folder if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')

    # Create the index.html file with Tailwind CSS for styling
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OCR Text Extractor</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Inter', sans-serif;
            }
            .result-box {
                white-space: pre-wrap; /* Preserves whitespace and newlines */
                word-wrap: break-word; /* Breaks long words */
            }
        </style>
    </head>
    <body class="bg-gray-100 text-gray-800 flex items-center justify-center min-h-screen">
        <div class="container mx-auto p-4 md:p-8 max-w-2xl">
            <div class="bg-white p-8 rounded-2xl shadow-lg">
                <h1 class="text-3xl md:text-4xl font-bold text-center mb-6 text-gray-900">Text Detection & Extraction</h1>
                <p class="text-center text-gray-600 mb-8">Upload an image to automatically extract the text using Tesseract OCR.</p>

                <!-- Upload Form -->
                <form method="post" enctype="multipart/form-data" class="mb-8 p-6 border-2 border-dashed border-gray-300 rounded-lg text-center hover:border-blue-500 transition-colors">
                    <label for="file-upload" class="cursor-pointer">
                        <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                        <span class="mt-2 block text-sm font-medium text-gray-900">Click to upload an image</span>
                        <span class="block text-xs text-gray-500">PNG, JPG, JPEG, GIF</span>
                    </label>
                    <input id="file-upload" name="file" type="file" class="sr-only" onchange="this.form.submit()">
                </form>

                <!-- Error Display -->
                {% if error %}
                    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg relative mb-6" role="alert">
                        <strong class="font-bold">Error:</strong>
                        <span class="block sm:inline">{{ error }}</span>
                    </div>
                {% endif %}

                <!-- Results Section -->
                {% if extracted_text is defined %}
                <div class="space-y-8">
                    <div>
                        <h2 class="text-2xl font-semibold mb-4 text-gray-900">Uploaded Image</h2>
                        <img src="{{ img_path }}" alt="Uploaded Image" class="w-full h-auto rounded-lg shadow-md">
                    </div>
                    <div>
                        <h2 class="text-2xl font-semibold mb-4 text-gray-900">Extracted Text</h2>
                        <div class="bg-gray-50 p-6 rounded-lg border border-gray-200 result-box">
                            <p>{{ extracted_text if extracted_text else "No text could be extracted." }}</p>
                        </div>
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """
    with open("templates/index.html", "w") as f:
        f.write(html_template)

    app.run(debug=True)
