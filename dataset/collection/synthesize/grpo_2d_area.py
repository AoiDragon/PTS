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
def draw_circle(draw, used_colors, existing_boxes, image, width, height):
    attempt = 0
    image_size = width * height
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
            area = math.pi * size ** 2

            shape_info = {
                "name": f"the {color} circle",
                "area": area,
            }

            existing_boxes.append(bounding_box)
            return shape_info

# 绘制三角形
def draw_triangle(draw, used_colors, existing_boxes, image, width, height):
    attempt = 0
    image_size = width * height
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

            s = (edge1 + edge2 + edge3) / 2  # 半周长
            area = math.sqrt(s * (s - edge1) * (s - edge2) * (s - edge3))

            draw.polygon(points, fill=color, outline="black")
            shape_info = {
                "name": f"the {color} triangle",
                "area": area
            }
            existing_boxes.append(bounding_box)
            return shape_info

# 绘制长方形
def draw_rectangle(draw, used_colors, existing_boxes, image, width, height):
    attempt = 0
    image_size = width * height
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

            area = edge_short1 * edge_long1

            shape_info = {
                "name": f"the {color} rectangle",
                "area": area
            }
            existing_boxes.append(bounding_box)
            return shape_info

# 批量生成图片和JSON文件
def generate_images(num_images, output_dir):
    jsonl_output_path = os.path.join(output_dir, "images_info.jsonl")
    image_output_path = os.path.join(output_dir, "images")
    os.makedirs(image_output_path, exist_ok=True)
    question_template_list = [
        "Calculate the relative area of {} to {}.",
        "Compute the proportion of {}'s area relative to {}'s area.",
        "Solve for {}'s area if the area of {} = 1.0.",
        "Express the area of {} as a decimal when the area of {} is 1.0.",
        "What is the area of {} relative to {}?",
        "I need you to calculate how large {} is relative to {} in terms of area.",
    ]
    question_template_list = ["<image>" + item + " The final answer should be a decimal number." for item in question_template_list] 

    with open(jsonl_output_path, "w", encoding="utf-8") as f:
        count = 0
        while count < num_images:
            image_name = f"{str(count+1).zfill(6)}.png"
            full_image_name = os.path.join(image_output_path, image_name)

            width = random.randint(600, 1000)
            height = random.randint(600, 1000)
            image = Image.new("RGB", (width, height), "white")
            draw = ImageDraw.Draw(image)

            used_colors = set()
            existing_boxes = []

            area_info_list = [
                {
                    "name": f"the image",
                    "area": width * height
                },
            ]

            num_shapes = random.randint(2, 5)
            for _ in range(num_shapes):
                shape = random.choice(shapes)
                if shape == "circle":
                    result = draw_circle(draw, used_colors, existing_boxes, full_image_name, width, height)
                elif shape == "triangle":
                    result = draw_triangle(draw, used_colors, existing_boxes, full_image_name, width, height)
                elif shape == "rectangle":
                    result = draw_rectangle(draw, used_colors, existing_boxes, full_image_name, width, height)
                if result:
                    area_info_list.append(result)
            area1, area2 = random.sample(area_info_list, 2) 
            question_template = random.choice(question_template_list)
            smaller_area = area1 if area1["area"] < area2["area"] else area2
            larger_area = area2 if area1["area"] < area2["area"] else area1
            # grpo_item = {
            #     "id": f"grpo_2d_area_{str(i + 1).zfill(6)}",
            #     "images": full_image_name,
            #     "problem": question_template.format(smaller_area["name"], larger_area["name"]),
            #     "answer": round(smaller_area["area"] / larger_area["area"], 2)
            # }
            grpo_item = {
                "id": f"grpo_2d_area_normal_{str(count+1).zfill(6)}",
                "images": [full_image_name],
                "problem": question_template.format(area2["name"], area1["name"]),
                "answer": round(area2["area"] / area1["area"], 2)
            }
            if round(area2["area"] / area1["area"], 2) != 0:
                append_jsonl(jsonl_output_path, grpo_item)
                image.save(full_image_name)
                count += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'grpo', '2d_area'))
    parser.add_argument("--num_images", type=int, default=2000)
    args = parser.parse_args()
    generate_images(args.num_images, args.output_dir)