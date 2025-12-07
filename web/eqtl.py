from flask import Flask, request, jsonify, render_template
import mysql.connector
import os

app = Flask(__name__)

# Database connection
db_config = {
    'host': 'localhost',
    'user': 'flask_user',
    'password': 'wheateQTLs@2025',
    'database': 'eqtl'
}

# Path to the folder containing images
IMAGE_FOLDER = "static/image"

@app.route("/", methods=["GET", "POST"])

def search_gene():
    results = []
    photos = []
    
    if request.method == "POST":
        name_query = request.form.get("name")

        # Connect to MySQL and fetch matching rows
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM wheat WHERE Geneid LIKE %s"
        cursor.execute(query, (f"%{name_query}%",))
        results = cursor.fetchall()

        # Generate photo filenames based on naming convention
        if name_query:
            grades = ["PRJNA670223", "PRJNA795836", "PRJNA838764", "PRJNA912645"]
            photos = []

            # Create photo filenames for the four grades
            for grade in grades:
                photo_filename = f"{grade}_{name_query}.FarmCPU.GWAS.png"  # Starting with 1 and changing the number dynamically later
                photo_path = os.path.join(IMAGE_FOLDER, photo_filename)
                if os.path.exists(photo_path):
                    photos.append((grade, photo_filename))

            # Check for missing photos and handle it in the HTML rendering part
            if len(photos) < 4:
                # Fill in placeholders for missing grades
                for grade in grades:
                    if not any(grade in photo[0] for photo in photos):
                        photos.append((grade, None))

        cursor.close()
        conn.close()

    return render_template("index.html", results=results, photos=photos)

if __name__ == "__main__":
    app.run(debug=True)


