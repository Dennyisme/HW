import torch
import requests
from models.clipseg import CLIPDensePredT
from PIL import Image
from torchvision import transforms
from matplotlib import pyplot as plt
import os
import numpy as np
from sklearn.metrics import precision_recall_curve, average_precision_score
from tqdm import tqdm
from matplotlib.colors import ListedColormap

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def process_mask(image_path):
    # Load image
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img)
    # Create mask
    mask = np.all(img_array == [0, 0, 0], axis=-1)  # Detect black pixels
    processed_mask = np.where(mask, 0, 1).astype(np.uint8)  # Background -> 255 (white), Foreground -> 0 (black)
    
    # Save processed mask
    processed_img = Image.fromarray(processed_mask)

    return processed_img

# def compute_metrics(pred_mask, true_mask):
#     intersection = np.logical_and(pred_mask, true_mask) # TP
#     union = np.logical_or(pred_mask, true_mask) # TP + FN + FP
#     iou = np.sum(intersection) / np.sum(union) # TP / ( TP + FN + FP )
#     return iou

def compute_metrics_moiu(pred_mask, true_mask):
    intersection = np.logical_and(pred_mask, true_mask) # TP
    inverted_intersection = np.logical_not(intersection) # TN + FN + FP
    
    union = np.logical_or(pred_mask, true_mask) # TP + FN + FP
    inverted_union = np.logical_not(union) # TN
    
    moiu = 0.5 * ( np.sum(inverted_union) / np.sum(inverted_intersection) + np.sum(intersection) / np.sum (union) )
    
    return moiu

    

def compute_ap(pred_mask, true_mask):
    pred_mask = pred_mask.flatten()
    true_mask = true_mask.flatten()
    precision, recall, _ = precision_recall_curve(true_mask, pred_mask)
    ap = average_precision_score(true_mask, pred_mask)
    return ap

def compute_ious(pred_masks, answer_image_array):
    # Ensure pred_masks is a NumPy array
    if torch.is_tensor(pred_masks):
        pred_masks = pred_masks.cpu().numpy()
    
    # Ensure the shapes are the same
    if pred_masks.shape != answer_image_array.shape:
        raise ValueError("Shapes of prediction and ground truth masks do not match.")

    pred_mask_flat = pred_masks.flatten()
    true_mask_flat = answer_image_array.flatten()

    # Compute mIoU
    miou = compute_metrics_moiu(pred_masks, answer_image_array)

    # Compute IoUBIN
    # threshold = 0.5
    # pred_mask_bin = (pred_mask_flat > threshold).astype(np.uint8)
    iou_bin = compute_metrics_moiu(pred_mask_flat, true_mask_flat)

    # Compute AP
    ap = compute_ap(pred_mask_flat, true_mask_flat)

    return miou, iou_bin, ap

# load model
model = CLIPDensePredT(version='ViT-B/16', reduce_dim=64)
model.eval()
# non-strict, because we only stored decoder weights (not CLIP weights)
model.load_state_dict(torch.load('clipseg_weights/rd64-uni.pth', map_location=torch.device('cpu')), strict=False)

predict_pascal_5i = True
predict_own_picture = False

if predict_pascal_5i:

    file_path = "data/VOC2012/ImageSets/Main/aeroplane_train.txt"
    image_id_list = []
    with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if parts[1] == "1":
                    image_id = parts[0]
                    image_id_list.append(image_id)

    image_num = 0
    total_mIoU = 0
    total_mIoBIN = 0
    total_AP = 0

    for image_id in tqdm(image_id_list):
        image_file_path = f'data/VOC2012/JPEGImages/{image_id}.jpg'
        
        
        # load and normalize image
        input_image = Image.open(image_file_path)
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            transforms.Resize((352, 352)),
        ])
        img = transform(input_image).unsqueeze(0)
        
        prompts = ['airplanes']

        sub_image_num = len(prompts) #　先為１就好
        # predict
        with torch.no_grad():
            preds = model(img.repeat(sub_image_num,1,1,1), prompts)[0]
            
        preds_sigmoid = torch.sigmoid(preds)  # 应用 sigmoid 激活函数
        print(f"Predicted probabilities min: {preds_sigmoid.min().item()}, max: {preds_sigmoid.max().item()}")
        threshold = 0.5 # 正確版
        # threshold = 0.6
        pred_masks = (preds_sigmoid > threshold).float()  # 轉換成二值掩碼
        # 检查二值掩码中前景像素的数量
        print(f"Foreground pixels: {pred_masks.sum().item()}")

        answer_image_path = f"data/VOC2012/SegmentationObject/{image_id}.png"
        if not os.path.exists(answer_image_path):
            print(f"File not found: {answer_image_path}. Skipping this image.")
            continue
        
        answer_image = process_mask(answer_image_path)
        answer_image_array = np.array(answer_image.resize((pred_masks[0][0].shape[1], pred_masks[0][0].shape[0]), Image.NEAREST))

        cmap = ListedColormap(['white', 'black'])
        # visualize prediction
        _, ax = plt.subplots(1, sub_image_num + 3, figsize=(15, 4))
        [a.axis('off') for a in ax.flatten()]
        ax[0].imshow(input_image)
        for i in range(sub_image_num):
            ax[i+1].imshow(pred_masks[i][0], cmap = cmap)
            ax[i+1].text(0, -15, prompts[i])
            ax[i+1].set_frame_on(True)
        
        ax[sub_image_num + 1].imshow(preds_sigmoid[0][0])
        ax[sub_image_num + 1].text(0, -15, "heatmap")
        
        ax[sub_image_num + 2].imshow(answer_image_array, cmap = cmap)
        ax[sub_image_num + 2].text(0, -15, "answer")
        
        pred_result_np = pred_masks[0][0].cpu().numpy()
        miou, iou_bin, ap = compute_ious(pred_result_np, answer_image_array)
        image_num += 1
        total_mIoU += miou
        total_mIoBIN += iou_bin
        total_AP += ap
        
        print(f'{image_id}- mIoU: {miou}, IoUBIN: {iou_bin}, AP: {ap}')
        plt.figtext(0.5, 0.01, f"mIoU: {miou:.4f}, IoUBIN: {iou_bin:.4f}, AP: {ap:.4f}", ha="center", fontsize=12)
        # result_path = f'result/VOC2012/{image_id}.jpg'   
        result_path = f'result/VOC2012_prompt_modified/{image_id}.jpg'
        # result_path = f'result/額外/VOC2012/{image_id}.jpg'
        # result_path = f'result/額外/VOC2012_prompt_modified/{image_id}.jpg'
        ensure_dir(result_path)
        plt.savefig(result_path)
        plt.close()

    avg_mIoU = round(total_mIoU / image_num * 100, 2)
    avg_mIoBIN = round(total_mIoBIN / image_num * 100, 2)
    avg_AP = round(total_AP / image_num * 100, 2)
    print("total count: ", image_num)

    print(f"Average mIou: {avg_mIoU}, Average mIoBIN: {avg_mIoBIN}, Average AP: {avg_AP}")

if predict_own_picture:
    
    image_file_path = f'data/pen.jpg'
    
    # load and normalize image
    input_image = Image.open(image_file_path)
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        transforms.Resize((352, 352)),
    ])
    img = transform(input_image).unsqueeze(0)
    
    prompts = ['pen']
    
    # predict
    with torch.no_grad():
        preds = model(img.repeat(1,1,1,1), prompts)[0]
    
    preds_sigmoid = torch.sigmoid(preds)
    threshold = 0.6
    pred_masks = (preds_sigmoid > threshold).float()
    cmap = ListedColormap(['white', 'black'])
    _, ax = plt.subplots(1, 3, figsize=(15, 4))
    [a.axis('off') for a in ax.flatten()]
    ax[0].imshow(input_image)
    ax[1].imshow(pred_masks[0][0], cmap = cmap)
    ax[1].text(0, -15, prompts[0])
    ax[1].set_frame_on(True) 
    
    ax[2].imshow(preds_sigmoid[0][0])
    ax[2].text(0, -15, "heatmap")   
    
    result_path = f'result/own_picture/prompt_pen.jpg'  
    ensure_dir(result_path)
    plt.savefig(result_path)
    plt.close()