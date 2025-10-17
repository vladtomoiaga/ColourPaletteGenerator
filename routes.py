from datetime import datetime
import os
from flask import Blueprint, render_template, request, flash, redirect, current_app
from werkzeug.utils import secure_filename
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.image as mpimg

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

routes = Blueprint("routes", __name__)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@routes.context_processor
def inject_current_year():
    """This method is setting the current year"""
    return {"current_year": datetime.now().year}


@routes.route("/", methods=["GET", "POST"])
def home():
    """This method create the route the Home page"""

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_folder, filename))

            # Complete filepath. Needed for imread
            complete_image_filepath = f"{upload_folder}{filename}"

            colour_list = []

            try:
                image = mpimg.imread(complete_image_filepath)
            except FileNotFoundError:
                return render_template("index.html", message="Image was not found.")
            else:
                # This line of code is for images who has 4 canals: PNG, TIFF, JPEG, etc. Eliminates Alpha canal
                if image.shape[2] == 4:
                    image = image[:, :, :3]

                # Get the dimensions (width, height, and depth) of the image
                w, h, d = tuple(image.shape)

                # Reshape the image into a 2D array, where each row represents a pixel
                pixel = np.reshape(image, (w * h, d))

                # Set the desired number of colors for the image. In this project the value was set to 10.
                number_colors = 10

                # Create a KMeans model with the specified number of clusters and fit it to the pixels.
                model = KMeans(n_clusters=number_colors, random_state=42).fit(pixel)

                labels = model.labels_
                counts = np.bincount(model.labels_)
                totals = labels.size
                # Percentage only from the number_colors. In this case is 10.
                percentage = (counts / totals) * 100

                # Get the cluster centers (representing colors) from the model. Some images (ex: PNG) can have values between 0 and 1.
                colour_palette = np.uint8(model.cluster_centers_ * 255) if image.max() <= 1.0 \
                                                                        else np.uint8(model.cluster_centers_)

                for color, percent in zip(colour_palette, percentage):
                    colour_list.append((f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}", f"{percent:.4f}"))

                sorted_colour_list = sorted(colour_list, reverse=True, key=lambda x: float(x[1]))
                return render_template("index.html", colours=sorted_colour_list, image=complete_image_filepath)

    return render_template("index.html")
