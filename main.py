from flask import Flask, render_template, request
import uuid
from werkzeug.utils import secure_filename
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'user_uploads')
REELS_FOLDER = os.path.join(BASE_DIR, 'static', 'reels')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REELS_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    myid = uuid.uuid1()
    if request.method == "POST":
        rec_id = request.form.get("uuid")
        desc = request.form.get("text", "")
        if not rec_id:
            return "Missing uuid", 400
        rec_id = secure_filename(rec_id)
        folder = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
        os.makedirs(folder, exist_ok=True)

        input_files = []
        for key in request.files:
            file = request.files[key]
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(folder, filename))
                input_files.append(filename)

        if not input_files:
            return "Please upload at least one image (png, jpg, jpeg, webp).", 400

        with open(os.path.join(folder, "desc.txt"), "w", encoding="utf-8") as f:
            f.write(desc)

        # input.txt is written LAST: generate_process.py only starts once it exists.
        # ffmpeg's concat demuxer ignores the duration of the final file, so repeat it.
        with open(os.path.join(folder, "input.txt"), "w", encoding="utf-8") as f:
            for fl in input_files:
                f.write(f"file '{fl}'\nduration 1\n")
            f.write(f"file '{input_files[-1]}'\n")

    return render_template("create.html", myid=myid)


@app.route("/gallery")
def gallery():
    reels = sorted(f for f in os.listdir(REELS_FOLDER) if f.endswith(".mp4"))
    return render_template("gallery.html", reels=reels)


if __name__ == "__main__":
    app.run(debug=True)
