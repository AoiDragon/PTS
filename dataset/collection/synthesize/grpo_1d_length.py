from PIL import Image, ImageDraw
import random
import math
import json
import os
import argparse
from tqdm import tqdm

# 定义一些颜色
colors = ["red", "green", "blue", "yellow", "purple", "orange"]

# 图片尺寸
max_retries = 10  # 增加重试次数

# 几何图形类别
shapes = ["circle", "triangle", "rectangle"]
        
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
    # 计算总共有多少个=
    total_equals = int(number * 10)
    
    # 每10个=为一组，用<>包裹
    groups = []
    for i in range(0, total_equals, 10):
        group = '=' * min(10, total_equals - i)
        groups.append(f'<{group}>')
    
    # 将所有的组连接起来
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

            dimension_info = [
                {
                    "name": f"the radius of the {color} circle",
                    "absolute_length": size
                },
                {
                    "name": f"the diameter of the {color} circle",
                    "absolute_length": 2*size
                }
            ]
            existing_boxes.append(bounding_box)
            return dimension_info

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
            dimension_info = [
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
            ]
            existing_boxes.append(bounding_box)
            return dimension_info

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

            dimension_info = [
                {
                    "name": f"the longer side of the {color} rectangle",
                    "absolute_length": edge_long1
                },
                {
                    "name": f"the shorter side of the {color} rectangle",
                    "absolute_length": edge_short1
                }
            ]
            existing_boxes.append(bounding_box)
            return dimension_info

# 批量生成图片和JSON文件
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
        "Calculate how long {} is relative to {}.",
        "Assess the scaling factor of {} with respect to {}."
    ]
    question_template_list = ["<image>" + item + " The final answer should be a decimal number." for item in question_template_list]

    with open(jsonl_output_path, "w", encoding="utf-8") as f:
        for i in tqdm(range(num_images)):
            image_name = f"{str(i+1).zfill(6)}.png"
            full_image_name = os.path.join(image_output_path, image_name)

            width = random.randint(600, 1000)
            height = random.randint(600, 1000)
            image = Image.new("RGB", (width, height), "white")
            draw = ImageDraw.Draw(image)

            used_colors = set()
            existing_boxes = []

            # 随机生成几何图形的数量
            num_shapes = random.randint(2, 5)
            dimension_info_list = [
                {
                    "name": f"the width of the image",
                    "absolute_length": width
                },
                {
                    "name": f"the height of the image",
                    "absolute_length": height
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
                    dimension_info_list.extend(result)

            # 从dimension_info_list中选两条边计算相对距离
            side1, side2 = random.sample(dimension_info_list, 2)  # 默认side1为src, side2为target
            reference_length = min(side1["absolute_length"], side2["absolute_length"])
            question_template = random.choice(question_template_list)
            relative_length1 = round(side1["absolute_length"] / reference_length, 1)
            relative_length2 = round(side2["absolute_length"] / reference_length, 1)

            eval_item = {
                "id": f"grpo_1d_length_normal_{str(i+1).zfill(6)}",
                "images": [full_image_name],
                "problem": question_template.format(side2["name"], side1["name"]),
                "answer": round(side2["absolute_length"] / side1["absolute_length"], 2)
            }
            # shorter_side = side1 if side1["absolute_length"] < side2["absolute_length"] else side2
            # longer_side = side2 if side1["absolute_length"] < side2["absolute_length"] else side1

            # reference_length = shorter_side["absolute_length"]
            # question_template = random.choice(question_template_list)

            # eval_item = {
            #     "id": f"grpo_1d_length_{str(i + 1).zfill(6)}",
            #     "images": full_image_name,
            #     "problem": question_template.format(shorter_side["name"], longer_side["name"]),
            #     "answer": round(shorter_side["absolute_length"] / longer_side["absolute_length"], 2)
            # }

            f.write(json.dumps(eval_item, ensure_ascii=False) + "\n")
            image.save(full_image_name)

# 生成100张图片
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'grpo', '1d_length'))
    parser.add_argument("--num_images", type=int, default=2000)
    args = parser.parse_args()
    generate_images(args.num_images, args.output_dir)