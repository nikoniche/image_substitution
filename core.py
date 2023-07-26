from PIL import Image
import numpy as np
import scipy
import scipy.misc
import scipy.cluster

DOMINANT_CLUSTERS_AMOUNT = 3


def _find_dominant_color(img: Image, resize=None):
    """Finds the color that covers most of the image."""

    # the option to resize the image
    img = img.resize(resize) if resize is not None else img

    ar = np.asarray(img)
    shape = ar.shape
    ar = ar.reshape(np.product(shape[:2]), shape[2]).astype(float)

    codes, dist = scipy.cluster.vq.kmeans(ar, DOMINANT_CLUSTERS_AMOUNT)

    vecs, dist = scipy.cluster.vq.vq(ar, codes)  # assign codes
    counts, bins = np.histogram(vecs, len(codes))  # count occurrences

    index_max = np.argmax(counts)  # find most frequent
    peak = codes[index_max]

    return tuple(peak)


def _are_colors_similar(color1: tuple, color2: tuple, tolerance: int):
    """Compares if two colors are similar enough."""

    color1_sum = color1[0] + color1[1] + color1[2]
    color2_sum = color2[0] + color2[1] + color2[2]
    difference = abs(color2_sum - color1_sum)
    if difference < tolerance:
        return True
    else:
        return False


def _find_placement(template: Image, dominant_color: tuple):
    """Finds the ideal area for a substitute image to be pasted to."""

    template_width, template_height = template.size
    template_pixel_grid = template.load()

    substitute_width, substitute_height = 0, 0
    starting_position = None
    current_matching_lines_streak = 0

    # runs through every line of pixels in the image to find which lines are mostly not made up of the dominant color
    for y in range(template_height):
        tolerance = template_width // 2
        line_start = None
        last_different = None
        passed = True

        # running through one line
        for x in range(template_width):
            try:
                color = template_pixel_grid[x, y]
            except IndexError:
                raise f"Error with extracting pixel colors pos {x}/{y}"
            else:
                if _are_colors_similar(color, dominant_color, 30):
                    tolerance -= 1
                    if tolerance == 0:
                        passed = False
                        break

                    if line_start is not None and last_different is not None:
                        current_line_length = last_different[0] - line_start[0]
                        if current_line_length > substitute_width:
                            substitute_width = current_line_length

                else:
                    last_different = x, y
                    if line_start is None:
                        line_start = x, y

            if line_start is not None and last_different is not None:
                current_line_length = last_different[0] - line_start[0]
                if current_line_length > substitute_width:
                    substitute_width = current_line_length

        if passed and y != template_height - 1:
            current_matching_lines_streak += 1
        else:
            if substitute_height < current_matching_lines_streak and line_start is not None:
                substitute_height = current_matching_lines_streak
                starting_position = line_start[0], line_start[1] - substitute_height
            current_matching_lines_streak = 0

    return starting_position, (substitute_width, substitute_height)


def substitution(template_path: str, substitute_path: str, use_dominant_color=False) -> Image:
    """
    Will return an image that merged the substitute into the template image.

    template_path: Path to the image you want a part replaced.
    substitute_path: Path to the image that will be pasted into the template.
    use_dominant_color: If True, will use dominant color to find the placement area.
    """

    try:
        template = Image.open(template_path)
        substitute = Image.open(substitute_path)
    except AttributeError:
        pass

    # find the dominant color of the template if required, otherwise use default white (255, 255, 255)
    dominant_color = (255, 255, 255) if not use_dominant_color else _find_dominant_color(template)

    # find the placement position and size for the substitute image within the template
    placement_position, new_size = _find_placement(template, dominant_color)

    # resize substitute image to fit the selected area
    resized_substitute = substitute.resize(new_size)

    # replace the selected area in the template with the substitute image
    template.paste(resized_substitute, placement_position)

    return template
