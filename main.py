from flask import Flask, render_template, redirect, make_response, request, jsonify
from replit import db, web
import random, json
from markdown import markdown
from random import randint

app = Flask("")
mobile = '<meta name="viewport" content="width=device-width" />'

configf = open("config.json", "r")
config = json.loads(configf.read())
configf.close()



# Home

@app.route("/")
def html():
  fdb = open("frases.json", "r")
  frases = json.loads(fdb.read())
  fdb.close()
  frase=frases[randint(0, len(frases)-1)]
  if frase["autor"]:
    autor = frase["autor"]
  else:
    autor = "Anónimo"
  return mobile + markdown(render_template("index.md", frase=frase["frase"], autor=autor, ext="", warning=""))

@app.route("/.md")
def md():
  fdb = open("frases.json", "r")
  frases = json.loads(fdb.read())
  fdb.close()
  frase=frases[randint(0, len(frases)-1)]
  if frase["autor"]:
    autor = frase["autor"]
  else:
    autor = "Anónimo"
  resp = make_response(render_template("index.md", frase=frase["frase"], autor=autor, ext=".md", warning=" (HTML)"))
  resp.headers["Content-Type"] = "text/markdown; charset=utf-8"
  return resp



# API docs

@app.route("/api")
def apihtml():
  return mobile + markdown(render_template("json.md", ext=""))

@app.route("/api.md")
def apimd():
  resp = make_response(render_template("json.md", ext=".md"))
  resp.headers["Content-Type"] = "text/markdown; charset=utf-8"
  return resp

@app.route("/.json")
def apijson():
  fdb = open("frases.json", "r")
  frases = json.loads(fdb.read())
  fdb.close()
  frase = frases[randint(0, len(frases)-1)]
  return jsonify(frase=frase["frase"], autor=frase["autor"])

@app.route("/all.json")
def apialljson():
  fdb = open("frases.json", "r")
  frases = json.loads(fdb.read())
  fdb.close()
  return jsonify(lista=frases)

@app.route("/.xml")
def apixml():
  fdb = open("frases.json", "r")
  frases = json.loads(fdb.read())
  fdb.close()
  resp = make_response('<?xml version="1.0" encoding="UTF-8"?>\n<frase>' + frases[randint(0, len(frases)-1)] + '</frase>')
  resp.headers["Content-Type"] = "application/xml; charset=utf-8"
  return resp

@app.route("/all.xml")
def apiallxml():
  fdb = open("frases.json", "r")
  frases = json.loads(fdb.read())
  fdb.close()
  xml = '<?xml version="1.0" encoding="UTF-8"?>\n<lista>'
  for x in frases:
    xml += '\n<frase>' + x + '</frase>'
  xml += '\n</lista>'
  resp = make_response(xml)
  resp.headers["Content-Type"] = "application/xml; charset=utf-8"
  return resp



# Sugerir

@app.route("/sugerir", methods=["GET", "POST"])
def sugerir():
  if request.method == "POST":
    try:
      frase = str(request.form["frase"]).replace("|", "&#124;")
      if "nombre" in request.form and request.form["nombre"]:
        nombre = str(request.form["nombre"]).replace("|", "&#124;")
      else:
        nombre = False
      try:
        db["sugerencias"].append([frase, nombre])
      except:
        db["sugerencias"] = [[frase, nombre]]
      error = ""
    except:
      error = ":D"
  else:
    error = ""
  return mobile + markdown(render_template("sugerir.md", error=error))

@app.route("/sugerir/beta", methods=["GET", "POST"])
def sugerirbeta():
  if request.method == "POST":
    try:
      frase = str(request.form["frase"]).replace("|", "&#124;")
      if "nombre" in request.form and request.form["nombre"]:
        nombre = str(request.form["nombre"]).replace("|", "&#124;")
      else:
        nombre = False
      try:
        db["sugerencias"].append([frase, nombre])
      except:
        db["sugerencias"] = [[frase, nombre]]
      error = ""
    except:
      error = ":D"
  else:
    error = ""
  return mobile + markdown(render_template("sugerirbeta.md", error=error))



# Dash

@app.route("/dash")
@web.authenticated
def dash():
  if web.auth.name == config["replit"]:
    return redirect("/dash/sugerencias")
  else:
    return "<h1>Restrictred</h1>"

@app.route("/dash/sugerencias")
@web.authenticated
def sugerencias():
  if web.auth.name == config["replit"]:
    # Tabla
    tabla = ""
    i = 0
    for x in db["sugerencias"]:
      if not x[1]: nombre = "Anónimo"
      else: nombre = x[1]
      tabla += f"|{x[0]}|{nombre}|[Add](/dash/sugerencias/add/{str(i)}) [Del](/dash/sugerencias/remove/{str(i)})|\n"
      i = i+1
    return mobile + markdown(render_template("dash.md", tabla=tabla), extensions=["tables"])
  else:
    return "<h1>Restrictred</h1>"

@app.route("/dash/sugerencias/remove/<id>")
@web.authenticated
def sugerenciasremove(id):
  if web.auth.name == config["replit"]:
    del db["sugerencias"][int(id)]
    return redirect("/dash/sugerencias")
  else:
    return "<h1>Restrictred</h1>"

@app.route("/dash/sugerencias/add/<id>")
@web.authenticated
def sugerenciasadd(id):
  if web.auth.name == config["replit"]:
    fdb = open("frases.json", "r")
    frases = json.loads(fdb.read())
    fdb.close()
    frases.append({"frase": db["sugerencias"][int(id)][0], "autor": db["sugerencias"][int(id)][1]})
    fdb = open("frases.json", "w")
    fdb.write(json.dumps(frases))
    del db["sugerencias"][int(id)]
    return redirect("/dash/sugerencias")
  else:
    return "<h1>Restrictred</h1>"

app.run(host="0.0.0.0")