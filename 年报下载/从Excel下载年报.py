#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从Excel文件读取图书馆信息，下载去年的年报，并更新Excel
"""

import os
import re
import time
import random
import pandas as pd
import requests
from urllib.parse import urlparse, urljoin
from datetime import datetime
from bs4 import BeautifulSoup

# 尝试导入PDF验证库
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    try:
        import fitz  # PyMuPDF
        HAS_PYMUPDF = True
    except ImportError:
        HAS_PYMUPDF = False
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_headers():
    """获取请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def setup_driver():
    """设置浏览器驱动"""
    try:
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        print(f"浏览器启动失败: {e}")
        raise

def get_last_year():
    """获取去年的年份"""
    return datetime.now().year - 1

def find_report_links(soup, base_url, target_year):
    """在HTML中查找指定年份的年报链接"""
    report_links = []
    target_year_str = str(target_year)
    
    # 方法1: 查找所有链接，筛选包含目标年份和年报相关的
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text().strip()
        
        # 构建完整URL
        full_url = urljoin(base_url, href)
        
        # 检查是否包含目标年份
        has_year = target_year_str in href or target_year_str in text
        
        # 检查是否与年报相关
        is_report = any(keyword in text.lower() or keyword in href.lower() 
                       for keyword in ['年报', '年度报告', 'annual', 'report', '年度'])
        
        # 检查是否是文件链接
        is_file = any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'])
        
        if has_year and (is_report or is_file):
            report_links.append({
                'url': full_url,
                'text': text,
                'type': 'direct_link'
            })
    
    # 方法2: 查找包含年份的文本，然后查找附近的链接
    for element in soup.find_all(['div', 'li', 'td', 'tr', 'p', 'span']):
        text = element.get_text()
        if target_year_str in text and ('年报' in text or '年度' in text or '报告' in text):
            # 在这个元素内查找链接
            links = element.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                full_url = urljoin(base_url, href)
                if full_url not in [r['url'] for r in report_links]:
                    report_links.append({
                        'url': full_url,
                        'text': link.get_text().strip() or text[:50],
                        'type': 'nearby_link'
                    })
    
    # 方法3: 查找所有文件链接，检查文件名是否包含目标年份
    for link in soup.find_all('a', href=True):
        href = link.get('href', '').lower()
        if any(ext in href for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']):
            full_url = urljoin(base_url, link.get('href', ''))
            if target_year_str in full_url.lower():
                if full_url not in [r['url'] for r in report_links]:
                    report_links.append({
                        'url': full_url,
                        'text': link.get_text().strip(),
                        'type': 'file_link'
                    })
    
    # 去重
    seen_urls = set()
    unique_links = []
    for link in report_links:
        if link['url'] not in seen_urls:
            seen_urls.add(link['url'])
            unique_links.append(link)
    
    return unique_links

def find_report_links_selenium(driver, page_url, target_year):
    """使用Selenium在页面中查找年报链接"""
    try:
        driver.get(page_url)
        time.sleep(3)  # 等待页面加载
        
        # 等待页面加载完成
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            pass
        
        # 获取页面源码
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        return find_report_links(soup, page_url, target_year)
        
    except Exception as e:
        print(f"  ❌ 访问页面失败: {e}")
        return []

def find_report_links_requests(page_url, target_year):
    """使用requests在页面中查找年报链接"""
    try:
        session = requests.Session()
        session.headers.update(get_headers())
        
        response = session.get(page_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        return find_report_links(soup, page_url, target_year)
        
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return []

def get_file_extension_from_url(url):
    """从URL获取文件扩展名"""
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    if path.endswith('.pdf'):
        return 'pdf'
    elif path.endswith('.doc'):
        return 'doc'
    elif path.endswith('.docx'):
        return 'docx'
    elif path.endswith('.xls'):
        return 'xls'
    elif path.endswith('.xlsx'):
        return 'xlsx'
    elif path.endswith('.ppt'):
        return 'ppt'
    elif path.endswith('.pptx'):
        return 'pptx'
    elif path.endswith('.html') or path.endswith('.htm'):
        return 'html'
    
    return 'pdf'  # 默认

def clean_filename(filename):
    """清理文件名"""
    invalid_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(invalid_chars, '_', filename)
    cleaned = cleaned.strip(' .')
    if not cleaned:
        cleaned = "unnamed_file"
    return cleaned

def validate_file(file_path):
    """校验文件是否可以正常打开"""
    if not os.path.exists(file_path):
        return False, "文件不存在"
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # 校验PDF文件
    if file_ext == '.pdf':
        # 方法1: 使用PyPDF2
        if HAS_PYPDF2:
            try:
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    if len(pdf_reader.pages) == 0:
                        return False, "PDF文件没有页面"
                    # 尝试读取第一页
                    first_page = pdf_reader.pages[0]
                    text = first_page.extract_text()
                    return True, "PDF文件正常"
            except Exception as e:
                return False, f"PDF文件损坏: {str(e)}"
        
        # 方法2: 使用PyMuPDF
        elif HAS_PYMUPDF:
            try:
                doc = fitz.open(file_path)
                if doc.page_count == 0:
                    doc.close()
                    return False, "PDF文件没有页面"
                # 尝试读取第一页
                first_page = doc[0]
                text = first_page.get_text()
                doc.close()
                return True, "PDF文件正常"
            except Exception as e:
                return False, f"PDF文件损坏: {str(e)}"
        
        # 方法3: 简单校验（检查文件头）
        else:
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(4)
                    if header == b'%PDF':
                        # 检查文件大小是否合理
                        file_size = os.path.getsize(file_path)
                        if file_size < 1024:
                            return False, "PDF文件大小异常小"
                        return True, "PDF文件格式正确"
                    else:
                        return False, "不是有效的PDF文件"
            except Exception as e:
                return False, f"读取文件失败: {str(e)}"
    
    # 校验其他文件类型（简单检查文件大小）
    else:
        file_size = os.path.getsize(file_path)
        if file_size < 1024:
            return False, "文件大小异常小"
        return True, "文件大小正常"

def save_html_as_pdf(url, filename, save_dir, library_name):
    """使用Selenium将HTML页面完整保存为PDF（包含图片等资源）"""
    driver = None
    try:
        print(f"    正在使用Selenium访问HTML页面...")
        driver = setup_driver()
        
        # 访问页面
        driver.get(url)
        
        # 等待页面完全加载（包括图片）
        print(f"    等待页面完全加载...")
        time.sleep(5)  # 基础等待
        
        # 等待所有图片加载完成
        try:
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            # 额外等待图片加载
            time.sleep(3)
            
            # 滚动页面确保所有内容加载
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
        except:
            print(f"    ⚠️ 页面加载超时，继续保存...")
        
        # 确保文件名是PDF
        filename = clean_filename(filename)
        if not filename.lower().endswith('.pdf'):
            filename = re.sub(r'\.[^.]+$', '', filename)
            filename = f"{filename}.pdf"
        
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)
        
        # 如果文件已存在，先删除
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        
        # 使用Chrome的打印功能保存为PDF
        print(f"    正在将页面保存为PDF...")
        
        # 设置打印选项
        print_options = {
            'printBackground': True,  # 包含背景图片和颜色
            'paperWidth': 8.27,  # A4宽度（英寸）
            'paperHeight': 11.69,  # A4高度（英寸）
            'marginTop': 0.4,
            'marginBottom': 0.4,
            'marginLeft': 0.4,
            'marginRight': 0.4,
        }
        
        # 执行打印命令
        result = driver.execute_cdp_cmd('Page.printToPDF', print_options)
        
        # 保存PDF
        import base64
        pdf_data = base64.b64decode(result['data'])
        
        with open(file_path, 'wb') as f:
            f.write(pdf_data)
        
        # 验证文件
        if not os.path.exists(file_path):
            print(f"    ❌ PDF保存失败")
            return False
        
        file_size = os.path.getsize(file_path)
        
        if file_size < 1024:
            print(f"    ⚠️ 文件大小异常小 ({file_size} 字节)，可能是错误页面")
            os.remove(file_path)
            return False
        
        print(f"    ✅ PDF保存成功: {filename}")
        print(f"       文件大小: {file_size:,} 字节 ({file_size/1024/1024:.2f} MB)")
        
        return True, file_path
        
    except Exception as e:
        print(f"    ❌ 保存HTML为PDF失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def download_file(url, filename, save_dir, library_name, check_html_pdf=True):
    """下载文件
    Args:
        url: 文件URL
        filename: 文件名
        save_dir: 保存目录
        library_name: 图书馆名称
        check_html_pdf: 是否检查HTML页面中的PDF链接（避免递归时重复检查）
    """
    try:
        session = requests.Session()
        session.headers.update(get_headers())
        
        print(f"    正在下载: {url[:80]}...")
        
        # 先检查是否是HTML页面
        is_html_page = False
        try:
            head_response = session.head(url, timeout=30, allow_redirects=True)
            content_type = head_response.headers.get('Content-Type', '').lower()
            
            if 'text/html' in content_type:
                is_html_page = True
        except:
            # HEAD请求失败，检查URL扩展名
            if url.lower().endswith(('.html', '.htm')):
                is_html_page = True
        
        # 如果是HTML页面，先尝试查找其中的PDF下载链接
        if is_html_page and check_html_pdf:
            print(f"    ⚠️ URL指向HTML页面，先查找其中的PDF下载链接...")
            
            # 使用Selenium访问页面，查找PDF链接
            driver = None
            try:
                driver = setup_driver()
                driver.get(url)
                time.sleep(3)  # 等待页面加载
                
                # 等待页面加载完成
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except TimeoutException:
                    pass
                
                # 获取页面源码
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # 查找所有PDF链接
                pdf_links = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    full_url = urljoin(url, href)
                    
                    # 检查是否是PDF链接
                    if '.pdf' in href.lower() or '.pdf' in full_url.lower():
                        # 检查是否包含年份或年报相关关键词
                        if str(get_last_year()) in text or '年报' in text or '年度' in text or '报告' in text:
                            pdf_links.append({
                                'url': full_url,
                                'text': text
                            })
                
                # 如果找到PDF链接，尝试下载第一个
                if pdf_links:
                    print(f"    ✅ 在HTML页面中找到 {len(pdf_links)} 个PDF下载链接")
                    pdf_url = pdf_links[0]['url']
                    print(f"    尝试下载PDF: {pdf_url[:80]}...")
                    
                    # 递归调用download_file下载PDF（设置check_html_pdf=False避免重复检查）
                    result, file_path = download_file(pdf_url, filename, save_dir, library_name, check_html_pdf=False)
                    if result and file_path:
                        return result, file_path
                    else:
                        print(f"    ❌ PDF链接下载失败")
                        return False, None
                else:
                    print(f"    ❌ HTML页面中未找到PDF链接")
                    return False, None
                
            except Exception as e:
                print(f"    ❌ 查找PDF链接失败: {e}")
                return False, None
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
        
        # 下载文件
        print(f"    正在连接服务器...")
        response = session.get(url, stream=True, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        # 获取文件大小（如果可用）
        total_size = int(response.headers.get('Content-Length', 0))
        if total_size > 0:
            total_size_mb = total_size / 1024 / 1024
            print(f"    文件大小: {total_size_mb:.2f} MB")
        
        # 确定文件扩展名
        file_ext = get_file_extension_from_url(url)
        content_type = response.headers.get('Content-Type', '').lower()
        
        # 如果下载的是HTML，使用Selenium保存为PDF
        if 'text/html' in content_type or file_ext == 'html':
            print(f"    ⚠️ 下载的文件是HTML，将转换为PDF...")
            # 先保存HTML到临时文件
            temp_html_path = os.path.join(save_dir, f"temp_{int(time.time())}.html")
            with open(temp_html_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 使用Selenium转换为PDF
            result, file_path = save_html_as_pdf(f"file:///{temp_html_path.replace(os.sep, '/')}", filename, save_dir, library_name)
            
            # 删除临时HTML文件
            try:
                if os.path.exists(temp_html_path):
                    os.remove(temp_html_path)
            except:
                pass
            
            return result, file_path
        
        if 'pdf' in content_type:
            file_ext = 'pdf'
        elif 'msword' in content_type or 'wordprocessingml' in content_type:
            file_ext = 'docx' if 'openxml' in content_type else 'doc'
        elif 'spreadsheetml' in content_type:
            file_ext = 'xlsx' if 'openxml' in content_type else 'xls'
        elif 'presentationml' in content_type:
            file_ext = 'pptx' if 'openxml' in content_type else 'ppt'
        
        # 确保文件名有正确的扩展名
        if not filename.lower().endswith(f'.{file_ext}'):
            filename = re.sub(r'\.[^.]+$', '', filename)
            filename = f"{filename}.{file_ext}"
        
        filename = clean_filename(filename)
        
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)
        
        # 如果文件已存在，先删除
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        
        # 保存文件并显示进度
        print(f"    开始下载...")
        downloaded_size = 0
        start_time = time.time()
        last_print_time = start_time
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    # 每0.5秒更新一次进度显示
                    current_time = time.time()
                    if current_time - last_print_time >= 0.5:
                        if total_size > 0:
                            percent = (downloaded_size / total_size) * 100
                            speed = downloaded_size / (current_time - start_time) / 1024  # KB/s
                            print(f"    进度: {percent:.1f}% ({downloaded_size/1024/1024:.2f} MB / {total_size/1024/1024:.2f} MB) - 速度: {speed:.1f} KB/s", end='\r')
                        else:
                            speed = downloaded_size / (current_time - start_time) / 1024  # KB/s
                            print(f"    已下载: {downloaded_size/1024/1024:.2f} MB - 速度: {speed:.1f} KB/s", end='\r')
                        last_print_time = current_time
        
        # 下载完成，换行
        print()  # 换行
        
        # 验证文件
        if not os.path.exists(file_path):
            print(f"    ❌ 文件保存失败")
            return False
        
        file_size = os.path.getsize(file_path)
        
        if file_size < 1024:
            print(f"    ⚠️ 文件大小异常小 ({file_size} 字节)，可能是错误页面")
            os.remove(file_path)
            return False
        
        print(f"    ✅ 下载成功: {filename}")
        print(f"       文件类型: {file_ext.upper()}")
        print(f"       文件大小: {file_size:,} 字节 ({file_size/1024/1024:.2f} MB)")
        
        return True, file_path
        
    except Exception as e:
        print(f"    ❌ 下载失败: {e}")
        return False, None

def process_library_row(row, library_name_col, url_col, save_dir, target_year):
    """处理Excel中的一行数据"""
    library_name = str(row[library_name_col]).strip()
    page_url = str(row[url_col]).strip()
    
    # 跳过空值（只检查图书馆名称）
    if pd.isna(row[library_name_col]) or library_name == 'nan' or not library_name:
        return False, None, None
    
    # 地址为空也要处理，不跳过
    if pd.isna(row[url_col]) or page_url == 'nan' or not page_url:
        print(f"\n⚠️ {library_name}: 年报地址为空，将标记为失败")
        return False, None, None
    
    print(f"\n{'='*60}")
    print(f"处理: {library_name}")
    print(f"年报地址: {page_url}")
    print(f"{'='*60}")
    
    # 先尝试使用requests
    report_links = find_report_links_requests(page_url, target_year)
    
    # 如果requests失败或没找到链接，使用Selenium
    if not report_links:
        print("  使用Selenium访问页面...")
        driver = setup_driver()
        try:
            report_links = find_report_links_selenium(driver, page_url, target_year)
        finally:
            driver.quit()
    
    if not report_links:
        print(f"  ⚠️ 未找到{target_year}年年报链接")
        return False, None, None
    
    print(f"  ✅ 找到 {len(report_links)} 个可能的年报链接")
    
    # 下载找到的链接
    success = False
    downloaded_url = None
    downloaded_file_path = None
    for i, link_info in enumerate(report_links, 1):
        url = link_info['url']
        link_text = link_info['text']
        
        print(f"\n  尝试下载链接 {i}/{len(report_links)}:")
        print(f"    文本: {link_text[:50]}...")
        
        # 生成文件名
        filename = f"{library_name}{target_year}年年报"
        
        result, file_path = download_file(url, filename, save_dir, library_name)
        if result and file_path:
            success = True
            downloaded_url = url  # 记录成功下载的URL
            downloaded_file_path = file_path  # 记录文件路径
            break  # 成功下载一个就够了
        else:
            print(f"    ⚠️ 该链接下载失败，尝试下一个...")
    
    return success, downloaded_url, downloaded_file_path

def load_config():
    """加载配置文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.txt")
    config = {}
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        except Exception as e:
            print(f"⚠️ 读取配置文件失败: {e}")
    
    return config

def main():
    """主函数"""
    print("=" * 60)
    print("从Excel下载图书馆年报工具")
    print("=" * 60)
    
    # 自动获取Excel文件路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 查找当前目录下的Excel文件
    excel_files = [f for f in os.listdir(script_dir) if f.endswith(('.xlsx', '.xls'))]
    if excel_files:
        # 自动使用第一个Excel文件
        excel_file = excel_files[0]
        excel_file = os.path.join(script_dir, excel_file)
        print(f"\n📄 自动使用Excel文件: {os.path.basename(excel_file)}")
    else:
        print("❌ 当前目录下未找到Excel文件")
        return
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel文件不存在: {excel_file}")
        return
    
    print(f"\n📄 Excel文件: {excel_file}")
    
    # 读取Excel文件
    try:
        df = pd.read_excel(excel_file, engine='openpyxl')
        print(f"✅ 成功读取Excel文件，共 {len(df)} 行数据")
        print(f"   列名: {list(df.columns)}")
    except Exception as e:
        print(f"❌ 读取Excel文件失败: {e}")
        return
    
    # 确定列名
    print(f"\n请确认列名:")
    library_name_col = None
    url_col = None
    
    # 自动识别列名
    for col in df.columns:
        col_lower = str(col).lower()
        if '图书馆' in str(col) or '名称' in col_lower or 'name' in col_lower:
            library_name_col = col
        elif '地址' in str(col) or 'url' in col_lower or '链接' in str(col) or '年报' in str(col):
            url_col = col
    
    if not library_name_col:
        print(f"\n可用列: {list(df.columns)}")
        library_name_col = input("请输入图书馆名称列名: ").strip()
    
    if not url_col:
        print(f"\n可用列: {list(df.columns)}")
        url_col = input("请输入年报地址列名: ").strip()
    
    if library_name_col not in df.columns or url_col not in df.columns:
        print(f"❌ 列名不正确")
        return
    
    print(f"\n✅ 使用列:")
    print(f"   图书馆名称: {library_name_col}")
    print(f"   年报地址: {url_col}")
    
    # 智能识别状态列（优先查找包含"是否"、"下载"、"状态"的列）
    status_col = None
    status_keywords = ['是否', '下载', '状态', '是否下载', '下载状态']
    
    # 方法1: 查找包含关键词的列
    for col in df.columns:
        col_str = str(col)
        if col_str != library_name_col and col_str != url_col:
            for keyword in status_keywords:
                if keyword in col_str:
                    status_col = col
                    print(f"✅ 自动识别状态列: {status_col}")
                    break
            if status_col:
                break
    
    # 方法2: 如果没找到，使用最后一列
    if not status_col:
        last_col_name = df.columns[-1]
        if last_col_name != library_name_col and last_col_name != url_col:
            status_col = last_col_name
            print(f"✅ 使用最后一列作为状态列: {status_col}")
        else:
            # 如果最后一列是数据列，添加新列
            df['下载状态'] = ''
            status_col = '下载状态'
            print(f"✅ 创建新状态列: {status_col}")
    
    print(f"   状态列: {status_col}")
    
    # 确保状态列是字符串类型（避免类型转换错误）
    df[status_col] = df[status_col].astype(str)
    # 将'nan'字符串替换为空字符串
    df[status_col] = df[status_col].replace('nan', '')
    
    # 添加年报下载地址列
    report_url_col = '年报下载地址'
    if report_url_col not in df.columns:
        df[report_url_col] = ''
        print(f"✅ 已添加新列: {report_url_col}")
    else:
        print(f"✅ 使用已有列: {report_url_col}")
    
    # 确保年报下载地址列是字符串类型
    df[report_url_col] = df[report_url_col].astype(str)
    df[report_url_col] = df[report_url_col].replace('nan', '')
    
    # 加载配置
    config = load_config()
    output_folder = config.get("output_folder", "").strip()
    if output_folder:
        save_dir = output_folder
    else:
        save_dir = os.path.join(script_dir, "下载的年报")
    
    print(f"\n📁 保存目录: {save_dir}")
    os.makedirs(save_dir, exist_ok=True)
    
    target_year = get_last_year()
    print(f"\n📅 目标年份: {target_year}年（去年）")
    print("=" * 60)
    
    # 处理每一行
    success_count = 0
    fail_count = 0
    already_done_count = 0
    
    for index, row in df.iterrows():
        library_name = str(row[library_name_col]).strip()
        
        # 检查下载状态，如果状态为"是"则跳过，否则抓取
        current_status = str(row[status_col]).strip()
        # 处理可能的特殊情况：去除所有空白字符，统一大小写
        current_status_clean = current_status.replace(' ', '').replace('\t', '').replace('\n', '')
        
        # 调试信息：显示读取到的状态值
        if index < 3:  # 只显示前3行的调试信息
            print(f"\n[调试] 第{index+1}行 - 图书馆: {library_name}, 状态列: '{status_col}', 状态值: '{current_status}' (清理后: '{current_status_clean}')")
        
        # 如果状态为"是"（考虑各种可能的格式），跳过
        if current_status_clean == '是' or current_status_clean.lower() == 'yes' or current_status_clean == '1':
            print(f"\n⏭️  跳过: {library_name}（状态为'是'，已下载）")
            already_done_count += 1
            continue
        
        # 状态为"否"、空值或其他，都进行抓取
        print(f"\n📥 开始处理: {library_name}（状态: '{current_status if current_status else '空'}）")
        
        try:
            result, downloaded_url, downloaded_file_path = process_library_row(row, library_name_col, url_col, save_dir, target_year)
            if result and downloaded_file_path:
                # 校验文件是否可以正常打开
                print(f"  🔍 正在校验文件...")
                is_valid, validation_msg = validate_file(downloaded_file_path)
                
                if is_valid:
                    print(f"  ✅ 文件校验通过: {validation_msg}")
                    df.at[index, status_col] = '是'
                    if downloaded_url:
                        df.at[index, report_url_col] = downloaded_url
                    success_count += 1
                else:
                    print(f"  ❌ 文件校验失败: {validation_msg}")
                    # 删除损坏的文件
                    try:
                        if os.path.exists(downloaded_file_path):
                            os.remove(downloaded_file_path)
                            print(f"  🗑️  已删除损坏的文件: {os.path.basename(downloaded_file_path)}")
                    except Exception as e:
                        print(f"  ⚠️ 删除文件失败: {e}")
                    # 更新状态为"否"
                    df.at[index, status_col] = '否'
                    df.at[index, report_url_col] = ''
                    print(f"  📝 已将状态更新为'否'")
                    fail_count += 1
                    
                    # 立即保存Excel，确保状态更新被保存
                    try:
                        df.to_excel(excel_file, index=False, engine='openpyxl')
                        print(f"  💾 已保存状态更新到Excel")
                    except Exception as e:
                        print(f"  ⚠️ 保存Excel失败: {e}")
            elif result:
                # 下载成功但没有文件路径（不应该发生）
                print(f"  ⚠️ 下载成功但未返回文件路径")
                df.at[index, status_col] = '否'
                df.at[index, report_url_col] = ''
                fail_count += 1
            else:
                # 下载失败，更新状态为"否"
                page_url = str(row[url_col]).strip()
                df.at[index, status_col] = '否'
                df.at[index, report_url_col] = ''  # 失败时清空地址
                if pd.isna(row[url_col]) or page_url == 'nan' or not page_url:
                    print(f"  ⚠️ 年报地址为空，已标记为'否'")
                else:
                    print(f"  ❌ 下载失败，已标记为'否'")
                fail_count += 1
                
                # 立即保存Excel，确保状态更新被保存
                try:
                    df.to_excel(excel_file, index=False, engine='openpyxl')
                    print(f"  💾 已保存状态更新到Excel")
                except Exception as e:
                    print(f"  ⚠️ 保存Excel失败: {e}")
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            df.at[index, status_col] = '否'
            df.at[index, report_url_col] = ''  # 失败时清空地址
            fail_count += 1
        
        # 每个图书馆之间稍作延迟
        time.sleep(2)
        
        # 每处理5个保存一次（防止数据丢失）
        if (index + 1) % 5 == 0:
            try:
                df.to_excel(excel_file, index=False, engine='openpyxl')
                print(f"\n💾 已保存进度到Excel文件（已处理 {index + 1}/{len(df)} 行）")
            except Exception as e:
                print(f"⚠️ 保存Excel失败: {e}")
    
    # 最终保存
    try:
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"\n✅ Excel文件已更新并保存")
    except Exception as e:
        print(f"❌ 保存Excel文件失败: {e}")
    
    # 输出统计
    print("\n" + "=" * 60)
    print("下载完成")
    print("=" * 60)
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {fail_count} 个（包括地址为空的情况）")
    print(f"✓ 已存在: {already_done_count} 个（状态为'是'，已跳过）")
    print(f"📊 总计: {len(df)} 个")
    print(f"📁 文件保存在: {save_dir}")
    print(f"📄 Excel文件已更新: {excel_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()

