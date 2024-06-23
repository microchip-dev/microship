import io
import os
import socket
import tqdm
from flask import Flask, request, send_file
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

app = Flask(__name__)

def extract_text(file_path):
    pdf_file_obj = open(file_path, 'rb')
    pdf_reader = PdfReader(pdf_file_obj)
    if len(pdf_reader.pages) > 5:
        print("El PDF tiene más de 5 páginas, no se cargará.")
        return ""
    text = ''
    for page_num in tqdm.tqdm(range(len(pdf_reader.pages))):
        page_obj = pdf_reader.pages[page_num]
        text += page_obj.extract_text()
    pdf_file_obj.close()
    return text

def make_bold(text):
    words = text.split()
    bold_words = []
    for word in words:
        bold_words.append(f'<b>{word[0]}</b>{word[1:]}')
    return ' '.join(bold_words)

def generate_pdf(text, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='NormalText', fontSize=12, leading=14, spaceBefore=0, spaceAfter=0, leftIndent=0, rightIndent=0, firstLineIndent=0, alignment=TA_JUSTIFY, fontName='Helvetica'))
    elements = []
    elements.append(Paragraph(text, styles['NormalText']))
    doc.build(elements)

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    file = request.files['file']
    input_path = os.path.join('/tmp', file.filename)
    file.save(input_path)
    text = extract_text(input_path)
    if text:
        bold_text = make_bold(text)
        output_path = os.path.join('/tmp', 'output.pdf')
        generate_pdf(bold_text, output_path)
        return send_file(output_path, as_attachment=True)
    else:
        return "El PDF tiene más de 5 páginas, no se procesó.", 400

@app.route('/hook')
def hook():
    return "<h2 style='font-weight: 400'>Hello world</h2>"

if __name__ == '__main__':
    if 'PORT' in os.environ:
        port = int(os.environ.get('PORT'))
        print(f"Listening on IP {socket.gethostbyname(socket.gethostname())} and port {port}")
    else:
        port = 5000
        print(f"Listening on IP {socket.gethostbyname(socket.gethostname())} and port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
