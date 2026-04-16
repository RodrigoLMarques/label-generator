from io import BytesIO
from flask import Flask, request, send_file, render_template
from main import parse_lines, generate_pdf

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/gerar", methods=["POST"])
def generate():
    quantities = request.form.getlist("qty")
    values = request.form.getlist("val")
    lines = [f"{q}xR${v}" for q, v in zip(quantities, values)
             if q and v and q.isdigit() and 0 < int(q) < 1000]
    labels = parse_lines(lines)

    if not labels:
        return "No labels provided.", 400

    buf = BytesIO()
    generate_pdf(labels, buf)
    buf.seek(0)

    return send_file(buf, mimetype="application/pdf",
                     as_attachment=True, download_name="labels.pdf")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=False)
