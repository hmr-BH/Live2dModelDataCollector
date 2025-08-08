import base64

# 替换为你的 PNG 图片文件路径
file_path = "../img/icon.png"

with open(file_path, "rb") as image_file:
    base64_encoded = base64.b64encode(image_file.read()).decode("utf-8")

print(base64_encoded)