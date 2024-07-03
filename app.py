from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import cv2
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
PROCESSED_FOLDER = 'static/processed/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

def cartoonify(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(img, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon

def sketchify(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    invert = cv2.bitwise_not(gray_img)
    blur = cv2.GaussianBlur(invert, (21, 21), 0)
    inverted_blur = cv2.bitwise_not(blur)
    sketch = cv2.divide(gray_img, inverted_blur, scale=256.0)
    return sketch

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Uploading file to: {filepath}")
        file.save(filepath)

        img = cv2.imread(filepath)
        if img is None:
            print(f"Failed to load image from {filepath}")
            return "File not found or invalid image format"

        cartoon = cartoonify(img)
        cartoon_path = os.path.join(app.config['PROCESSED_FOLDER'], 'cartoon_' + filename)
        print(f"Saving cartoonified image to: {cartoon_path}")
        cv2.imwrite(cartoon_path, cartoon)

        sketch = sketchify(img)
        sketch_path = os.path.join(app.config['PROCESSED_FOLDER'], 'sketch_' + filename)
        print(f"Saving sketch image to: {sketch_path}")
        cv2.imwrite(sketch_path, sketch)

        return render_template('result.html', filename=filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
