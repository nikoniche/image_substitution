import tkinter as tk
from core import substitution
from PIL import Image, ImageTk
from tkinter import filedialog

WIDTH, HEIGHT = 1200, 650
FRAME_SIZE = 380
BG_COLOR = "#303030"
FONT = "Consolas"


def _bind_hover(widget):
    def darken(event: tk.Event) -> None:
        event.widget.config(bg="darkgray")

    def revert(event: tk.Event) -> None:
        event.widget.config(bg="gray")

    widget.bind("<Enter>", darken)
    widget.bind("<Leave>", revert)


class UI(tk.Tk):

    def __init__(self):
        super().__init__()

        self.template_path = None
        self.substitute_path = None
        self.current_result = None

        self.image_references = []

        self.title("Image Substitution")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.config(bg=BG_COLOR)

        # centering widgets in row
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # generating title labels
        self._generate_label(0, "Template image")
        self._generate_label(1, "Result")
        self._generate_label(2, "Substitute image")

        # generating image placeholders
        self.template_placeholder = self._generate_image_placeholder(0)
        self.result_placeholder = self._generate_image_placeholder(1)
        self.substitute_placeholder = self._generate_image_placeholder(2)

        # generate browse buttons
        self._generate_button("Open template", 0, 2, self._save_browsed_path, 0)
        self._generate_button("Open substitute", 2, 2, self._save_browsed_path, 1)

        self.check_var = tk.BooleanVar()
        self.check_var.trace("w", self._merge)
        check_button = tk.Checkbutton(self, text="Use dominant color", variable=self.check_var, font=(FONT, 14),
                                      bg="gray", height=1, relief="ridge")
        check_button.grid(column=1, row=2, pady=(4, 0))
        _bind_hover(check_button)

        # generate _show button
        self._generate_button("Show", 1, 3, self._show)

        # generate save as button
        self._generate_button("Save as", 1, 4, self._save_result)

        self.mainloop()

    def _display_image(self, path: str, placeholder: tk.Label, image=None) -> None:
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

        image = image.resize(new_dimensions)

        # applies the changes
        photo_image = ImageTk.PhotoImage(image)
        placeholder.config(image=photo_image)

        # saves the photo image reference
        self.image_references.append(photo_image)

    def _generate_image_placeholder(self, column: int) -> tk.Label:
        """Generates a placeholder and with it its parent frame."""

        frame = tk.Frame(self, borderwidth=3, bg="black", relief="ridge",
                         width=FRAME_SIZE, height=FRAME_SIZE)
        frame.grid(column=column, row=1)
        frame.grid_propagate(False)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        placeholder = tk.Label(frame, bg="gray")
        placeholder.grid(sticky="nsew")
        self._display_image("neutral_image.jpg", placeholder)
        return placeholder

    def _generate_label(self, column: int, text: str) -> None:
        """Generates a title label."""

        label = tk.Label(self, text=text, font=(FONT, 19), bg=BG_COLOR, fg="white")
        label.grid(column=column, row=0, pady=(40, 10))

    def _save_browsed_path(self, index: int) -> None:
        """Asks the user for a path to a directory and saves it to a set variable depending on the index argument."""

        filepath = filedialog.askopenfilename()

        # selecting the correct variable based on index
        # index 0 == template, 1 == substitute
        placeholder = self.template_placeholder if index == 0 else self.substitute_placeholder
        if index == 0:
            self.template_path = filepath
        else:
            self.substitute_path = filepath

        self._display_image(filepath, placeholder)

        # automatically calls _merge
        self.after(1, self._merge)

    def _generate_button(self, text: str, column: int, row: int, func, *args) -> None:
        """Generates a button."""

        button = tk.Button(self, text=text, relief="ridge", bg="gray", width=20, height=1,
                           font=(FONT, 15),
                           command=lambda: func(*args))
        button.grid(column=column, row=row, pady=(10, 0))

        _bind_hover(button)

    def _merge(self, *_):
        """Merges the template with the substitute and sets it as the current result."""

        if self.template_path is not None and self.substitute_path is not None:
            self.current_result = substitution(self.template_path, self.substitute_path,
                                               use_dominant_color=self.check_var.get())
            self._display_image(None, self.result_placeholder, self.current_result)

    def _show(self):
        """Shows the current result in a separate window."""

        if self.current_result is not None:
            self.current_result.show()

    def _save_result(self):
        """Asks the user for a save location and saves the result."""

        dialog = filedialog.asksaveasfile(mode="w", defaultextension=".png", filetypes=[("PNG files", ".png")])
        if dialog is not None:
            save_path = dialog.name

            if self.current_result is not None:
                try:
                    self.current_result.save(save_path)
                except OSError:
                    jpg_path = save_path.replace(".png", ".jpg")
                    self.current_result.save(jpg_path)
