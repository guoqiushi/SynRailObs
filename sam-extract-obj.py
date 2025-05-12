import numpy as np
import cv2
from segment_anything import SamPredictor, sam_model_registry
from PIL import Image
import glob
import os
import json

model_type="vit_b"
sam_ckpt_path = 'D:/jupyter/segment-anything/sam_vit_b_01ec64.pth'
sam = sam_model_registry[model_type](checkpoint=sam_ckpt_path)
predictor = SamPredictor(sam)

def segment_object_with_sam(image_path, points,save_path="output.png"):

    # 2. 读取图像
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    predictor.set_image(image_rgb)

    # 3. 构建 prompt
    input_point = np.array(points)
    input_label = np.ones(len(points))  # 所有点都作为前景

    # 4. 预测掩码
    masks, scores, _ = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True
    )
    best_mask = masks[np.argmax(scores)]  # 取得分最高的掩码

    # 5. 应用掩码：生成透明背景 PNG
    result = image_rgb.copy()
    mask_uint8 = (best_mask * 255).astype(np.uint8)

    # 生成带 alpha 通道的图像
    rgba = cv2.cvtColor(result, cv2.COLOR_RGB2RGBA)
    rgba[:, :, 3] = mask_uint8  # 设置透明度

    # 保存为 PNG
    Image.fromarray(rgba).save(save_path)
    print(f"Saved segmented object to {save_path}")

def extract_labelme_points(json_path):
    """
    提取 LabelMe JSON 文件中所有 point 类型的标注点信息。

    参数:
        json_path (str): JSON 文件路径。

    返回:
        List[Dict]: 每个点的信息，包括 label、x、y。
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    result = []
    for shape in data.get('shapes', []):
        if shape.get('shape_type') == 'point':
            label = shape.get('label')
            x, y = shape['points'][0]
            result.append([x,y])

    return result

if __name__ == '__main__':

    obj_list = glob.glob('E:/synRailoBS/non-person/*.jpg')
    for img_path in obj_list:
        img_name = os.path.basename(img_path)
        json_path = os.path.join('E:/synRailoBS/non-person', os.path.basename(img_path).split('.')[0] + '.json')
        segment_object_with_sam(
            image_path=img_path,
            points=extract_labelme_points(json_path),
            save_path='D:/dataset/sam-obj/non-person/{}'.format(img_name.split('.')[0] + '.png')
        )
