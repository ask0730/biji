# -*- coding: utf-8 -*-
"""
宁夏图书馆年报下载脚本
功能：从宁夏文化和旅游厅网站查找并下载宁夏图书馆的决算报告
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import requests
import os
import time
import re
import urllib3
from urllib.parse import urljoin, urlparse
import random

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def simulate_human_delay(min_seconds=0.5, max_seconds=1.5):
    """模拟人类操作的延迟"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def simulate_human_click(driver, element):
    """模拟人类点击行为"""
    try:
        # 滚动到元素可见
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
        simulate_human_delay(0.3, 0.8)
        
        # 移动到元素上并点击
        ActionChains(driver).move_to_element(element).pause(random.uniform(0.1, 0.3)).click().perform()
        simulate_human_delay(0.5, 1.0)
        return True
    except Exception as e:
        # 如果ActionChains失败，尝试直接点击
        try:
            driver.execute_script("arguments[0].click();", element)
            simulate_human_delay(0.5, 1.0)
            return True
        except:
            print(f"  点击失败: {e}")
            return False

def setup_selenium_driver(download_dir=None):
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
    
    # 如果指定了下载目录，配置下载选项
    if download_dir:
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True  # PDF文件自动下载
        }
        chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

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

def download_pdf(url, filename, save_dir):
    """下载PDF文件"""
    try:
        session = requests.Session()
        session.headers.update(get_headers())
        
        print(f"正在下载: {url}")
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

def find_and_download_report(url, base_url, save_dir, last_year_str):
    """查找并下载宁夏图书馆决算报告"""
    driver = None
    try:
        print("正在启动浏览器...")
        driver = setup_selenium_driver(download_dir=save_dir)
        
        print(f"正在访问页面: {url}")
        driver.get(url)
        
        # 等待页面加载
        print("等待页面加载...")
        simulate_human_delay(2, 3)
        
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            print("  页面加载超时，继续尝试...")
        
        # 滚动页面确保内容加载
        print("滚动页面加载所有内容...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        simulate_human_delay(1, 2)
        driver.execute_script("window.scrollTo(0, 0);")
        simulate_human_delay(1, 2)
        
        # 查找包含"图书馆"和"决算"的链接
        print("\n查找包含'图书馆'和'决算'的链接...")
        
        keywords = ['图书馆', '决算']
        target_links = []
        
        # 方法1: 查找所有链接
        all_links = driver.find_elements(By.TAG_NAME, "a")
        print(f"  找到 {len(all_links)} 个链接")
        
        for link in all_links:
            try:
                text = link.text.strip()
                href = link.get_attribute('href')
                
                if not text or not href:
                    continue
                
                # 检查是否包含关键词
                if all(keyword in text for keyword in keywords):
                    # 提取年份
                    year_in_text = extract_year_from_text(text)
                    
                    target_links.append({
                        'element': link,
                        'text': text,
                        'href': href,
                        'year': year_in_text
                    })
                    print(f"  ✓ 找到链接: {text} (年份: {year_in_text or '未知'})")
            except:
                continue
        
        # 方法2: 如果方法1没找到，放宽条件
        if not target_links:
            print("  未找到同时包含两个关键词的链接，尝试放宽条件...")
            for link in all_links:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')
                    
                    if not text or not href:
                        continue
                    
                    # 检查是否包含"图书馆"或"决算"
                    if '图书馆' in text and '决算' in text:
                        year_in_text = extract_year_from_text(text)
                        target_links.append({
                            'element': link,
                            'text': text,
                            'href': href,
                            'year': year_in_text
                        })
                        print(f"  ✓ 找到链接: {text} (年份: {year_in_text or '未知'})")
                except:
                    continue
        
        if not target_links:
            print("  ✗ 未找到符合条件的链接")
            print("  显示前20个链接供参考:")
            for i, link in enumerate(all_links[:20]):
                try:
                    text = link.text.strip()
                    if text:
                        print(f"    {i+1}. {text[:80]}")
                except:
                    pass
            return None
        
        # 优先选择去年的链接
        target_link = None
        for link_info in target_links:
            if link_info['year'] == last_year_str:
                target_link = link_info
                print(f"\n✓ 找到去年的链接: {target_link['text']}")
                break
        
        # 如果没有去年的，选择第一个
        if not target_link:
            target_link = target_links[0]
            print(f"\n⚠️  未找到 {last_year_str} 年的链接，将点击: {target_link['text']}")
        
        # 点击链接
        print(f"\n准备点击链接: {target_link['text']}")
        print(f"  链接URL: {target_link['href']}")
        
        if simulate_human_click(driver, target_link['element']):
            print("  ✓ 已点击链接")
        else:
            # 如果模拟点击失败，尝试直接点击
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_link['element'])
                simulate_human_delay(0.5, 1.0)
                target_link['element'].click()
                print("  ✓ 已点击链接（直接点击）")
            except Exception as e:
                print(f"  ✗ 点击链接失败: {e}")
                return None
        
        # 等待新页面加载
        print("\n等待新页面加载...")
        simulate_human_delay(3, 5)
        
        # 获取新页面URL
        new_url = driver.current_url
        print(f"新页面URL: {new_url}")
        
        # 尝试从页面中提取年份
        page_text = driver.page_source
        page_title = driver.title
        extracted_year = extract_year_from_text(page_text) or extract_year_from_text(page_title) or extract_year_from_text(new_url) or target_link['year']
        
        # 使用提取的年份，如果没有则使用去年的年份
        year_for_filename = extracted_year if extracted_year else last_year_str
        if extracted_year and extracted_year != last_year_str:
            print(f"⚠️  注意：从页面中提取到年份 {extracted_year}，将使用此年份")
        
        # 查找页面中的PDF下载链接
        print("\n查找页面中的PDF下载链接...")
        
        # 方法1: 查找PDF链接
        pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
        if pdf_links:
            pdf_link = pdf_links[0]
            pdf_url = pdf_link.get_attribute('href')
            if not pdf_url.startswith('http'):
                pdf_url = urljoin(new_url, pdf_url)
            print(f"✓ 找到PDF链接: {pdf_url}")
            
            # 下载PDF
            filename = f"宁夏图书馆{year_for_filename}年年报.pdf"
            success = download_pdf(pdf_url, filename, save_dir)
            if success:
                return year_for_filename
        
        # 方法2: 如果当前URL就是PDF，直接下载
        if new_url.lower().endswith('.pdf') or '.pdf' in new_url.lower():
            print(f"✓ 当前URL是PDF: {new_url}")
            filename = f"宁夏图书馆{year_for_filename}年年报.pdf"
            success = download_pdf(new_url, filename, save_dir)
            if success:
                return year_for_filename
        
        # 方法3: 查找iframe中的PDF
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            try:
                iframe_src = iframe.get_attribute('src')
                if iframe_src and '.pdf' in iframe_src.lower():
                    if not iframe_src.startswith('http'):
                        iframe_src = urljoin(new_url, iframe_src)
                    print(f"✓ 找到iframe中的PDF: {iframe_src}")
                    filename = f"宁夏图书馆{year_for_filename}年年报.pdf"
                    success = download_pdf(iframe_src, filename, save_dir)
                    if success:
                        return year_for_filename
            except:
                continue
        
        # 方法4: 查找所有下载链接
        download_keywords = ['下载', 'download', '决算', '报告']
        all_download_links = driver.find_elements(By.TAG_NAME, "a")
        for link in all_download_links:
            try:
                link_text = link.text.strip()
                link_href = link.get_attribute('href')
                
                if not link_href:
                    continue
                
                # 检查链接文本或href中是否包含下载关键词
                if any(keyword in link_text.lower() or keyword in link_href.lower() for keyword in download_keywords):
                    if not link_href.startswith('http'):
                        link_href = urljoin(new_url, link_href)
                    
                    # 检查是否是文件链接
                    if link_href.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx')):
                        print(f"✓ 找到文件链接: {link_text} -> {link_href}")
                        file_ext = os.path.splitext(link_href)[1] or '.pdf'
                        filename = f"宁夏图书馆{year_for_filename}年年报{file_ext}"
                        success = download_pdf(link_href, filename, save_dir)
                        if success:
                            return year_for_filename
            except:
                continue
        
        print("✗ 未找到PDF下载链接")
        return None
        
    except Exception as e:
        print(f"✗ 查找年报失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if driver:
            print("\n等待3秒后关闭浏览器...")
            time.sleep(3)
            driver.quit()

def main():
    """主函数"""
    print("=" * 60)
    print("宁夏图书馆年报下载工具")
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
    
    # 宁夏图书馆决算页面URL
    report_page_url = "https://whhlyt.nx.gov.cn/zwgk/fdzdgknr/yjsgk/"
    base_url = "https://whhlyt.nx.gov.cn"
    
    print(f"目标年份: {last_year}年")
    print(f"输出路径: {output_folder}")
    print("-" * 60)
    
    # 查找并下载年报
    result = find_and_download_report(report_page_url, base_url, output_folder, last_year_str)
    
    if result:
        print("\n" + "=" * 60)
        print("✓ 下载完成")
        print("=" * 60)
        print(f"文件已保存到: {output_folder}")
    else:
        print("\n" + "=" * 60)
        print("✗ 下载失败")
        print("=" * 60)

if __name__ == "__main__":
    main()

