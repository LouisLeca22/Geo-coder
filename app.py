from flask import Flask, render_template, request, send_file
import pandas 
from geopy.geocoders import ArcGIS
import datetime 
import folium 

app=Flask(__name__)

nom = ArcGIS()


@app.route("/")
def index():
    return render_template("index.html", active="active")

@app.route("/success", methods=['POST'])
def success():
    global filename
    if request.method=="POST":
        file = request.files["file"]
        try:
            df = pandas.read_csv(file, sep=",")
            if "adresse" in df.columns or "Adresse" in df.columns:
                if "adresse" in df.columns:
                    df = df.rename(columns={"adresse": "Adresse"})
                df["Latitude"]=df["Adresse"].apply(nom.geocode).apply(lambda x: x.latitude if x != None else None)
                df["Longitude"]=df["Adresse"].apply(nom.geocode).apply(lambda x: x.longitude if x != None else None)
                filename =datetime.datetime.now().strftime("uploads/"+file.filename.split(".")[0]+"_%Y-%m-%d-%H-%M-%S-%f"+".csv")
                df_html = df.to_html(index=False)
                df.to_csv(filename, index=False)

                zipped = list(zip(df["Latitude"], df["Longitude"], df["Adresse"]))
                htmlDeco = """ <h4>Adresse :</h4>
                <p> %s </p>
                """

                map = folium.Map(location=[0,0], zoom_start=2, tiles="Stamen Terrain")
                fg = folium.FeatureGroup(name="My Map") 

                for item in zipped:
                    iframe = folium.IFrame(html=htmlDeco % item[2], width=300, height=110)
                    fg.add_child(folium.Marker(location=[item[0],item[1]], popup=folium.Popup(iframe), icon=folium.Icon(color="orange")))
                
                map.add_child(fg)

                map = map._repr_html_()

                return render_template("index.html", df_html=df_html, btn="download.html", map=map)
            else:
                return render_template("index.html", error="Ajouter un fichier csv qui contient au moins une colonne nommée Adresse ou adresse")
        except Exception as e:
            return render_template("index.html", text="Verifier votre fichier", active="")

@app.route("/download")
def download():
    return send_file(filename, attachment_filename="fichier.csv", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=False)

