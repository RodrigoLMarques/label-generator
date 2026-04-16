from io import BytesIO
from flask import Flask, request, send_file, render_template
from main import parsear_linhas, gerar_pdf

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/gerar", methods=["POST"])
def gerar():
    quantidades = request.form.getlist("qty")
    valores = request.form.getlist("val")
    linhas = [f"{q}xR${v}" for q, v in zip(quantidades, valores)
              if q and v and q.isdigit() and 0 < int(q) < 1000]
    etiquetas = parsear_linhas(linhas)

    if not etiquetas:
        return "Nenhuma etiqueta informada.", 400

    buf = BytesIO()
    gerar_pdf(etiquetas, buf)
    buf.seek(0)

    return send_file(buf, mimetype="application/pdf",
                     as_attachment=True, download_name="etiquetas.pdf")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=False)
