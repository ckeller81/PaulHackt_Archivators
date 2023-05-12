from flask import Flask, jsonify, send_file, request, abort
from flask_cors import CORS
import os
import random
from PIL import Image

app = Flask(__name__, static_folder='wwwroot', static_url_path="/")
CORS(app)

data_path = os.environ.get("DATA_PATH", "c:\\temp\\paulhackt")
images_path = os.path.join(data_path, 'images')
resized_images_path = os.path.join(data_path, 'resized_images')

if not os.path.exists(resized_images_path):
    os.makedirs(resized_images_path)


@app.route("/heartbeat")
def heartbeat():
    return jsonify({"status": "healthy"})


@app.route('/api/images/exhibition')
def exhibition():
    # Get all files in the folder
    files = os.listdir(images_path)

    # Filter files to only include those ending with ".jpg"
    jpg_files = [file for file in files if file.endswith(".jpg")]

    # Pick 20 random files from the list
    random_files = random.sample(jpg_files, 20)

    # Get filenames without extensions
    filenames_without_extension = [
        os.path.splitext(file)[0] for file in random_files
    ]

    return {
        "title": "Kosmos Klee",
        "imageIds": filenames_without_extension
    }


@app.route('/images/<path:path>')
def images(path):
    full_image_path = os.path.join(images_path, f"{path}.jpg")

    width = request.args.get('width')
    if width:
        try:
            width = int(width)
        except ValueError:
            return "Invalid width parameter. Please provide a valid integer value."

    resized_image_path = os.path.join(
        resized_images_path, f"{path}_w{width}.jpg")

    # Check if the resized image already exists
    if os.path.exists(resized_image_path):
        return send_file(resized_image_path, mimetype='image/jpg')

    if not os.path.exists(full_image_path):
        # Return 404 error
        abort(404)

    # Resize the image if it doesn't exist
    # Get the desired width from query parameter
    if width:
        try:
            img = Image.open(full_image_path)
            # Resize to specified width, maintaining aspect ratio
            img.thumbnail((width, img.size[1]))
            img.save(resized_image_path, "JPEG")

            return send_file(resized_image_path, mimetype='image/jpg')
        except IOError:
            return "Error resizing image."

    return send_file(full_image_path, mimetype='image/jpg')


@app.route('/api/description/<path:path>')
def image_description(path):
    text_file_path = os.path.join(images_path, f"{path}.txt")
    if not os.path.exists(text_file_path):
        abort(404)

    with open(text_file_path, "r", encoding="utf-8") as f:
        text = f.read()

    return {
        "description": text
    }


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return app.send_static_file("index.html")


@app.errorhandler(404)
def not_found_error(error):
    return "404 Not Found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
