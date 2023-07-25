from core import substitution

# template_path = input("Template path: ")
# substitute_path = input("Substitute path: ")

template_path = "meme3.jpg"
substitute_path = "buff_tree.jpg"

result = substitution(template_path, substitute_path)

try:
    result.save("result.jpg")
except OSError:
    result.save("result.png")

result.show()
