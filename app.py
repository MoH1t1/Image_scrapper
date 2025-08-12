from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import logging
import pymongo 
logging.basicConfig(filename="scrappers.log" , level=logging.INFO)
import os

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
                try: 
                    query = request.form['content'].strip()
                    if not query:
                         return "Please enter a search term", 400
                
                    query = query.replace(" ", "_")                        # query to search for images
                    save_directory = os.path.join("static", "images")      # directory to store downloaded images
                    if not os.path.exists(save_directory):
                        os.makedirs(save_directory)
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
                    response = requests.get(f"https://www.google.com/search?q={query}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")
                    soup = BeautifulSoup(response.content, "html.parser")
                    image_tags = soup.find_all("img")
                    del image_tags[0]
                    img_data=[]
                    for index,image_tag in enumerate(image_tags[:5]):                     # range limits it to on;y 5 images downlaod
                                image_url = image_tag['src']
                                image_data = requests.get(image_url).content              # send a request to the image URL and save the image
                                mydict={"Index":index,"Image":image_data}
                                img_data.append(mydict)
                                with open(os.path.join(save_directory, f"{query}_{image_tags.index(image_tag)}.jpg"), "wb") as f:
                                    f.write(image_data)
                    client = client = pymongo.MongoClient("mongodb+srv://mohitagarwalq:N495PW544Ca5isPT@cluster0.kgmzehs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
                    db = client['image_scrap']
                    review_col = db['image_scrap_data']
                    review_col.insert_many(img_data)          
                    image_urls = [f"/static/images/{query}_{i}.jpg" for i in range(len(image_tags[:5]))]
                    return render_template("result.html", query=query.replace("_", " "),images=image_urls)
                except Exception as e:
                    logging.info(e)
                    return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

