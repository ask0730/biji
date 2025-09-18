import requests
import os
import time
import random
from urllib.parse import urlparse

def download_pdf_stealth(url, filename=None, delay_range=(1, 3)):
    """
    隐蔽下载PDF文件
    
    Args:
        url (str): PDF文件的URL
        filename (str): 保存的文件名，如果为None则从URL中提取
        delay_range (tuple): 随机延迟范围（秒）
    """
    try:
        # 模拟真实浏览器的请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # 创建会话以保持连接
        session = requests.Session()
        session.headers.update(headers)
        
        # 随机延迟，模拟人类行为
        delay = random.uniform(delay_range[0], delay_range[1])
        print(f"等待 {delay:.1f} 秒...")
        time.sleep(delay)
        
        # 发送GET请求下载文件
        response = session.get(url, stream=True, timeout=30)
        response.raise_for_status()  # 检查请求是否成功
        
        # 如果没有指定文件名，从URL中提取
        if filename is None:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename.endswith('.pdf'):
                filename = 'downloaded_file.pdf'
        
        # 确保文件名以.pdf结尾
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        # 下载并保存文件
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"PDF文件已成功下载: {filename}")
        print(f"文件大小: {os.path.getsize(filename)} 字节")
        
        # 关闭会话
        session.close()
        
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    # PDF下载链接
    pdf_url = "https://www.gzlib.com.cn/tcsoft/resources/files/20221215/33769c82-0734-4eb3-a0c1-f646f64320bf.pdf"
    
    print("PDF下载工具")
    print("=" * 30)
    print("使用隐蔽模式下载...")
    download_pdf_stealth(pdf_url, "downloaded_document.pdf")
