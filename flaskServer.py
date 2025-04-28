from flask import Flask, render_template, url_for, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from PIL import Image, ExifTags
from pillow_heif import register_heif_opener

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    file = db.Column(db.LargeBinary)
    filename = db.Column(db.String(200))
    pic_orientation = db.Column(db.Integer)

    def __repr__(self):
        return f'<Data {self.name}>'
    
with app.app_context():
    db.create_all()

def resize_and_crop(img, target_width=600, target_height=448):
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        new_height = target_height
        new_width = int(new_height * img_ratio)
    else:
        new_width = target_width
        new_height = int(new_width / img_ratio)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Step 2: Center crop
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    return img.crop((left, top, right, bottom))


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    deletePicture = Data.query.get_or_404(id)

    try:
        db.session.delete(deletePicture)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an issue deleting your picture'
    
@app.route('/image/<int:id>')
def image(id):
    pic = Data.query.get_or_404(id)
    return send_file(BytesIO(pic.file), mimetype='image/jpeg')

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        picName = request.form['picName']
        picFile = request.files['picFile']

        try:
            register_heif_opener()
            img = Image.open(picFile.stream)

            orientation = None
            try:
                exif = img._getexif()
                if exif is not None:
                    for tag, value in exif.items():
                        decoded_tag = ExifTags.TAGS.get(tag, tag)
                        if decoded_tag == 'Orientation':
                            orientation = value
                            break
            except Exception as e:
                print(f"EXIF reading error: {e}")

            img = resize_and_crop(img)

            img_io = BytesIO()
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(img_io, format='JPEG', quality=90)
            img_io.seek(0)

            newPic = Data(
                name=picName,
                filename=picFile.filename,
                file=img_io.read(),
                pic_orientation=orientation
            )

        except Exception as e:
            return f"Please enter a valid picture. Error: {e}"

        try:
            db.session.add(newPic)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f'There was an issue adding your picture: {e}'

    else:
        pictures = Data.query.order_by(Data.name).all()
        return render_template('index.html', pictures=pictures)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')