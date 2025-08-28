from flask import Flask, render_template, request
from datetime import datetime
from pm25 import get_open_data
import json

app = Flask(__name__)


from flask import Response


@app.route("/pm25", methods=["GET", "POST"])
def get_pm25():
    values = get_open_data(newest=True)

    if request.method == "POST":
        county = request.form.get("county")
        print(county)
        values = [value for value in values if value[1] == county]

    content = {
        "columns": ["site", "county", "pm25", "updatetime", "unit"],
        "values": values,
    }

    return render_template("pm25.html", content=content)
    # return Response(
    #     json.dumps(content, ensure_ascii=False),
    #     mimetype="application/json; charset=utf-8",
    # )


# 首頁
@app.route("/")
def index():
    now_time = time()
    return render_template("index.html", now_time=now_time)


@app.route("/time/")
def time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@app.route("/books/")
@app.route("/books/<int:id>")
def get_books(id=None):
    try:
        if id == None:
            return render_template("books.html", books=books)
        return books[id]
    except Exception as e:
        print(e)
        return f"編號錯誤:{e}"


# http://127.0.0.1:5000/bmi/height=176&weight=68
@app.route("/bmi/height=<height>&weight=<weight>")
def bmi(height, weight):
    try:
        bmi = round(eval(weight) / (eval(height) / 100) ** 2, 2)
        return f"身高:{height} 體重:{weight} <br> BMI={bmi}"
    except Exception as e:
        return f"參數錯誤:{e}"


books = {
    1: {
        "name": "Python book",
        "price": 299,
        "image_url": "https://im2.book.com.tw/image/getImage?i=https://www.books.com.tw/img/CN1/136/11/CN11361197.jpg&v=58096f9ck&w=348&h=348",
    },
    2: {
        "name": "Java book",
        "price": 399,
        "image_url": "https://im1.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/087/31/0010873110.jpg&v=5f7c475bk&w=348&h=348",
    },
    3: {
        "name": "C# book",
        "price": 499,
        "image_url": "https://im1.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/036/04/0010360466.jpg&v=62d695bak&w=348&h=348",
    },
}

if __name__ == "__main__":
    app.run(debug=True)
