from flask import Flask, render_template, request, send_file, jsonify
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
import io
import re
import pandas as pd

app = Flask(__name__)

# Register Unicode-compatible font (Ensure 'NotoSans-Regular.ttf' is in the directory)
pdfmetrics.registerFont(TTFont("NotoSans", "NotoSans-Regular.ttf"))

# Load Samputeekarana map from Excel file
def load_samputeekarana_map_from_excel(excel_path):
    df = pd.read_excel(excel_path)
    # Assuming the first column contains line numbers and the second column contains mantras
    samputeekarana_map = {str(row[0]): row[1] for row in df.values}
    return samputeekarana_map

# Path to your Excel file
excel_file_path = "verses.xlsx"  # Update this with the correct path to your Excel file
samputeekarana_map = load_samputeekarana_map_from_excel(excel_file_path)

# Load Lalitha Sahasranama text
def load_lalitha_sahasranama():
    with open("lalitha_sahasranama.txt", "r", encoding="utf-8") as file:
        return file.readlines()

sahasranama_lines = load_lalitha_sahasranama()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_line_number = request.form["aspect"]
        samputeekarana = samputeekarana_map.get(selected_line_number, "Mantra not found")

        # Generate PDF with the selected line as samputeekarana
        pdf_buffer, pdf_filename = generate_pdf(selected_line_number, samputeekarana)

        return send_file(pdf_buffer, mimetype="application/pdf", as_attachment=True, download_name=pdf_filename)

    return render_template("index.html", aspects=samputeekarana_map.keys())

@app.route("/get-mantra", methods=["POST"])
def get_mantra():
    """Fetch the Samputeekarana mantra dynamically."""
    try:
        data = request.get_json()  # Get JSON data
        selected_aspect = data.get("aspect")  # Extract 'aspect' from request

        if not selected_aspect:
            return jsonify({"mantra": "Aspect not provided"}), 400

        mantra = samputeekarana_map.get(selected_aspect, "Mantra not found")
        return jsonify({"mantra": mantra})
    except Exception as e:
        return jsonify({"mantra": "Error processing request", "error": str(e)}), 500

def generate_pdf(selected_line_number, samputeekarana):
    """
    Generate a PDF with a centered header and footer.
    """
    safe_filename = f"Samputeekarana_LSN_{selected_line_number}.pdf"
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    def add_header_footer():
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawCentredString(width / 2, height - 30, "Sree Matre Namaha")
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawCentredString(width / 2, height - 50, "Sri Vidya Learning Center, Kanchipuram")
        pdf.setFont("Helvetica", 9)
        pdf.drawString(50, 40, "www.srimeru.org")
        pdf.drawString(50, 60, "www.facebook.com/Soundarya.Lahari")
        pdf.drawRightString(width - 50, 40, "8088256632, 8867709990")
        pdf.drawRightString(width - 50, 60, "srimeru999@gmail.com")

    pdf.setFont("NotoSans", 12)
    y = height - 80  # Start below the header

    for line in sahasranama_lines:
        if y < 50:
            add_header_footer()
            pdf.showPage()
            pdf.setFont("NotoSans", 12)
            y = height - 80

        pdf.drawString(100, y, samputeekarana)  # Add selected mantra
        y -= 20
        pdf.drawString(100, y, line.strip())
        y -= 20
        pdf.drawString(100, y, samputeekarana)  # Add selected mantra again
        y -= 40

    add_header_footer()  # Ensure footer is added before saving
    pdf.save()
    buffer.seek(0)

    return buffer, safe_filename


if __name__ == "__main__":
    app.run(debug=True)
