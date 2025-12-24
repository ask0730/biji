# -*- coding: utf-8 -*-
"""
南京图书馆年报下载脚本
功能：从南京图书馆官网下载去年的年报，并重命名为"南京图书馆年份年报"格式
"""

import requests
import os
import time
import re
import urllib3
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def setup_selenium_driver():
    """设置Selenium浏览器驱动"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def get_headers():
    """获取模拟浏览器的请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/pdf',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def clean_filename(filename):
    """清理文件名，移除Windows不允许的字符"""
    invalid_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(invalid_chars, '_', filename)
    cleaned = cleaned.strip(' .')
    if not cleaned:
        cleaned = "unnamed_file"
    return cleaned

def extract_year_from_text(text):
    """从文本中提取年份，优先提取完整的年份（如2023、2024）"""
    if not text:
        return None
    # 优先匹配完整的4位年份（2000-2099）
    year_match = re.search(r'(20[0-3]\d)', text)
    if year_match:
        return year_match.group(1)
    return None


def load_config(config_path="config.txt"):
    """读取配置文件"""
    config = {}
    try:
        if not os.path.exists(config_path):
            # 如果配置文件不存在，创建默认配置
            default_config = """# 配置文件
# 格式：key=value
# 支持使用 # 开头添加注释
# 支持空行

# 输出文件夹路径（必填）
# 示例：output_folder=D:\\Desktop\\图书馆年报
output_folder=D:\\Desktop\\图书馆年报
"""
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(default_config)
            print(f"✓ 已创建默认配置文件: {config_path}")
            print("  请编辑配置文件设置输出路径后重新运行")
            return None
        
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    config[key] = value
    except Exception as e:
        print(f"✗ 读取配置文件失败: {e}")
        return None
    
    return config

def find_last_year_report(url, base_url):
    """在页面中查找去年的年报链接"""
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    last_year_str = str(last_year)
    
    driver = None
    try:
        print(f"正在使用浏览器访问页面: {url}")
        driver = setup_selenium_driver()
        driver.get(url)
        
        # 等待页面加载
        time.sleep(3)
        
        # 等待列表项加载
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.wzList li"))
            )
        except TimeoutException:
            print("⚠️  等待列表项超时，继续尝试...")
        
        time.sleep(2)
        
        # 获取渲染后的页面源码
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 查找 ul.wzList 下的链接
        wz_list = soup.find('ul', class_='wzList')
        if not wz_list:
            print("✗ 未找到 wzList 容器")
            return None
        
        # 查找所有 li > div > a 结构
        all_links = []
        li_elements = wz_list.find_all('li', recursive=True)
        
        for li in li_elements:
            divs = li.find_all('div', recursive=True)
            for div in divs:
                a_tag = div.find('a', href=True)
                if a_tag:
                    href = a_tag.get('href')
                    text = a_tag.get_text().strip()
                    
                    if not href or href.startswith('javascript:') or href.startswith('#'):
                        continue
                    
                    # 构建完整URL
                    if href.startswith('http://') or href.startswith('https://'):
                        full_url = href
                    else:
                        full_url = urljoin(url, href)
                    
                    # 提取年份
                    year = extract_year_from_text(text) or extract_year_from_text(href)
                    
                    # 检查是否包含年报相关关键词
                    keywords = ['年报', '年度报告', '年度', '决算', '公开']
                    is_report = any(keyword in text or keyword in href for keyword in keywords)
                    
                    if year or is_report:
                        all_links.append({
                            'url': full_url,
                            'text': text,
                            'year': year,
                            'is_pdf': full_url.lower().endswith('.pdf')
                        })
                    break
        
        # 查找去年的年报
        last_year_links = [link for link in all_links if link['year'] == last_year_str or last_year_str in link['text']]
        
        if not last_year_links:
            # 如果没有找到，尝试查找所有包含去年年份的链接
            for link in all_links:
                if last_year_str in link['text'] or last_year_str in link['url']:
                    if not link['year']:
                        link['year'] = last_year_str
                    last_year_links.append(link)
        
        if last_year_links:
            # 优先选择PDF链接
            pdf_links = [link for link in last_year_links if link['is_pdf']]
            if pdf_links:
                result = pdf_links[0]
                print(f"✓ 找到去年的年报: {result['text']} (年份: {result['year']})")
                return result['url'], result['year']
            
            # 如果不是PDF，访问链接页面查找PDF
            for link_info in last_year_links:
                if any(keyword in link_info['text'] for keyword in ['年报', '年度报告', '决算', '公开']):
                    print(f"访问链接页面查找PDF: {link_info['url']}")
                    try:
                        session = requests.Session()
                        session.headers.update(get_headers())
                        response = session.get(link_info['url'], timeout=30, verify=False)
                        response.encoding = response.apparent_encoding or 'utf-8'
                        link_soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # 查找PDF链接
                        for pdf_link in link_soup.find_all('a', href=True):
                            pdf_href = pdf_link.get('href')
                            if pdf_href and pdf_href.lower().endswith('.pdf'):
                                pdf_url = urljoin(link_info['url'], pdf_href)
                                if last_year_str in pdf_url or last_year_str in pdf_link.get_text():
                                    print(f"✓ 找到PDF: {pdf_url}")
                                    return pdf_url, last_year_str
                        
                        # 查找iframe中的PDF
                        for iframe in link_soup.find_all('iframe', src=True):
                            iframe_src = iframe.get('src')
                            if iframe_src and iframe_src.lower().endswith('.pdf'):
                                pdf_url = urljoin(link_info['url'], iframe_src)
                                print(f"✓ 找到PDF (iframe): {pdf_url}")
                                return pdf_url, last_year_str
                    except Exception as e:
                        print(f"  访问失败: {e}")
                        continue
            
            # 返回第一个链接
            result = last_year_links[0]
            print(f"✓ 找到去年的链接: {result['text']} (年份: {result['year']})")
            return result['url'], result['year']
        
        print(f"✗ 未找到 {last_year} 年的年报")
        return None
        
    except Exception as e:
        print(f"✗ 查找失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if driver:
            driver.quit()

def download_pdf(url, filename, save_dir):
    """下载PDF文件"""
    try:
        session = requests.Session()
        session.headers.update(get_headers())
        
        print(f"正在下载: {url}")
        # requests库会自动处理URL编码，包括中文文件名
        response = session.get(url, stream=True, timeout=60, verify=False)
        response.raise_for_status()
        
        # 检查内容类型
        content_type = response.headers.get('Content-Type', '').lower()
        if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
            print(f"⚠️  警告: 内容类型可能不是PDF: {content_type}")
        
        # 确保文件名以.pdf结尾
        if not filename.endswith('.pdf'):
            filename = filename + '.pdf'
        
        # 清理文件名
        filename = clean_filename(filename)
        
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)
        
        # 如果文件已存在，先删除
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"  已删除已存在的文件: {filename}")
            except:
                pass
        
        # 保存文件
        file_size = 0
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    file_size += len(chunk)
        
        # 验证文件是否成功保存
        if not os.path.exists(file_path):
            print(f"✗ 文件保存失败: {file_path}")
            return False
        
        actual_size = os.path.getsize(file_path)
        print(f"✓ 下载成功: {filename}")
        print(f"  文件大小: {actual_size:,} 字节 ({actual_size/1024/1024:.2f} MB)")
        print(f"  保存路径: {file_path}")
        
        session.close()
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ 下载失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 发生错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("南京图书馆年报下载工具")
    print("=" * 60)
    
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.txt")
    
    # 读取配置文件
    config = load_config(config_path)
    if config is None:
        return
    
    # 获取输出路径
    output_folder = config.get("output_folder", "").strip()
    if not output_folder:
        print("✗ 错误: 配置文件中未设置 output_folder")
        print("  请在配置文件中设置输出路径")
        return
    
    # 获取去年的年份
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    last_year_str = str(last_year)
    
    # 南京图书馆年报页面URL
    report_page_url = "https://www.jslib.org.cn/gk/jgnb/jslib_xxgk/"
    base_url = "https://www.jslib.org.cn"
    
    print(f"目标年份: {last_year}年")
    print(f"输出路径: {output_folder}")
    print("-" * 60)
    
    # 查找年报链接
    result = find_last_year_report(report_page_url, base_url)
    
    if not result:
        print("\n✗ 未找到年报链接，下载失败")
        return
    
    # 处理返回值
    if isinstance(result, tuple):
        pdf_url, actual_year = result
        year_for_filename = actual_year or last_year_str
    else:
        pdf_url = result
        year_for_filename = last_year_str
    
    # 生成文件名，使用实际找到的年份
    filename = f"南京图书馆{year_for_filename}年年报.pdf"
    filename = clean_filename(filename)
    
    print(f"\n文件名: {filename}")
    print("-" * 60)
    
    # 下载文件
    success = download_pdf(pdf_url, filename, output_folder)
    
    if success:
        print("\n" + "=" * 60)
        print("✓ 下载完成")
        print("=" * 60)
        print(f"文件已保存到: {os.path.join(output_folder, filename)}")
    else:
        print("\n" + "=" * 60)
        print("✗ 下载失败")
        print("=" * 60)

if __name__ == "__main__":
    main()

