import numpy as np
from collections import Counter

with open("input8") as fr:
    image_data = fr.read().strip()

test_image_data = "123456789012"

def process_image_data(data, rows, cols):
    layers = []
    assert len(data) % (rows*cols) == 0, f"Encountered {len(data)} // {rows*cols}"
    layers_no = len(data) // (rows*cols)
    pointer = 0
    for _ in range(layers_no):
        layer = []
        for _ in range(rows):
            row = [int(digit) for digit in data[pointer:pointer+cols]]
            pointer += cols
            layer.append(row)
        layers.append(layer)

    return layers

test_image = process_image_data(test_image_data, 2, 3)
task_image = process_image_data(image_data, 6, 25)

def count_digits(layer, digits):
        counted = Counter((n for row in layer for n in row))
        if type(digits) == int:
            return counted[digits] or 0
        return tuple(counted[d] or 0 for d in digits)

assert count_digits([[1,2,3], [2,3,4]], 2) == 2
assert count_digits([[1,2,3], [2,3,4]], (2,3)) == (2,2)
assert count_digits([[1,2,3], [2,3,4]], [1,4]) == (1,1)

def part1(image):
    counted = [(*count_digits(layer, (0,1,2)), ind) for ind,layer in enumerate(image)]
    best = min(counted, key=lambda x: x[0])

    return (best, best[1] * best[2])


assert part1(test_image) == ((0,1,1,0), 1)

def compose_pixels(pixels: list):
        pixels.reverse()
        while len(pixels):
            pix = pixels.pop()
            if pix == 2:
                continue
            break
        else:
            return 2
        return pix

assert compose_pixels([2, 1, 2]) == 1
assert compose_pixels([1,0,0]) == 1
assert compose_pixels([2,2,2]) == 2
assert compose_pixels([2,2,0]) == 0

def stack_layers(image):
    layers_no = len(image)
    rows = len(image[0])
    cols = len(image[0][0])
    tensor = np.array(image)

    new_img = [[0 for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            pixels = list(tensor[0:layers_no, i, j])
            pix = compose_pixels(pixels)
            new_img[i][j] = pix

    return new_img

def part2(image):
    LRFKU = stack_layers(image)
    print(LRFKU)