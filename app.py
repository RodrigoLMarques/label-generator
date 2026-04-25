import os
import tempfile
import cups
from io import BytesIO
from flask import Flask, request, send_file, render_template, jsonify
from dotenv import load_dotenv
from main import parse_lines, generate_pdf

load_dotenv()

app = Flask(__name__)

PRINTER_NAME = os.getenv("PRINTER_NAME", "epson")
PRINT_OPTIONS = {"media": "A5", "orientation-requested": "4"}
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

def _collect_labels():
    quantities = request.form.getlist("qty")
    values = request.form.getlist("val")
    lines = [f"{q}xR${v}" for q, v in zip(quantities, values)
             if q and v and q.isdigit() and 0 < int(q) < 1000]
    return parse_lines(lines)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/gerar", methods=["POST"])
def generate():
    labels = _collect_labels()

    if not labels:
        return "No labels provided.", 400

    buf = BytesIO()
    generate_pdf(labels, buf)
    buf.seek(0)

    return send_file(buf, mimetype="application/pdf",
                     as_attachment=True, download_name="labels.pdf")


@app.route("/imprimir", methods=["POST"])
def print_labels():
    labels = _collect_labels()

    if not labels:
        return jsonify({"error": "Nenhuma etiqueta fornecida."}), 400

    if DRY_RUN:
        return jsonify({"job": 0, "total": len(labels)})

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(tmp_fd)
    try:
        generate_pdf(labels, tmp_path)
        conn = cups.Connection()
        job_id = conn.printFile(PRINTER_NAME, tmp_path, "Etiquetas", PRINT_OPTIONS)
    finally:
        os.unlink(tmp_path)

    return jsonify({"job": job_id, "total": len(labels)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=False)
