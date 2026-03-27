# -*- coding: utf-8 -*-
import json, random, sys
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
ZODIAC_PATH = DATA_DIR / "zodiac.json"
TAROT_PATH = DATA_DIR / "tarot.json"                  # 大アルカナ（個別）
MINOR_PATH = DATA_DIR / "minor_structure.json"        # 小アルカナ（構造）
ELEMENT_MSG_PATH = DATA_DIR / "element_messages.json" # 五行メッセージ（任意）


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_birthdate(text: str) -> date:
    text = (text or "").strip()
    if not text:
        raise ValueError("未入力です。YYYY-MM-DD 形式で入力してください。")

    try:
        dt = datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("形式が違います。YYYY-MM-DD 形式で入力してください。")

    if dt > date.today():
        raise ValueError("未来日は入力できません。")

    return dt


def get_zodiac_key(month: int, day: int) -> str:
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


# -----------------------------
# 四柱推命（簡易）：年柱（干支）
# -----------------------------
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


def get_year_ganzhi(year: int) -> dict:
    """
    1984年=甲子 を基準に年干支を求める（簡易・一般的な方式）。
    ※厳密な四柱推命は立春基準などがあるが、個人制作では西暦年基準でOK。
    """
    base = 1984  # 甲子
    diff = year - base
    stem = TENKAN[diff % 10]
    branch = JUNISHI[diff % 12]
    return {
        "stem": stem["jp"],
        "branch": branch["jp"],
        "ganzhi": stem["jp"] + branch["jp"],
        "elem": stem["elem"],
        "yin_yang": stem["yin_yang"],
        "animal": branch["animal"],
    }


# -----------------------------
# タロット：小アルカナ（構造） + 大アルカナ（個別）
# -----------------------------
def draw_minor(minor_struct: dict) -> dict:
    suits = list(minor_struct["suits"].keys())
    ranks = list(minor_struct["ranks"].keys())

    suit_key = random.choice(suits)
    rank_key = random.choice(ranks)

    reversed_flag = random.random() < 0.5

    suit = minor_struct["suits"][suit_key]
    rank = minor_struct["ranks"][rank_key]

    rank_meaning = rank["reversed"] if reversed_flag else rank["upright"]
    suit_keywords = suit["keywords_reversed"] if reversed_flag else suit["keywords_upright"]

    meaning = f"{suit['theme']}｜{rank_meaning}（キーワード：{random.choice(suit_keywords)}）"

    return {
        "type": "minor",
        "name": f"{suit['jp']}の{rank['jp']}",
        "position": "逆位置" if reversed_flag else "正位置",
        "meaning": meaning,
    }


def draw_tarot_mixed(major_cards: list[dict], minor_struct: dict) -> dict:
    # 小アルカナが多いので、小70%：大30%（好みで調整OK）
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
# タロット画像ファイル名取得
# -----------------------------
def get_major_image_filename(card_name: str):
    image_map = {
        "愚者": "fool.png",
        "魔術師": "magician.png",
        "女教皇": "high_priestess.png",
        "女帝": "empress.png",
        "皇帝": "emperor.png",
        "法王": "hierophant.png",
        "恋人": "lovers.png",
        "戦車": "chariot.png",
        "力": "strength.png",
        "隠者": "hermit.png",
        "運命の輪": "wheel_of_fortune.png",
        "正義": "justice.png",
        "吊るされた男": "hanged_man.png",
        "死神": "death.png",
        "節制": "temperance.png",
        "悪魔": "devil.png",
        "塔": "tower.png",
        "星": "star.png",
        "月": "moon.png",
        "太陽": "sun.png",
        "審判": "judgement.png",
        "世界": "world.png"
    }
    return image_map.get(card_name)

# -----------------------------
# 合成ヒント生成（ルールベース）
# -----------------------------
def build_today_hint(z: dict, yz: dict, t: dict) -> str:
    element_actions = {
        "木": ["新しい事にも挑戦し", "ストレッチし", "まず学んでみ"],
        "火": ["表現し", "一歩前に踏み出し", "気持ちを盛り上げ"],
        "土": ["整え", "段取りを大切にし", "まず基礎固め"],
        "金": ["余計な荷物を下ろし", "決断を大切にし", "まずルール化し"],
        "水": ["まず一休みし", "情報や必要なことを集め", "流れに乗る事を心がけ"],
    }

    theme_styles = {
        "はじまり": "まず着手する",
        "安定": "丁寧に積み上げる",
        "情報": "軽く試してみる",
        "安心": "守りを整える",
        "主役": "堂々と選ぶ",
        "整理": "無駄を減らす",
        "調和": "バランスを取る",
        "深掘り": "本質を見に行く",
        "冒険": "新しい方へ動く",
        "結果": "淡々と進め切る",
        "ひらめき": "アイデアを形にする",
        "癒し": "感覚を満たす",
    }
    style = theme_styles.get(z.get("theme", ""), "自分のペースで進める")

    meaning = t.get("meaning", "")
    position = t.get("position", "正位置")

    # トーン（正逆で変える）
    if position == "逆位置":
        tone = "深呼吸。整う事に集中してみて"
        caution = True
    else:
        tone = "追い風だよ。直感を信じて行こう"
        caution = False

    # まずルール表（先に定義！）
    key_rules = [
        (["整理", "判断", "正義", "決断", "選択", "切る"], "決める"),
        (["調整", "節制", "バランス", "中庸", "整える", "回復"], "整える"),
        (["前進", "戦車", "突破", "加速", "挑戦", "行動"], "動く"),
        (["希望", "星", "未来", "癒し", "安心"], "信じる"),
        (["不安", "月", "迷い", "混乱", "疑い"], "落ち着く"),
        (["刷新", "死神", "終わり", "リセット", "解放", "距離"], "手放す"),
        (["成功", "太陽", "祝福", "達成", "実り"], "広げる"),
        (["審判", "後悔", "決めきれない", "迷い"], "見直す"),

        # 小アルカナ寄り
        (["遅れ", "停滞", "中途半端"], "ペース調整する"),
        (["依存", "執着", "甘え"], "自立する"),
        (["燃え尽き", "疲労", "消耗"], "休む"),
        (["空回り", "焦り", "暴走"], "落ち着く"),
        (["感情的", "過干渉"], "距離を取る"),
    ]

    # 逆位置×負荷ワードは最優先
    key_action = None
    if position == "逆位置":
        if any(w in meaning for w in ["混乱", "感情的", "疲れ", "消耗", "過干渉", "不安"]):
            key_action = "落ち着く"

    # まだ決まってなければルールで探す
    if key_action is None:
        for words, action in key_rules:
            if any(w in meaning for w in words):
                key_action = action
                break

    # それでも無ければデフォルト
    if key_action is None:
        key_action = "整える" if position == "逆位置" else "進める"

    # 五行アクション（逆位置は守り寄せ）
    elem = yz.get("elem", "土")
    if position == "逆位置":
        safe_actions = ["休む", "整える", "ペース調整する", "距離を取る"]
        elem_action = random.choice(safe_actions)
    else:
        elem_action = random.choice(element_actions.get(elem, ["整える"]))

    # 文章生成
    if caution:
        return f"{tone}。『{style}』をベースに、まず{elem_action}→{key_action}の順でいってみよう☆"
    else:
        return f"{tone}。『{style}』をベースに、{elem_action}てから{key_action}と運が乗ってくよ〜♪"

def main():
    print("Fortune Palette（CUI版）")
    print("生年月日から太陽星座＋タロット＋（簡易）四柱推命で今日のヒントを出します。\n")

    zodiac = load_json(ZODIAC_PATH)
    major = load_json(TAROT_PATH)
    minor_struct = load_json(MINOR_PATH)

    element_msgs = {}
    if ELEMENT_MSG_PATH.exists():
        element_msgs = load_json(ELEMENT_MSG_PATH)

    # 引数でもOK：python main.py 1994-12-14
    if len(sys.argv) >= 2:
        birth_text = sys.argv[1]
    else:
        birth_text = input("生年月日を入力してください（YYYY-MM-DD）：")

    try:
        bd = parse_birthdate(birth_text)
    except ValueError as e:
        print(f"\n入力エラー：{e}")
        return

    # 太陽星座
    zkey = get_zodiac_key(bd.month, bd.day)
    z = zodiac[zkey]

    # 四柱推命（簡易：年柱）
    yz = get_year_ganzhi(bd.year)
    elem_info = element_msgs.get(yz["elem"])

    # 🌙 大アルカナ
    major_card = random.choice(major)
    rev_major = random.random() < 0.5

    t_major = {
        "type": "major",
        "name": major_card["name"],
        "position": "逆位置" if rev_major else "正位置",
        "meaning": major_card["reversed"] if rev_major else major_card["upright"],
    }

    # 🔮 小アルカナ
    t_minor = draw_minor(minor_struct)


    # 合成ヒント
    today_hint = build_today_hint(z, yz, t_major)

    # 出力
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

def fortune_from_birthdate(birth_text: str) -> dict:
    """生年月日文字列から占い結果をdictで返す（Web用）"""
    bd = parse_birthdate(birth_text)

    zodiac = load_json(ZODIAC_PATH)
    major = load_json(TAROT_PATH)
    minor_struct = load_json(MINOR_PATH)

    element_msgs = {}
    if ELEMENT_MSG_PATH.exists():
        element_msgs = load_json(ELEMENT_MSG_PATH)

    zkey = get_zodiac_key(bd.month, bd.day)
    z = zodiac[zkey]

    yz = get_year_ganzhi(bd.year)
    elem_info = element_msgs.get(yz["elem"])

    # 🌙 大アルカナ
    major_card = random.choice(major)
    rev_major = random.random() < 0.5

    t_major = {
        "type": "major",
        "name": major_card["name"],
        "position": "逆位置" if rev_major else "正位置",
        "meaning": major_card["reversed"] if rev_major else major_card["upright"],
    }

    # 🔮 小アルカナ
    t_minor = draw_minor(minor_struct)
    
    # ヒント（大アルカナベース）
    today_hint = build_today_hint(z, yz, t_major)

    return {
    "birthdate": bd.isoformat(),
    "zodiac": z,
    "shichusuimei": yz,
    "element_info": elem_info,
    "today_hint": today_hint,
    "tarot_major": t_major,
    "tarot_minor": t_minor,
    "major_image": get_major_image_filename(t_major["name"]),
    "is_reversed": t_major["position"] == "逆位置"
    }

if __name__ == "__main__":
    main()