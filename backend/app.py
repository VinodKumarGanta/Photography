import os
import uuid
import qrcode
from io import BytesIO
from flask import Flask, request, jsonify, render_template, send_file, url_for, send_from_directory

app = Flask(__name__)

# Configurations
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dictionary to store photo metadata (In a real app, you would use a database like SQLite or PostgreSQL)
photo_db = {}

@app.route('/')
def index():
    # Simple upload interface for the photographer
    return render_template('upload.html')

from PIL import Image, ExifTags

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'photo' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        photo_id = str(uuid.uuid4())
        file_ext = '.jpg' # Force to jpg constraint for compression
        filename = f"{photo_id}{file_ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            img = Image.open(file)
            
            # Handle orientation from EXIF
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation]=='Orientation':
                        break
                exif = img._getexif()
                if exif is not None:
                    if exif[orientation] == 3:
                        img=img.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        img=img.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        img=img.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError):
                pass
            
            # Resize image down for web efficiency
            max_size = (1600, 1600)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to RGB to ensure jpg saving works
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
                
            # Compress and save
            img.save(filepath, 'JPEG', quality=85, optimize=True)
        except Exception as e:
            # Fallback to direct save
            file_ext = os.path.splitext(file.filename)[1]
            filename = f"{photo_id}{file_ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.seek(0)
            file.save(filepath)
        
        # Store metadata
        photo_db[photo_id] = {
            'filename': filename,
            'original_name': file.filename
        }
        
        # URL for the customer to view the photo (this must be accessible from their phone)
        # In production this would be an https domain
        view_url = url_for('view_photo', photo_id=photo_id, _external=True)
        
        # URL to fetch the generated QR code image
        qr_url = url_for('get_qr', photo_id=photo_id, _external=True)
        
        return jsonify({
            'success': True,
            'photo_id': photo_id,
            'view_url': view_url,
            'qr_url': qr_url
        })

@app.route('/qrcode/<photo_id>')
def get_qr(photo_id):
    if photo_id not in photo_db:
        return "Photo not found", 404
        
    view_url = url_for('view_photo', photo_id=photo_id, _external=True)
    
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(view_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

@app.route('/view/<photo_id>')
def view_photo(photo_id):
    if photo_id not in photo_db:
        return "Photo not found!", 404
        
    return render_template('view.html', photo_id=photo_id)

@app.route('/image/<photo_id>')
def serve_image(photo_id):
    if photo_id not in photo_db:
        return "Photo not found", 404
    
    filename = photo_db[photo_id]['filename']
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download/<photo_id>')
def download_photo(photo_id):
    if photo_id not in photo_db:
        return "Photo not found", 404
    
    filename = photo_db[photo_id]['filename']
    # Download attachment uses the original photo name
    original_name = photo_db[photo_id].get('original_name', 'Vinod_Photography_Print.jpg')
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True, download_name=original_name)

if __name__ == '__main__':
    # Run the server. host='0.0.0.0' makes it accessible on the local network
    app.run(debug=True, host='0.0.0.0', port=5000)
