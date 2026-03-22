from flask import Flask, request, jsonify
from PIL import Image
import io
import base64
import os

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/slice", methods=["POST"])
def slice_image():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    try:
        img = Image.open(file.stream).convert("RGBA")
        width, height = img.size
        num_slices = 7
        slice_height = height // num_slices

        slices = []
        for i in range(num_slices):
            top = i * slice_height
            bottom = (i + 1) * slice_height if i < num_slices - 1 else height
            slice_img = img.crop((0, top, width, bottom))
            buf = io.BytesIO()
            slice_img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            slices.append({
                "filename": f"slide_{i + 1}.png",
                "data": b64
            })

        return jsonify({"slices": slices})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
