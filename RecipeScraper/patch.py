import json
import re


def load_js_array(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(
        r"const\s+\w+\s*=\s*(\[.*\])\s*;",
        content,
        re.DOTALL
    )

    if not match:
        raise Exception("找不到陣列資料")

    return json.loads(match.group(1))


def save_js_array(file_path, data):
    content = (
        "const equipments = "
        + json.dumps(data, ensure_ascii=False, indent=2)
        + ";\n"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def hack(file, **kwargs):
    data = load_js_array(file)

    patch_fields = {
        "materials",
        "note",
        "level",
        "id"
    }

    condition = {}
    patch = {}

    for key, value in kwargs.items():
        if key in patch_fields:
            patch[key] = value
        else:
            condition[key] = value

    found = False

    for item in data:
        if all(item.get(k) == v for k, v in condition.items()):
            item.update(patch)
            found = True
            print(f"已修改: {item['name']}")

    if found:
        save_js_array(file, data)
    else:
        print("找不到符合條件的資料")
        
        
        
if __name__ == "__main__":
    hack(
        file="data/data_pet_light.js",
        name="時尚圍巾",
        materials={
            "絲線": 10,
            "阿巴尼斯棉線": 10,
            "白金條": 10,
            "杉": 10
        }
    )
    hack(
        file="data/data_pet_accessory.js",
        name="幻想鈴鐺",
        materials={
            "開米士棉線": 15,
            "絲柏": 15,
            "梣": 15,
            "七葉樹": 20
        }
    )
    hack(
        file="data/data_pet_heavy.js",
        name="翡翠手甲",
        materials={
            "勒格耐席鉧條": 15,
            "傑諾瓦毛線": 20,
            "芎麻布": 10,
            "朴": 5,
            "風龍蜥的甲殼": 1
        },
    )
    hack(
        file="data/data_pet_collar.js",
        name="銅頸圈",
        materials={
            "銅條": 10,
            "銀條": 20,
            "薄棉布": 20,
            "樅": 10,
        },
    )
    hack(
        file="data/data_pet_collar.js",
        name="自然項圈",
        materials={
            "白金條": 20,
            "幻之鋼條": 10,
            "傑諾瓦毛線": 20,
            "杉": 10,
            "永久冰石": 3
        },
    )
    hack(
        file="data/data_shoes.js",
        name="水龍之鞋",
        materials={
            "破損的鞋": 1,
            "鋼騎之礦": 2,
            "魔族的水晶": 2,
            "朴": 20
        },
    )
    hack(
        file="data/data_shoes.js",
        name="大木屐",
        materials={
              "鋁條": 20,
              "勒格耐席姆條": 14,
              "單木": 40,
              "梣": 40,
              "風龍蜥的甲殼": 2

        },
    )
