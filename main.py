import tkinter as tk
from core import substitution
from PIL import Image, ImageTk
from tkinter import filedialog

WIDTH, HEIGHT = 1200, 650
FRAME_SIZE = 380
BG_COLOR = "#303030"

template_path = None
substitute_path = None
current_result = None

image_references = []


def display_image(path: str, placeholder: tk.Label, image=None) -> None:
    """Displays an image in a placeholder. Automatically rescales the image to fit the placeholder."""

    # calculates new width for the image, so it fits well into the frame
    scale = FRAME_SIZE - 12

    image = Image.open(path) if image is None else image

    # calculates new dimensions for rescaling the image
    img_width, img_height = image.size
    if img_width > img_height:
        new_dimensions = scale, round(img_height / img_width * scale)
    else:
        new_dimensions = round(img_width / img_height * scale), scale

    neutral_image_temp = image.resize(new_dimensions)

    # applies the changes
    neutral_image = ImageTk.PhotoImage(neutral_image_temp)
    placeholder.config(image=neutral_image)

    # saves the photo image reference
    image_references.append(neutral_image)


def generate_image_placeholder(window: tk.Tk, column: int):
    """Generates a placeholder and with it its parent frame."""

    frame = tk.Frame(window, borderwidth=3, bg="black", relief="ridge",
                     width=FRAME_SIZE, height=FRAME_SIZE)
    frame.grid(column=column, row=1)
    frame.grid_propagate(False)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)
    placeholder = tk.Label(frame, bg="gray")
    placeholder.grid(sticky="nsew")
    display_image("neutral_image.jpg", placeholder)
    return placeholder


def generate_label(window: tk.Tk, column: int, text: str):
    """Generates a title label."""

    label = tk.Label(window, text=text, font=("Consolas", 19), bg=BG_COLOR, fg="white")
    label.grid(column=column, row=0, pady=(40, 10))


def save_browsed_path(index: int, placeholder: tk.Label) -> None:
    """Asks the user for a path to a directory and saves it to a set variable depending on the index argument."""

    filepath = filedialog.askopenfilename()

    # selecting the correct variable based on index
    # index 0 == template, 1 == substitute
    if index == 0:
        global template_path
        template_path = filepath
    else:
        global substitute_path
        substitute_path = filepath

    display_image(filepath, placeholder)

    # automatically calls merge
    merge()


def generate_button(root, text, column, row, func, *args):
    """Generates a button."""

    button = tk.Button(root, text=text, relief="ridge", bg="gray", width=20, height=1,
                       font=("Consolas", 15),
                       command=lambda: func(*args))
    button.grid(column=column, row=row, pady=(10, 0))


def merge():
    """Merges the template with the substitute and sets it as the current result."""

    if template_path is not None and substitute_path is not None:
        global current_result
        current_result = substitution(template_path, substitute_path)
        display_image(None, result_placeholder, current_result)


def show():
    """Shows the current result in a separate window."""

    if current_result is not None:
        current_result.show()


def save_result():
    """Asks the user for a save location and saves the result."""

    dialog = filedialog.asksaveasfile(mode="w", defaultextension=".png", filetypes=[("PNG files", ".png")])
    if dialog is not None:
        save_path = dialog.name

        if current_result is not None:
            try:
                current_result.save(save_path)
            except OSError:
                jpg_path = save_path.replace(".png", ".jpg")
                current_result.save(jpg_path)


# master window
root = tk.Tk()
root.title("Image Substitution")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.config(bg=BG_COLOR)

# centering widgets in row
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

# generating title labels
generate_label(root, 0, "Template image")
generate_label(root, 1, "Result")
generate_label(root, 2, "Substitute image")

# generating image placeholders
template_placeholder = generate_image_placeholder(root, 0)
result_placeholder = generate_image_placeholder(root, 1)
substitute_placeholder = generate_image_placeholder(root, 2)

# generate browse buttons
generate_button(root, "Open template", 0, 2, save_browsed_path, 0, template_placeholder)
generate_button(root, "Open substitute", 2, 2, save_browsed_path, 1, substitute_placeholder)

# generate show button
generate_button(root, "Show", 1, 2, show)

# generate save as button
generate_button(root, "Save as", 1, 3, save_result)

root.mainloop()
