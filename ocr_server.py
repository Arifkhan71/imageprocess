from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import base64
from PIL import Image
import easyocr
import io


app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template('imgpro.html')

reader = easyocr.Reader(['en'])

@app.route('/save-canvas', methods=['POST'])
def save_canvas():
    try:
        data = request.get_json()
        image_data = data.get('imageData')  # Extract the image data

        if not image_data:
            return jsonify({"error": "No image data provided"}), 400  # Error if no data

        # Remove "data:image/png;base64," prefix if present
        if image_data.startswith("data:image/png;base64,"):
            image_data = image_data.replace("data:image/png;base64,", "")

        try:
            # Decode base64 image data
            img_data = base64.b64decode(image_data)

            # Convert to an image that EasyOCR can process
            image = Image.open(io.BytesIO(img_data))

            # Convert the PIL image to RGB as EasyOCR expects color images
            image = image.convert("RGB")

            # Save the PIL image into a BytesIO object
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="PNG")
            image_bytes.seek(0)

            # Perform OCR with EasyOCR
            result = reader.readtext(image_bytes.getvalue(), detail=0)

            # Join recognized text into a single string
            recognized_text = " ".join(result)

            # Return recognized text as JSON
            return jsonify({"recognizedText": recognized_text})

        except Exception as e:
            return jsonify({"error": f"Image processing failed: {str(e)}"}), 500  # Handle decoding errors

    except Exception as e:
        return jsonify({"error": f"Request processing failed: {str(e)}"}), 500  # Handle other errors

if __name__ == '__main__':
    app.run(port=8000, debug=True)