# -*- coding: utf-8 -*-

# JSON読み込み、ランダム抽選、コマンドライン引数を使うため
import json, random, sys

# 日付の変換・比較に使う
from datetime import datetime, date

# ファイルパス操作に使う
from pathlib import Path

#カラーマップ

COLOR_MAP = {
    "レッド": "red",
    "コーラル": "coral",
    "ゴールド": "gold",
    "ベージュ": "beige",
    "ブラウン": "brown",
    "オリーブ": "olive",
    "イエロー": "yellow",
    "ミント": "mintcream",
    "スカイブルー": "skyblue",
    "ネイビー": "navy",
    "ブルー": "blue",
    "ラベンダー": "lavender"
}
# -----------------------------
# データファイルの場所
# -----------------------------
# main.py があるフォルダを基準に data フォルダを見る
DATA_DIR = Path(__file__).parent / "data"

# 各JSONファイルのパス
ZODIAC_PATH = DATA_DIR / "zodiac.json"                  # 星座データ
TAROT_PATH = DATA_DIR / "tarot.json"                    # 大アルカナデータ
MINOR_PATH = DATA_DIR / "minor_structure.json"          # 小アルカナ構造データ
ELEMENT_MSG_PATH = DATA_DIR / "element_messages.json"   # 五行メッセージ（あれば使う）
MAJOR_IMAGE_PATH = DATA_DIR / "major_images.json"       # 大アルカナ画像対応表
HINT_RULES_PATH = DATA_DIR / "hint_rules.json"          # ヒント生成用ルール
RISSHUN_PATH = DATA_DIR / "risshun_1966_2060.json"      # 立春データ

# -----------------------------
# ラッキーカラーの関数
# -----------------------------
def convert_colors(color_list):
    result = []
    for c in color_list:
        result.append({
            "name": c,                     # 表示用（日本語）
            "code": COLOR_MAP.get(c, "#ccc")  # CSS用（英語 or fallback）
        })
    return result


# -----------------------------
# JSONファイルを読む関数
# -----------------------------
def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------------
# 占いで使うJSONデータをまとめて読み込む
# -----------------------------------
def load_fortune_data():
    # 星座データ
    zodiac = load_json(ZODIAC_PATH)

    # 大アルカナデータ
    major = load_json(TAROT_PATH)

    # 小アルカナ構造データ
    minor_struct = load_json(MINOR_PATH)

    # 五行メッセージ（ファイルがあるときだけ読む）
    element_msgs = {}
    if ELEMENT_MSG_PATH.exists():
        element_msgs = load_json(ELEMENT_MSG_PATH)

    # 大アルカナ画像対応表
    major_images = load_json(MAJOR_IMAGE_PATH)

    # ヒント生成ルール
    hint_rules = load_json(HINT_RULES_PATH)


    # まとめて返す
    return zodiac, major, minor_struct, element_msgs, major_images, hint_rules


# -----------------------------
# 生年月日の文字列チェック
# -----------------------------
def parse_birthdate(text: str) -> date:
    # None対策＋前後の空白を削除
    text = (text or "").strip()

    # 未入力ならエラー
    if not text:
        raise ValueError("未入力です。YYYY-MM-DD 形式で入力してください。")

    # YYYY-MM-DD の形で日付に変換
    try:
        dt = datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        # 形式が違えばエラー
        raise ValueError("形式が違います。YYYY-MM-DD 形式で入力してください。")

    # 未来日は不可
    if dt > date.today():
        raise ValueError("未来日は入力できません。")

    return dt


# -----------------------------
# 太陽星座のキーを返す
# -----------------------------
def get_zodiac_key(month: int, day: int) -> str:
    # 月日を 1214 みたいな形にして判定しやすくする
    md = month * 100 + day

    if 321 <= md <= 419:
        return "aries"
    if 420 <= md <= 520:
        return "taurus"
    if 521 <= md <= 620:
        return "gemini"
    if 621 <= md <= 722:
        return "cancer"
    if 723 <= md <= 822:
        return "leo"
    if 823 <= md <= 922:
        return "virgo"
    if 923 <= md <= 1022:
        return "libra"
    if 1023 <= md <= 1121:
        return "scorpio"
    if 1122 <= md <= 1221:
        return "sagittarius"
    if md >= 1222 or md <= 119:
        return "capricorn"
    if 120 <= md <= 218:
        return "aquarius"
    return "pisces"

SIGN_ELEMENT = {
    "aries": "fire",
    "leo": "fire",
    "sagittarius": "fire",
    "taurus": "earth",
    "virgo": "earth",
    "capricorn": "earth",
    "gemini": "air",
    "libra": "air",
    "aquarius": "air",
    "cancer": "water",
    "scorpio": "water",
    "pisces": "water"
}


def get_today_zodiac():
    today = date.today()
    return get_zodiac_key(today.month, today.day)


def tarot_to_element(card_name: str):
    if "太陽" in card_name or "戦車" in card_name:
        return "fire"
    if "星" in card_name or "月" in card_name:
        return "water"
    if "皇帝" in card_name or "世界" in card_name:
        return "earth"
    if "魔術師" in card_name or "愚者" in card_name:
        return "air"
    return None


def calculate_element_balance(zkey: str, t_major: dict):
    score = {
        "fire": 0,
        "earth": 0,
        "air": 0,
        "water": 0
    }

    # 生まれ持ったベース（太陽星座）
    natal_elem = SIGN_ELEMENT[zkey]
    score[natal_elem] += 2

    # 今日の空気（今日の太陽星座）
    today_key = get_today_zodiac()
    today_elem = SIGN_ELEMENT[today_key]
    score[today_elem] += 1

    # タロット補正
    tarot_elem = tarot_to_element(t_major["name"])
    if tarot_elem:
        if t_major["position"] == "逆位置":
            score[tarot_elem] -= 1
        else:
            score[tarot_elem] += 1

    return score


def get_lucky_color_v2(zkey: str, t_major: dict):
    score = calculate_element_balance(zkey, t_major)

    ELEMENT_COLORS = {
        "fire": ["レッド", "コーラル", "ゴールド"],
        "earth": ["ベージュ", "ブラウン", "オリーブ"],
        "air": ["イエロー", "ミント", "スカイブルー"],
        "water": ["ネイビー", "ブルー", "ラベンダー"]
    }

    weakest = min(score, key=score.get)
    strongest = max(score, key=score.get)

    ELEMENT_LABELS = {
        "fire": "火",
        "earth": "地",
        "air": "風",
        "water": "水"
    }

    return {
        "balance": ELEMENT_COLORS[weakest],
        "boost": ELEMENT_COLORS[strongest],
        "weakest": weakest,
        "strongest": strongest,
        "weakest_label": ELEMENT_LABELS[weakest],
        "strongest_label": ELEMENT_LABELS[strongest],
        "score": score
    }

# -----------------------------
# 立春データ読み込み
# -----------------------------
with RISSHUN_PATH.open("r", encoding="utf-8") as f:
    RISSHUN_DATA = json.load(f)

def get_adjusted_year(birth_str):
    """立春日ベースで年を補正する（時間入力なし版）"""
    birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
    year = birth_date.year

    risshun = RISSHUN_DATA.get(str(year))
    if not risshun:
        return year

    risshun_date = datetime.strptime(risshun["japan_date"], "%Y-%m-%d").date()

    if birth_date < risshun_date:
        return year - 1
    return year


# -----------------------------
# 四柱推命（簡易）用データ
# -----------------------------
# 十干
TENKAN = [
    {"jp": "甲", "elem": "木", "yin_yang": "陽"},
    {"jp": "乙", "elem": "木", "yin_yang": "陰"},
    {"jp": "丙", "elem": "火", "yin_yang": "陽"},
    {"jp": "丁", "elem": "火", "yin_yang": "陰"},
    {"jp": "戊", "elem": "土", "yin_yang": "陽"},
    {"jp": "己", "elem": "土", "yin_yang": "陰"},
    {"jp": "庚", "elem": "金", "yin_yang": "陽"},
    {"jp": "辛", "elem": "金", "yin_yang": "陰"},
    {"jp": "壬", "elem": "水", "yin_yang": "陽"},
    {"jp": "癸", "elem": "水", "yin_yang": "陰"},
]

# 十二支
JUNISHI = [
    {"jp": "子", "animal": "鼠"},
    {"jp": "丑", "animal": "牛"},
    {"jp": "寅", "animal": "虎"},
    {"jp": "卯", "animal": "兎"},
    {"jp": "辰", "animal": "龍"},
    {"jp": "巳", "animal": "蛇"},
    {"jp": "午", "animal": "馬"},
    {"jp": "未", "animal": "羊"},
    {"jp": "申", "animal": "猿"},
    {"jp": "酉", "animal": "鶏"},
    {"jp": "戌", "animal": "犬"},
    {"jp": "亥", "animal": "猪"},
]

# -----------------------------
# 年柱（干支）を求める
# -----------------------------
def get_year_ganzhi(year: int) -> dict:
    """
    1984年=甲子 を基準に年干支を求める簡易方式
    厳密な四柱推命は立春基準などがあるけど、
    この個人制作では西暦年ベースでわかりやすくしている
    """
    base = 1984  # 甲子の年
    diff = year - base

    # 10干と12支は周期が違うので、それぞれ余りで求める
    stem = TENKAN[diff % 10]
    branch = JUNISHI[diff % 12]

    # 必要情報をまとめて返す
    return {
        "stem": stem["jp"],                 # 十干
        "branch": branch["jp"],             # 十二支
        "ganzhi": stem["jp"] + branch["jp"],# 干支の組み合わせ
        "elem": stem["elem"],               # 五行
        "yin_yang": stem["yin_yang"],       # 陰陽
        "animal": branch["animal"],         # 動物
    }


# -----------------------------
# 小アルカナを1枚引く
# -----------------------------
def draw_minor(minor_struct: dict) -> dict:
    # スート（例：ソード、カップなど）一覧
    suits = list(minor_struct["suits"].keys())

    # ランク（例：エース、2、クイーンなど）一覧
    ranks = list(minor_struct["ranks"].keys())

    # スートとランクをランダムに選ぶ
    suit_key = random.choice(suits)
    rank_key = random.choice(ranks)

    # 50%で逆位置
    reversed_flag = random.random() < 0.5

    # 選ばれたデータを取り出す
    suit = minor_struct["suits"][suit_key]
    rank = minor_struct["ranks"][rank_key]

    # 正逆で意味を切り替える
    rank_meaning = rank["reversed"] if reversed_flag else rank["upright"]
    suit_keywords = suit["keywords_reversed"] if reversed_flag else suit["keywords_upright"]

    # 表示用メッセージを作る
    meaning = f"{suit['theme']}｜{rank_meaning}（キーワード：{random.choice(suit_keywords)}）"

    return {
        "type": "minor",
        "name": f"{suit['jp']}の{rank['jp']}",
        "position": "逆位置" if reversed_flag else "正位置",
        "meaning": meaning,
    }


# -----------------------------
# 大アルカナ or 小アルカナを混ぜて引く関数
# ※今の main / Web では未使用
# -----------------------------
def draw_tarot_mixed(major_cards: list[dict], minor_struct: dict) -> dict:
    # 小アルカナ70%、大アルカナ30%
    if random.random() < 0.7:
        return draw_minor(minor_struct)

    card = random.choice(major_cards)
    reversed_flag = random.random() < 0.5

    return {
        "type": "major",
        "name": card["name"],
        "position": "逆位置" if reversed_flag else "正位置",
        "meaning": card["reversed"] if reversed_flag else card["upright"],
    }


# -----------------------------
# 大アルカナ画像ファイル名を返す
# -----------------------------
def get_major_image_filename(card_name: str, image_map: dict):
    # カード名に対応する画像ファイル名を返す
    return image_map.get(card_name)


# -----------------------------
# 今日のヒント生成
# -----------------------------
def build_today_hint(z: dict, yz: dict, t: dict, hint_rules: dict) -> str:
    # 五行ごとのおすすめ行動
    element_actions = hint_rules["element_actions"]

    # 星座テーマに応じた行動スタイル
    theme_styles = hint_rules["theme_styles"]

    
    # 星座データの theme に対応するスタイルを取得
    style = theme_styles.get(z.get("theme", ""), "自分のペースで進める")

    # タロットの意味文と正逆位置
    meaning = t.get("meaning", "")
    position = t.get("position", "正位置")

    # 正位置 / 逆位置で全体トーンを変える
    if position == "逆位置":
        tone = "深呼吸。整う事に集中してみて"
        caution = True
    else:
        tone = "追い風だよ。直感を信じて行こう"
        caution = False

    # 意味文に含まれる言葉からアクションを決めるルール表
    key_rules = [
        (["整理", "判断", "正義", "決断", "選択", "切る"], "決める"),
        (["調整", "節制", "バランス", "中庸", "整える", "回復"], "整える"),
        (["前進", "戦車", "突破", "加速", "挑戦", "行動"], "動く"),
        (["希望", "星", "未来", "癒し", "安心"], "信じる"),
        (["不安", "月", "迷い", "混乱", "疑い"], "落ち着く"),
        (["刷新", "死神", "終わり", "リセット", "解放", "距離"], "手放す"),
        (["成功", "太陽", "祝福", "達成", "実り"], "広げる"),
        (["審判", "後悔", "決めきれない", "迷い"], "見直す"),

        # 小アルカナ寄りの言葉
        (["遅れ", "停滞", "中途半端"], "ペース調整する"),
        (["依存", "執着", "甘え"], "自立する"),
        (["燃え尽き", "疲労", "消耗"], "休む"),
        (["空回り", "焦り", "暴走"], "落ち着く"),
        (["感情的", "過干渉"], "距離を取る"),
    ]

    # まずアクションは未決定にしておく
    key_action = None

    # 逆位置で、しんどいワードが含まれるときは最優先で「落ち着く」
    if position == "逆位置":
        if any(w in meaning for w in ["混乱", "感情的", "疲れ", "消耗", "過干渉", "不安"]):
            key_action = "落ち着く"

    # まだ決まっていなければルール表から探す
    if key_action is None:
        for words, action in key_rules:
            if any(w in meaning for w in words):
                key_action = action
                break

    # 最後まで決まらなければデフォルト
    if key_action is None:
        key_action = "整える" if position == "逆位置" else "進める"

    # 五行から行動を決める
    elem = yz.get("elem", "土")

    # 逆位置は守り寄りの行動だけにする
    if position == "逆位置":
        safe_actions = ["休む", "整える", "ペース調整する", "距離を取る"]
        elem_action = random.choice(safe_actions)
    else:
        elem_action = random.choice(element_actions.get(elem, ["整える"]))

    # 最終メッセージを返す
    if caution:
        return f"{tone}。『{style}』をベースに、まず{elem_action}→{key_action}の順でいってみよう☆"
    else:
        return f"{tone}。『{style}』をベースに、{elem_action}てから{key_action}と運が乗ってくよ〜♪"


# -----------------------------
# CUI版メイン処理
# -----------------------------
def main():
    print("Fortune Palette（CUI版）")
    print("生年月日から太陽星座＋タロット＋（簡易）四柱推命で今日のヒントを出します。\n")

    # JSONデータをまとめて読み込む
    zodiac, major, minor_struct, element_msgs, _, hint_rules = load_fortune_data()

    # コマンドライン引数があればそれを使う
    # 例: python main.py 1994-12-14
    if len(sys.argv) >= 2:
        birth_text = sys.argv[1]
    else:
        # なければキーボード入力
        birth_text = input("生年月日を入力してください（YYYY-MM-DD）：")

    # 入力チェック
    try:
        bd = parse_birthdate(birth_text)
    except ValueError as e:
        print(f"\n入力エラー：{e}")
        return

    # 星座を求める
    zkey = get_zodiac_key(bd.month, bd.day)
    z = zodiac[zkey]

    # 四柱推命（簡易：年柱）
    adjusted_year = get_adjusted_year(birth_text)
    yz = get_year_ganzhi(adjusted_year)
    elem_info = element_msgs.get(yz["elem"])

    # 大アルカナを1枚引く
    major_card = random.choice(major)
    rev_major = random.random() < 0.5

    t_major = {
        "type": "major",
        "name": major_card["name"],
        "position": "逆位置" if rev_major else "正位置",
        "meaning": major_card["reversed"] if rev_major else major_card["upright"],
    }

    # 小アルカナを1枚引く
    t_minor = draw_minor(minor_struct)

    lucky_color = get_lucky_color_v2(zkey, t_major)

    # 今日のヒントを作る（今は大アルカナベース）
    today_hint = build_today_hint(z, yz, t_major, hint_rules)

    # 表示
    print("\n========== 結果 ==========")
    print(f"生年月日：{bd.isoformat()}")
    print(f"太陽星座：{z['jp']}")
    print(f"今日のテーマ：{z['theme']}")
    print(f"ラッキーカラー：{z['color']}")
    print(f"ひとこと：{z['message']}")
    print("--------------------------")
    print(f"四柱推命（簡易）年柱：{yz['ganzhi']}（{yz['animal']}）")
    print(f"十干：{yz['stem']}／五行：{yz['elem']}／陰陽：{yz['yin_yang']}")
    if elem_info:
        print(f"{elem_info['title']}：{elem_info['message']}")
    print("--------------------------")
    print(f"大アルカナ：{t_major['name']}（{t_major['position']}）")
    print(f"小アルカナ：{t_minor['name']}（{t_minor['position']}）")
    print(f"大アルカナメッセージ：{t_major['meaning']}")
    print(f"小アルカナメッセージ：{t_minor['meaning']}")
    print("--------------------------")
    print(f"今日のヒント：{today_hint}")
    print("==========================\n")


# -----------------------------
# Web版用：結果を辞書で返す
# -----------------------------
def fortune_from_birthdate(birth_text: str) -> dict:
    """生年月日文字列から占い結果を dict で返す（Web用）"""

    # 入力文字列を日付に変換
    bd = parse_birthdate(birth_text)

    # JSONデータをまとめて読み込む
    zodiac, major, minor_struct, element_msgs, major_images, hint_rules = load_fortune_data()

    # 星座を求める
    zkey = get_zodiac_key(bd.month, bd.day)
    z = zodiac[zkey]

    # 四柱推命（簡易）
    adjusted_year = get_adjusted_year(birth_text)
    yz = get_year_ganzhi(adjusted_year)
    elem_info = element_msgs.get(yz["elem"])

    # 大アルカナを1枚引く
    major_card = random.choice(major)
    rev_major = random.random() < 0.5

    t_major = {
        "type": "major",
        "name": major_card["name"],
        "position": "逆位置" if rev_major else "正位置",
        "meaning": major_card["reversed"] if rev_major else major_card["upright"],
    }

    # 小アルカナを1枚引く
    t_minor = draw_minor(minor_struct)

    lucky_color = get_lucky_color_v2(zkey, t_major)
    lucky_color["balance"] = convert_colors(lucky_color["balance"])
    lucky_color["boost"] = convert_colors(lucky_color["boost"])

    if not lucky_color["balance"]:
        lucky_color["balance"] = [{"name": "グレー", "code": "#ccc"}]

    if not lucky_color["boost"]:
        lucky_color["boost"] = [{"name": "グレー", "code": "#ccc"}]

    # ヒント生成（大アルカナベース）
    today_hint = build_today_hint(z, yz, t_major, hint_rules)

    # 星座のラッキーカラー
    zodiac_color_code = COLOR_MAP.get(z["color"], "#ccc")
    
    # HTML側で使いやすいように必要情報をまとめて返す
    return {
        "birthdate": bd.isoformat(),                                # 生年月日
        "zodiac": z,                                                # 星座データ一式
        "shichusuimei": yz,                                         # 年柱データ
        "element_info": elem_info,                                  # 五行メッセージ
        "today_hint": today_hint,                                   # 今日のヒント
        "tarot_major": t_major,                                     # 大アルカナ
        "tarot_minor": t_minor,                                     # 小アルカナ
        "major_image": get_major_image_filename(t_major["name"], major_images),   # 大アルカナ画像名
        "is_reversed": t_major["position"] == "逆位置",              # 逆位置かどうか
        "zodiac_color_code": zodiac_color_code,
        "lucky_color": lucky_color
    }


# -----------------------------
# このファイルを直接実行したときだけ main() を動かす
# -----------------------------
if __name__ == "__main__":
    main()