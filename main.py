import time

from core import substitution
from PIL import Image

template_path = input("Template path: ")
Image.open(template_path).show()

substitute_path = input("Substitute path: ")
Image.open(substitute_path).show()

print("Generating..")
result = substitution(template_path, substitute_path)

try:
    result.save("result.jpg")
except OSError:
    result.save("result.png")

result.show()
