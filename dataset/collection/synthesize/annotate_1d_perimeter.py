from PIL import Image, ImageDraw
import random
import math
import json
import os
import argparse

# 定义一些颜色
colors = ["red", "green", "blue", "yellow", "purple", "orange"]

# 图片尺寸
max_retries = 50  # 增加重试次数

# 几何图形类别
shapes = ["circle", "triangle", "rectangle"]

def append_jsonl(file_path, data):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

# 生成随机位置
def random_position(width, height):
    return (random.randint(0, width), random.randint(0, height))

# 生成随机颜色
def random_color(used_colors):
    available_colors = [color for color in colors if color not in used_colors]
    return random.choice(available_colors) if available_colors else None

# 生成随机大小
def random_size():
    return random.randint(50, 400)

# 生成随机角度
def random_angle():
    return random.randint(1, 360)

def random_angle_30_to_150():
    return random.randint(30, 150)

def random_angle_90_to_180():
    return random.randint(90, 180)

# 将相对距离转换成<=========>
def visualize(number):
    total_equals = int(number * 10)
    
    groups = []
    for i in range(0, total_equals, 10):
        group = '=' * min(10, total_equals - i)
        groups.append(f'<{group}>')
    
    result = ''.join(groups)
    return result

# 检查两个矩形是否重叠
def rectangles_overlap(rect1, rect2):
    x1, y1, x2, y2 = rect1
    x3, y3, x4, y4 = rect2
    return not (x2 < x3 or x1 > x4 or y2 < y3 or y1 > y4)

# 获取图形的边界框并检查是否超出图片边界
def get_bounding_box(points, width, height):
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    bounding_box = (min(x_coords), min(y_coords), max(x_coords), max(y_coords))

    # 检查边界框是否超出图片边界
    x1, y1, x2, y2 = bounding_box
    if x1 <= 0 or y1 <= 0 or x2 >= width or y2 >= height:
        return None  # 超出边界
    return bounding_box

# 绘制圆形
def draw_circle(draw, used_colors, existing_boxes, width, height):
    attempt = 0
    while True:
        attempt += 1
        if attempt > max_retries:
            return None
        x, y = random_position(width, height)
        size = random_size()
        color = random_color(used_colors)
        if not color:
            return None
        bounding_box = (x, y, x + 2 * size, y + 2 * size)
        if not get_bounding_box([(x, y), (x + 2 * size, y + 2 * size)], width, height):
            continue  # 超出边界，重新生成
        overlap = any(rectangles_overlap(bounding_box, box) for box in existing_boxes)
        if not overlap:
            used_colors.add(color)
            draw.ellipse(bounding_box, fill=color, outline="black")
            perimeter = 2*math.pi*size

            shape_info = {
                "name": f"the {color} circle",
                "dimension_info": [{
                    "name": f"the radius of the {color} circle",
                    "absolute_length": size
                }],
                "perimeter_info": {
                    "name": f"the perimeter of the {color} circle",
                    "absolute_length": perimeter
                }
            }
            existing_boxes.append(bounding_box)
            return shape_info

# 绘制三角形
def draw_triangle(draw, used_colors, existing_boxes, width, height):
    attempt = 0
    while True:
        attempt += 1
        if attempt > max_retries:
            return None
        x, y = random_position(width, height)
        size = random_size()
        color = random_color(used_colors)
        if not color:
            return None
        angle = random_angle()
        angle1 = random_angle_90_to_180()
        angle2 = random_angle_90_to_180()
        points = [
            (x + size * math.cos(math.radians(angle)), y + size * math.sin(math.radians(angle))),
            (x + size * math.cos(math.radians(angle + angle1)), y + size * math.sin(math.radians(angle + angle1))),
            (x + size * math.cos(math.radians(angle + angle1 + angle2)), y + size * math.sin(math.radians(angle + angle1 + angle2))),
        ]
        bounding_box = get_bounding_box(points, width, height)
        if not bounding_box:
            continue  # 超出边界，重新生成
        overlap = any(rectangles_overlap(bounding_box, box) for box in existing_boxes)
        if not overlap:
            used_colors.add(color)
            (x1, y1), (x2, y2), (x3, y3) = points
    
            # 计算每条边的长度
            edge1 = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            edge2 = math.sqrt((x3 - x2)**2 + (y3 - y2)**2)
            edge3 = math.sqrt((x1 - x3)**2 + (y1 - y3)**2)

            edge_short, edge_medium, edge_long = sorted([edge1, edge2, edge3])

            draw.polygon(points, fill=color, outline="black")

            perimeter = edge1 + edge2 + edge3
            shape_info = {
                "name": f"the {color} triangle",
                "dimension_info": [
                    {
                        "name": f"the shortest side of the {color} triangle",
                        "absolute_length": edge_short
                    },
                    {
                        "name": f"the medium side of the {color} triangle",
                        "absolute_length": edge_medium
                    },
                    {
                        "name": f"the longest side of the {color} triangle",
                        "absolute_length": edge_long
                    }
                ],
                "perimeter_info": {
                    "name": f"the perimeter of the {color} triangle",
                    "absolute_length": perimeter
                }
            }

            existing_boxes.append(bounding_box)
            return shape_info

# 绘制长方形
def draw_rectangle(draw, used_colors, existing_boxes, width, height):
    attempt = 0
    while True:
        attempt += 1
        if attempt > max_retries:
            return None
        x, y = random_position(width, height)
        size = random_size()
        color = random_color(used_colors)
        if not color:
            return None
        angle = random_angle()
        angle1 = random_angle_30_to_150()

        points = [
            (x + size * math.cos(math.radians(angle)), y + size * math.sin(math.radians(angle))),
            (x + size * math.cos(math.radians(angle + angle1)), y + size * math.sin(math.radians(angle + angle1))),
            (x + size * math.cos(math.radians(angle + 180)), y + size * math.sin(math.radians(angle + 180))),
            (x + size * math.cos(math.radians(angle + 180 + angle1)), y + size * math.sin(math.radians(angle + 180 + angle1))),
        ]

        # 获取边界框
        bounding_box = get_bounding_box(points, width, height)
        if not bounding_box:
            continue  # 超出边界，重新生成
        # 检查是否与已有图形重叠
        overlap = any(rectangles_overlap(bounding_box, box) for box in existing_boxes)
        if not overlap:
            used_colors.add(color)
            draw.polygon(points, fill=color, outline="black")

            (x1, y1), (x2, y2), (x3, y3), (x4, y4) = points

            # 计算每条边的长度
            edge1 = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            edge2 = math.sqrt((x3 - x2)**2 + (y3 - y2)**2)
            edge3 = math.sqrt((x4 - x3)**2 + (y4 - y3)**2)
            edge4 = math.sqrt((x1 - x4)**2 + (y1 - y4)**2)

            edge_short1, edge_short2, edge_long1, edge_long2  = sorted([edge1, edge2, edge3, edge4])
            perimeter = edge_short1 * 2 + edge_long1 * 2

            shape_info = {
                "name": f"the {color} rectangle",
                "dimension_info": [
                    {
                        "name": f"the longer side of the {color} rectangle",
                        "absolute_length": edge_long1
                    },
                    {
                        "name": f"the shorter side of the {color} rectangle",
                        "absolute_length": edge_short1
                    }
                ],
                "perimeter_info": {
                    "name": f"the perimeter of the {color} rectangle",
                    "absolute_length": perimeter
                }
            }

            existing_boxes.append(bounding_box)
            return shape_info


# relative_annotation 由于思维链理论上先获取了各条边的相对长度，再计算的周长，所以标注里的周长也需要这样得到
def relative_annotation(shape, reference_length):
    relative_item = {
        "name": shape["name"],
        "dimension_info": [
            {
                "name": item["name"],
                "relative_length": round(item["absolute_length"] / reference_length, 1),
                "symbolization_result": visualize(round(item["absolute_length"] / reference_length, 1))
            }
            for item in shape["dimension_info"]
        ],
    }
    if len(shape["dimension_info"]) == 2: # image or rectangle
        relative_item["perimeter_info"] = {
            "name": shape["perimeter_info"]["name"],
            "relative_length": 2 * sum([round(item["absolute_length"] / reference_length, 1) for item in shape["dimension_info"]]),
        }
    elif len(shape["dimension_info"]) == 3: # triangle
        relative_item["perimeter_info"] = {
            "name": shape["perimeter_info"]["name"],
            "relative_length": sum([round(item["absolute_length"] / reference_length, 1) for item in shape["dimension_info"]]),
        }
    elif len(shape["dimension_info"]) == 1:  # circle
        relative_item["perimeter_info"] = {
            "name": shape["perimeter_info"]["name"],
            "relative_length": round(2 * math.pi * shape["dimension_info"][0]["absolute_length"] / reference_length, 2),
        }
    return relative_item


def generate_images(num_images, output_dir):
    jsonl_output_path = os.path.join(output_dir, "images_info.jsonl")
    image_output_path = os.path.join(output_dir, "images")
    os.makedirs(image_output_path, exist_ok=True)

    question_template_list = [
        "What is the relative length of {} compared to {}?",
        "Calculate the relative length of {} with respect to {}.",
        "Assess the relative size of {} versus {}.",
        "Measure the length of {} in relation to {}.",
        "How many units is {} if {} is 1 unit?",
        "{} is to {} as what is to 1?",
        "Calculate how long {} is relative to {}.",
        "Determine the ratio of the length of {} to that of {}.",
        "Assess the scaling factor of {} with respect to {}."
    ]
    question_template_list = ["<image>" + item + " The final answer should be a decimal number." for item in question_template_list]
    
    with open(jsonl_output_path, "w", encoding="utf-8") as f:
        for i in range(num_images):
            image_name = f"train_1d_perimeter_{str(i+1).zfill(6)}.png"
            full_image_name = os.path.join(image_output_path, image_name)

            width = random.randint(600, 1000)
            height = random.randint(600, 1000)
            image = Image.new("RGB", (width, height), "white")

            draw = ImageDraw.Draw(image)
            used_colors = set()
            existing_boxes = []

            # 随机生成几何图形的数量
            num_shapes = random.randint(2, 5)
            shape_info_list = [
                {
                    "name": "the image",
                    "dimension_info": [
                        {
                            "name": f"the width of the image",
                            "absolute_length": width
                        },
                        {
                            "name": f"the height of the image",
                            "absolute_length": height
                        }
                    ],
                    "perimeter_info": {
                        "name": f"the perimeter of the image",
                        "absolute_length": width * 2 + height * 2
                    }
                }
            ]

            for _ in range(num_shapes):
                shape = random.choice(shapes)
                if shape == "circle":
                    result = draw_circle(draw, used_colors, existing_boxes, width, height)
                elif shape == "triangle":
                    result = draw_triangle(draw, used_colors, existing_boxes, width, height)
                elif shape == "rectangle":
                    result = draw_rectangle(draw, used_colors, existing_boxes, width, height)
                if result:
                    shape_info_list.append(result)

            # 从dimension_info_list中选两条边计算相对距离
            shape1, shape2 = random.sample(shape_info_list, 2)
            dimensions = [item["absolute_length"] for item in shape1["dimension_info"] + shape2["dimension_info"]]
            reference_length = min(dimensions)
            relative_shape_info1 = relative_annotation(shape1, reference_length)
            relative_shape_info2 = relative_annotation(shape2, reference_length)

            question_template = random.choice(question_template_list)
            
            output_json = {
                "id": f"train_1d_perimeter_{str(i+1).zfill(6)}",
                "image": full_image_name,
                "shape1": relative_shape_info1,
                "shape2": relative_shape_info2,
                "question": question_template.format(relative_shape_info2["perimeter_info"]["name"], relative_shape_info1["perimeter_info"]["name"]),
                "answer": round(relative_shape_info2["perimeter_info"]["relative_length"] / relative_shape_info1["perimeter_info"]["relative_length"], 2),
            }

            f.write(json.dumps(output_json, ensure_ascii=False) + "\n")
            image.save(full_image_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'annotation', '1d_perimeter'))
    parser.add_argument("--num_images", type=int, default=2000)
    args = parser.parse_args()
    generate_images(args.num_images, args.output_dir)