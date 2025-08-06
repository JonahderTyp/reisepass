import io

from flask import (Blueprint, Flask, redirect, render_template, request,
                   send_file, session, url_for)
from flask_socketio import emit
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from ..database.db import member
from ..database.exceptions import ElementDoesNotExsist

card_site = Blueprint(
    "card", __name__, template_folder="templates", url_prefix="/card")


def generate_id_pdf(data, size=3):
    """
    Generate a PDF with ID-like cards arranged in a 3x3 grid, with an extra outer margin.
    Each card shows the provided personal details and a QR code with demo data.

    Parameters:
      data: A list of dictionaries with keys: 'vorname', 'nachname', 'geburtstag', 'size', and 'weight'.

    Returns:
      A BytesIO buffer containing the PDF.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    page_width, page_height = A4

    # Outer margin around the edge of the paper (20 mm)
    outer_margin = 8 * mm

    # Available drawing area after reserving outer margins
    avail_width = page_width - 2 * outer_margin
    avail_height = page_height - 2 * outer_margin

    # Define grid: 3 columns x 3 rows per page
    card_width = avail_width / size
    card_height = avail_height / size

    text_margin = 20/size  # inner margin for text and QR code within each card
    qr_size = 250/size      # size (in points) for the QR code
    plane_image_path = "./reisepass/database/plane.png"  # Path to the plane image file
    plane_width = 300/size  # desired width in points for the plane image
    plane_height = 300/size  # desired height in points for the plane image

    size_bold = 44/size
    size_regular = 36/size
    size_small = 24/size

    styles = getSampleStyleSheet()
    detail_style = styles["Normal"].clone('detail_style')
    detail_style.fontName = "Helvetica"
    detail_style.fontSize = size_regular
    detail_style.leading = size_regular * 1.2

    person: member
    for idx, person in enumerate(data):
        card_index = idx % size ** 2
        col = card_index % size
        # Reverse row order to have the first row at the top
        row = (size - 1) - (card_index // size)

        # Calculate x, y positions including outer margin
        x = outer_margin + col * card_width
        y = outer_margin + row * card_height

        # Draw the card border
        c.rect(x, y, card_width, card_height)

        # Draw the plane image in the top-right corner of the card
        # plane_x = x + card_width - text_margin - plane_width
        # plane_y = y + card_height - text_margin - plane_height
        plane_x = x + (card_width - plane_width) / 2
        plane_y = y + (card_height - plane_height) / 2
        try:
            c.drawImage(plane_image_path, plane_x, plane_y,
                        width=plane_width, height=plane_height,
                        preserveAspectRatio=True, mask='auto')
        except Exception as e:
            # In case the image is not found or fails to load, simply pass
            print(f"Error loading image: {e}")

        # Set the text starting position near the top of the card
        text_x = x + text_margin
        text_y = y + card_height - text_margin - size_bold

        # Draw full name in bold
        c.setFont("Helvetica-Bold", size_bold)
        c.drawString(text_x, text_y, person.vorname)
        text_y -= size_bold  # move down for the next line
        c.drawString(text_x, text_y, person.nachname)

        beruf = person.jsondata.get("beruf", "Pfadfinder")

        # Draw additional details in regular font, word-wrapped
        details = [
            f"Geburtstag: {person.geburtstag}",
            f"Stufe: {person.stufe.name}",
            f"{beruf}",
        ]
        detail_text = "<br/>".join(details)
        para = Paragraph(detail_text, detail_style)
        w, h = para.wrap(card_width - 2 * text_margin, card_height)
        text_y -= h  # move down for the paragraph height
        para.drawOn(c, text_x, text_y)

        # Create a QR code with demo data
        qr_data = person.code
        qr_code = qr.QrCodeWidget(qr_data, barLevel='M')
        bounds = qr_code.getBounds()
        qr_width_val = bounds[2] - bounds[0]
        qr_height_val = bounds[3] - bounds[1]
        # Scale the QR code to the desired size
        d = Drawing(qr_size, qr_size, transform=[
                    qr_size/qr_width_val, 0, 0, qr_size/qr_height_val, 0, 0])
        d.add(qr_code)
        # Position the QR code at the bottom-right of the card
        qr_x = x + card_width - qr_size + (text_margin/2)
        qr_y = y + text_margin
        renderPDF.draw(d, c, qr_x, qr_y)
        c.setFont("Helvetica-Oblique", size_small)
        c.drawString(qr_x + (qr_size / 4),
                     qr_y + qr_size - size_small,
                     qr_data)

        c.setFont("Helvetica-Oblique", size_small)
        details = [
            "DPSG St. Stephanus Beckum",
            "Simon Wessel:",
            "0176 12345678",
            "Nele Braunart:",
            "0176 87654321",
            "Zeltplatz:",
            "Talsperrenstraße 90",
            "53881 Euskirchen"
        ]
        text_y = y + text_margin + (len(details) + 1) * size_small
        for detail in details:
            text_y -= size_small  # move down for each line
            c.drawString(text_x, text_y, detail)

        # Start a new page after every 9 cards
        if (idx + 1) % (size * size) == 0:
            c.showPage()

    c.save()
    buffer.seek(0)
    return buffer


@card_site.route("/")
def index():
    return render_template("card/download.html")


@card_site.get("/download")
def download():
    # Sample data for demonstration. In a real scenario, you might retrieve this from a database or request.
    size = request.args.get("size", default=3, type=int)
    print(f"Generating ID cards with size: {size}")
    pdf_buffer = generate_id_pdf(member.get_all(), size=int(size))
    return send_file(pdf_buffer,
                     as_attachment=False,
                     download_name="id_cards.pdf",
                     mimetype="application/pdf")
