from flask import Flask, request, jsonify, send_file
from PIL import Image
import io
import zipfile
import os

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/slice", methods=["POST"])
def slice_image():
    """
    Accepts a PNG file upload, slices it into 7 equal horizontal strips,
    and returns a ZIP file containing slide_1.png through slide_7.png.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Send PNG as multipart/form-data with key 'file'"}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".png"):
        return jsonify({"error": "Only PNG files are supported"}), 400

    try:
        img = Image.open(file.stream).convert("RGBA")
        width, height = img.size
        num_slices = 7
        slice_height = height // num_slices

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for i in range(num_slices):
                top = i * slice_height
                # Last slice gets any remaining pixels (handles rounding)
                bottom = (i + 1) * slice_height if i < num_slices - 1 else height

                slice_img = img.crop((0, top, width, bottom))
                slice_buffer = io.BytesIO()
                slice_img.save(slice_buffer, format="PNG")
                slice_buffer.seek(0)

                filename = f"slide_{i + 1}.png"
                zf.writestr(filename, slice_buffer.read())

        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="carousel_slices.zip"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
