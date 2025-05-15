import random
import math


def bezier_curve(points, num=100):
    n = len(points) - 1
    t_values = np.linspace(0, 1, num=num)

    def bernstein(i, n, t):
        return comb(n, i) * (t ** i) * ((1 - t) ** (n - i))

    def comb(n, k):
        from math import comb as math_comb
        return math_comb(n, k)

    curve = []
    for t in t_values:
        x = sum(bernstein(i, n, t) * p[0] for i, p in enumerate(points))
        y = sum(bernstein(i, n, t) * p[1] for i, p in enumerate(points))
        curve.append((x, y))

    return curve


def extract_bezier_region(image_path, bezier_points, output_path=None):
    if isinstance(image_path, str):
        image = Image.open(image_path).convert("RGBA")
    else:
        image = image_path.convert("RGBA")

    width, height = image.size

    # 1. 生成贝塞尔曲线路径
    curve = bezier_curve(bezier_points, num=300)

    # 2. 创建掩码图像
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(curve, fill=255)

    # 3. 应用掩码
    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    result.paste(image, mask=mask)

    # 4. 可选保存
    if output_path:
        result.save(output_path, format="PNG")

    return result

def generate_curvy_bezier_points(center=(300, 300), radius=150, num_points=20, jitter=60, seed=None):
    if seed is not None:
        random.seed(seed)

    cx, cy = center
    bezier_points = []

    # 控制“频率”和“波动程度”
    base_freq = random.uniform(1.5, 3.0)
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        # 引入一个非线性扰动项（模拟 perlin-like 波动）
        distortion = math.sin(angle * base_freq + random.uniform(-0.5, 0.5))
        r = radius + distortion * jitter + random.uniform(-jitter / 2, jitter / 2)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        bezier_points.append((x, y))

    # 闭合曲线
    bezier_points.append(bezier_points[0])
    return bezier_points

if __name__ == '__main__':
    # 控制点定义一个贝塞尔闭合区域
    bezier_points = generate_curvy_bezier_points()
    # 调用函数
    result_img = extract_bezier_region("D:/dataset/dtd/images/bumpy/bumpy_0021.jpg", bezier_points,
                                       output_path='dtd_patch.png')

    # 显示或保存
    result_img.show()
    # result_img.save("cropped_region.png")
