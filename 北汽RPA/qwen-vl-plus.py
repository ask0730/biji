# -*- coding: utf-8 -*-
import base64
import io
import os
import time
import requests
from PIL import Image
import pythoncom
import win32com.client as win32

BASE_URL = "http://192.168.100.121:9080"
API_KEY = "sk-PxldK3SEs3uMLbwd8353AbA99dAd4a30B8Ee7f79C7F075Fc"
MODEL = "Qwen3-VL-30B-A3B-Instruct"

def img_to_base64(img_path):
    """图片转base64"""
    try:
        with Image.open(img_path) as img:
            img = img.convert("RGB")
            img.thumbnail((1600, 1600))
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=90)
            return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print("图片处理异常：", str(e))
        return ""

def word_multi_page_to_images(word_path, temp_dir="temp_pages"):
    """
    多页Word → 逐页截图 → 生成多张图片
    返回：图片路径列表
    """
    pythoncom.CoInitialize()
    word = None
    doc = None
    page_img_paths = []
    
    try:
        # 创建临时目录
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # 启动Word并打开文档
        word = win32.Dispatch("Word.Application")
        word.Visible = True
        word.WindowState = 1  # 最大化窗口，保证截图完整
        word.DisplayAlerts = 0
        
        doc = word.Documents.Open(os.path.abspath(word_path))
        doc.Activate()
        
        # 获取总页数
        total_pages = doc.ComputeStatistics(2)  # 2 = wdStatisticPages
        print(f"Word文档总页数：{total_pages}")
        
        # 逐页截图
        for page_num in range(1, total_pages + 1):
            print(f"正在截图第 {page_num}/{total_pages} 页...")
            # 跳转到指定页
            word.Selection.GoTo(What=1, Which=1, Count=page_num)
            # 等待页面渲染
            time.sleep(1)
            
            # 截图并保存
            img_path = os.path.join(temp_dir, f"page_{page_num}.jpg")
            from PIL import ImageGrab
            img = ImageGrab.grab()
            img.save(img_path, "JPEG", quality=95)
            page_img_paths.append(img_path)
        
        return page_img_paths
        
    except Exception as e:
        print(f"多页截图失败：{e}")
        return []
    finally:
        if doc:
            doc.Close(False)
        if word:
            word.Quit()
        pythoncom.CoUninitialize()

def is_word_file(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    return ext in [".doc", ".docx"]

def 识别多页文件内容(指令, 文件路径):
    temp_dir = "temp_pages"
    page_imgs = []
    all_results = []
    
    try:
        # 处理Word文件
        if is_word_file(文件路径):
            print("检测到Word文件，正在逐页截图...")
            page_imgs = word_multi_page_to_images(文件路径, temp_dir)
            if not page_imgs:
                return "Word截图失败"
        else:
            # 单张图片直接识别
            page_imgs = [文件路径]
        
        # 逐页调用模型识别
        for idx, img_path in enumerate(page_imgs, 1):
            print(f"正在识别第 {idx}/{len(page_imgs)} 页...")
            b64 = img_to_base64(img_path)
            if not b64:
                all_results.append(f"第{idx}页：图片读取失败")
                continue
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + API_KEY
            }
            
            payload = {
                "model": MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"这是文档的第{idx}页，{指令}"},
                            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}
                        ]
                    }
                ],
                "temperature": 0.1
            }
            
            resp = requests.post(
                BASE_URL + "/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=120,
                proxies={"http": None, "https": None}
            )
            
            resp.raise_for_status()
            result = resp.json()
            if "choices" in result:
                all_results.append(f"===== 第{idx}页识别结果 =====\n{result['choices'][0]['message']['content']}")
            else:
                all_results.append(f"第{idx}页：模型错误 - {str(result)}")
        
        return "\n\n".join(all_results)
        
    except Exception as e:
        return f"异常：{str(e)}"
    finally:
        # 清理临时文件
        if os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, f))
                except:
                    pass
            os.rmdir(temp_dir)

# ===================== 测试调用 =====================
if __name__ == "__main__":
    # 直接传入任意页数的Word
    结果 = 识别多页文件内容("提取所有文字并排版，保留表格和图片信息", r"D:\Desktop\demo\北汽RPA\test.docx")
    
    print("=" * 50)
    print("完整识别结果11：")
    print("=" * 50)
    print(结果)