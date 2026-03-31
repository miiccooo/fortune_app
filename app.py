from flask import Flask, render_template, request
from datetime import date
from main import fortune_from_birthdate

app = Flask(__name__)

# -----------------------------------
# トップページ表示（GET）
# -----------------------------------
@app.get("/")
def index():
    # 今日の日付をHTMLに渡す（カレンダー制限などに使える）
    return render_template("index.html", today=date.today().isoformat())


# -----------------------------------
# フォーム送信後の処理（POST）
# -----------------------------------
@app.post("/result")
def result():

    # ▼ HTMLの<select>から値を取得
    # name="year" とかに対応してる
    year = request.form.get("year")
    month = request.form.get("month")
    day = request.form.get("day")

    # ▼ どれか未選択だったらエラー
    if not year or not month or not day:
        return render_template(
            "index.html",
            error="日付を選んでね",  # エラーメッセージ表示
            today=date.today().isoformat()
        )

    # ▼ 文字列を YYYY-MM-DD の形に整える
    # int(month):02 → 01,02みたいに2桁にする
    birth = f"{year}-{int(month):02}-{int(day):02}"

    try:
        # ▼ 占い処理を実行（main.pyの関数）
        data = fortune_from_birthdate(birth)

        # ▼ 結果ページへ
        return render_template("result.html", data=data, error=None)

    except Exception as e:
        # ▼ エラーが起きたときは入力画面に戻す
        return render_template(
            "index.html",
            error=str(e),  # エラー内容表示
            year=year,     # 選択状態を保持
            month=month,
            day=day,
            today=date.today().isoformat()
        )


# -----------------------------------
# アプリ起動
# -----------------------------------
if __name__ == "__main__":
    app.run(debug=True)