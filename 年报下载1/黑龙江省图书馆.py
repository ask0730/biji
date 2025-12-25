# -*- coding: utf-8 -*-
"""
黑龙江省图书馆年报下载脚本
功能：从黑龙江省图书馆官网下载去年的年报，并重命名为"黑龙江省图书馆年份年报"格式
"""

import requests
import os
import time
import re
import urllib3
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Selenium相关导入（用于点击下载按钮）
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  警告: 未安装Selenium，无法点击下载按钮")
    print("  安装命令: pip install selenium")

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

def extract_year_from_url_params(url):
    """从URL参数中提取年份（特别是从filename参数）"""
    try:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        # 检查filename参数
        if 'filename' in params:
            filename = params['filename'][0]
            year = extract_year_from_text(filename)
            if year:
                return year
    except:
        pass
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

def setup_driver():
    """设置Selenium WebDriver"""
    if not SELENIUM_AVAILABLE:
        return None
    
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"✗ 启动浏览器失败: {e}")
        print("  请确保已安装Chrome浏览器和ChromeDriver")
        return None

def find_last_year_report(url, base_url):
    """在页面中查找去年的年报链接"""
    # 获取去年的年份
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    last_year_str = str(last_year)
    
    if not SELENIUM_AVAILABLE:
        print("✗ Selenium未安装，无法点击下载按钮")
        return None
    
    driver = None
    try:
        print("正在使用浏览器访问页面查找年报...")
        driver = setup_driver()
        if not driver:
            return None
        
        print(f"正在访问页面: {url}")
        driver.get(url)
        
        # 等待页面加载
        print("等待页面加载...")
        time.sleep(3)
        
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            print("  页面加载超时，继续尝试...")
        
        time.sleep(2)
        
        print(f"\n查找 {last_year} 年的年报...")
        print("  正在查找包含'黑龙江省图书馆'和去年年份的文档链接...")
        
        # 首先尝试在列表页面查找包含"图书馆"和去年年份的链接
        # 根据页面结构，链接可能在列表项中
        library_report_link = None
        library_report_text = None
        
        try:
            # 方法1: 查找包含"图书馆"和去年年份的链接
            all_links = driver.find_elements(By.XPATH, "//a[@href]")
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    title_attr = link.get_attribute('title') or ''
                    combined_text = text + ' ' + title_attr
                    
                    # 检查是否包含"图书馆"和去年年份
                    if ('图书馆' in combined_text or '图书馆' in href) and last_year_str in combined_text:
                        # 确保不是PDF链接（列表页通常不是直接PDF）
                        if not href.lower().endswith('.pdf'):
                            library_report_link = href
                            library_report_text = text or title_attr
                            print(f"✓ 找到文档链接: {library_report_text}")
                            print(f"  链接: {href}")
                            break
                except:
                    continue
        except Exception as e:
            print(f"  查找链接时出错: {e}")
        
        # 如果找到文档链接，点击进入详情页
        if library_report_link:
            try:
                print(f"\n正在访问文档详情页...")
                # 如果是相对路径，需要拼接base_url
                if library_report_link.startswith('/'):
                    detail_url = urljoin(base_url, library_report_link)
                elif not library_report_link.startswith('http'):
                    detail_url = urljoin(base_url, '/' + library_report_link)
                else:
                    detail_url = library_report_link
                
                print(f"  详情页URL: {detail_url}")
                driver.get(detail_url)
                time.sleep(3)
                
                # 等待页面加载
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except TimeoutException:
                    print("  页面加载超时，继续尝试...")
                
                time.sleep(2)
                
                # 在详情页查找PDF链接
                print("  在详情页查找PDF下载链接...")
                
                # 首先尝试直接查找PDF链接
                try:
                    pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                    for link in pdf_links:
                        try:
                            href = link.get_attribute('href')
                            text = link.text.strip()
                            if href:
                                # 如果是相对路径，转换为绝对路径
                                if href.startswith('/'):
                                    pdf_url = urljoin(base_url, href)
                                elif not href.startswith('http'):
                                    pdf_url = urljoin(detail_url, href)
                                else:
                                    pdf_url = href
                                
                                print(f"✓ 在详情页找到PDF链接: {text or pdf_url}")
                                return pdf_url, last_year_str
                        except:
                            continue
                except:
                    pass
                
                # 查找包含"下载"的链接
                try:
                    download_links = driver.find_elements(By.XPATH, "//a[contains(text(), '下载')]")
                    for link in download_links:
                        try:
                            href = link.get_attribute('href')
                            text = link.text.strip()
                            if href:
                                if href.startswith('/'):
                                    pdf_url = urljoin(base_url, href)
                                elif not href.startswith('http'):
                                    pdf_url = urljoin(detail_url, href)
                                else:
                                    pdf_url = href
                                
                                print(f"✓ 找到下载链接: {text or pdf_url}")
                                return pdf_url, last_year_str
                        except:
                            continue
                except:
                    pass
                
                # 在页面源码中查找PDF URL
                page_source = driver.page_source
                pdf_patterns = [
                    r'https?://[^\s<>"\'\)]+\.pdf',
                    r'["\']([^"\']*\.pdf)["\']',
                    r'href=["\']([^"\']*\.pdf)["\']',
                ]
                
                for pattern in pdf_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    for match in matches:
                        pdf_path = None
                        if isinstance(match, tuple):
                            pdf_path = next((m for m in match if m), None)
                        else:
                            pdf_path = match
                        
                        if pdf_path and pdf_path.lower().endswith('.pdf'):
                            if pdf_path.startswith('http'):
                                pdf_url = pdf_path
                            elif pdf_path.startswith('/'):
                                pdf_url = urljoin(base_url, pdf_path)
                            else:
                                pdf_url = urljoin(detail_url, pdf_path)
                            
                            print(f"✓ 在页面源码中找到PDF: {pdf_url}")
                            return pdf_url, last_year_str
                
            except Exception as e:
                print(f"  访问详情页失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 如果列表页直接有PDF链接，也尝试查找
        print("  尝试在列表页直接查找PDF链接...")
        try:
            pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
            for link in pdf_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    if href and last_year_str in (href + ' ' + text) and '图书馆' in (href + ' ' + text):
                        print(f"✓ 找到PDF链接: {text or href}")
                        return href, last_year_str
                except:
                    continue
        except:
            pass
        
        # 查找包含"年报"和去年年份的链接
        try:
            report_links = driver.find_elements(By.XPATH, "//a[contains(text(), '年报') or contains(text(), '决算') or contains(text(), '预算')]")
            for link in report_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    if href and last_year_str in (href + ' ' + text) and '图书馆' in (href + ' ' + text):
                        print(f"✓ 找到年报链接: {text or href}")
                        # 如果是详情页链接，需要进入详情页查找PDF
                        if not href.lower().endswith('.pdf'):
                            # 这里可以再次尝试访问详情页，但为了避免重复，先返回链接
                            return href, last_year_str
                        else:
                            return href, last_year_str
                except:
                    continue
        except:
            pass
        
        # 查找下载相关的元素
        download_elements = []
        
        # 1. 查找包含"下载"文本的元素
        try:
            download_text_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '下载')]")
            for element in download_text_elements:
                try:
                    text = element.text.strip()
                    if '下载' in text and last_year_str in text:
                        download_elements.append({
                            'element': element,
                            'text': text,
                            'type': 'text'
                        })
                except:
                    continue
        except:
            pass
        
        # 2. 查找包含"点击下载"的元素
        try:
            click_download_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '点击下载')]")
            for element in click_download_elements:
                try:
                    text = element.text.strip()
                    if '点击下载' in text:
                        download_elements.append({
                            'element': element,
                            'text': text,
                            'type': 'click_download'
                        })
                except:
                    continue
        except:
            pass
        
        # 3. 查找所有a标签中包含"下载"的链接
        try:
            download_links = driver.find_elements(By.XPATH, "//a[contains(text(), '下载')]")
            for link in download_links:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')
                    if '下载' in text:
                        download_elements.append({
                            'element': link,
                            'text': text,
                            'href': href,
                            'type': 'link'
                        })
                except:
                    continue
        except:
            pass
        
        # 4. 查找button标签中包含"下载"的按钮
        try:
            download_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '下载')]")
            for button in download_buttons:
                try:
                    text = button.text.strip()
                    if '下载' in text:
                        download_elements.append({
                            'element': button,
                            'text': text,
                            'type': 'button'
                        })
                except:
                    continue
        except:
            pass
        
        if download_elements:
            print(f"  找到 {len(download_elements)} 个下载相关元素")
            for i, elem_info in enumerate(download_elements[:5]):
                try:
                    location = elem_info['element'].location
                    print(f"    {i+1}. {elem_info['text'][:50]} | 类型: {elem_info['type']} | Y坐标: {location['y']}")
                except:
                    print(f"    {i+1}. {elem_info['text'][:50]} | 类型: {elem_info['type']}")
        
        # 优先选择包含去年年份的元素
        year_elements = [e for e in download_elements if last_year_str in e.get('text', '')]
        if year_elements:
            download_elements = year_elements
        
        # 优先选择"点击下载"类型的元素，并按Y坐标排序（最下面的优先）
        click_download_elements = [e for e in download_elements if e.get('type') == 'click_download']
        if click_download_elements:
            print(f"  找到 {len(click_download_elements)} 个'点击下载'元素")
            # 按Y坐标排序，Y坐标最大的（最下面的）优先
            try:
                click_download_elements.sort(key=lambda x: x['element'].location['y'], reverse=True)
                bottom_element = click_download_elements[0]
                print(f"  选择最下面的'点击下载'按钮（Y坐标: {bottom_element['element'].location['y']}）")
                print(f"  文本: {bottom_element['text'][:50]}")
                download_elements = [bottom_element]
            except Exception as e:
                print(f"  获取元素位置失败: {e}，使用第一个'点击下载'元素")
                download_elements = [click_download_elements[0]]
        else:
            # 如果没有"点击下载"，按Y坐标排序所有下载元素，选择最下面的
            try:
                download_elements.sort(key=lambda x: x['element'].location['y'], reverse=True)
                print(f"  未找到'点击下载'，选择最下面的下载元素（Y坐标: {download_elements[0]['element'].location['y']}）")
                download_elements = [download_elements[0]]  # 只点击最下面的
            except:
                print(f"  无法获取元素位置，使用第一个下载元素")
                if download_elements:
                    download_elements = [download_elements[0]]  # 只点击第一个
        
        # 尝试点击下载元素
        for elem_info in download_elements:
            try:
                element = elem_info['element']
                text = elem_info['text']
                
                # 检查元素是否可见
                if not element.is_displayed():
                    continue
                
                print(f"  尝试点击: {text[:50]}")
                
                # 滚动到元素可见
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(1)
                
                # 保存当前窗口句柄
                current_window = driver.current_window_handle
                windows_before = driver.window_handles
                
                # 尝试点击
                try:
                    element.click()
                except:
                    # 如果普通点击失败，使用JavaScript点击
                    driver.execute_script("arguments[0].click();", element)
                
                # 等待页面响应
                time.sleep(3)
                
                # 检查是否有新窗口打开
                windows_after = driver.window_handles
                if len(windows_after) > len(windows_before):
                    # 切换到新窗口
                    new_window = [w for w in windows_after if w not in windows_before][0]
                    driver.switch_to.window(new_window)
                    print("  检测到新窗口打开")
                
                # 检查当前URL是否是PDF
                current_url = driver.current_url
                print(f"  当前URL: {current_url}")
                
                # 检查URL是否是PDF
                if current_url.lower().endswith('.pdf') or '.pdf' in current_url.lower():
                    print(f"✓ 找到PDF链接: {current_url}")
                    return current_url, last_year_str
                
                # 检查页面内容类型
                try:
                    content_type = driver.execute_script("return document.contentType || ''")
                    if 'pdf' in content_type.lower():
                        print(f"✓ 页面内容是PDF")
                        return current_url, last_year_str
                except:
                    pass
                
                # 在新页面中查找PDF链接
                try:
                    pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                    if pdf_links:
                        pdf_url = pdf_links[0].get_attribute('href')
                        print(f"✓ 在新页面找到PDF链接: {pdf_url}")
                        return pdf_url, last_year_str
                except:
                    pass
                
                # 在页面源码中查找PDF URL
                page_source = driver.page_source
                pdf_patterns = [
                    r'https?://[^\s<>"\'\)]+\.pdf',
                    r'["\']([^"\']*\.pdf)["\']',
                    r'href=["\']([^"\']*\.pdf)["\']',
                ]
                
                for pattern in pdf_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    for match in matches:
                        pdf_path = None
                        if isinstance(match, tuple):
                            pdf_path = next((m for m in match if m), None)
                        else:
                            pdf_path = match
                        
                        if pdf_path and pdf_path.lower().endswith('.pdf'):
                            if pdf_path.startswith('http'):
                                pdf_url = pdf_path
                            elif pdf_path.startswith('/'):
                                base_url_parsed = urlparse(url)
                                pdf_url = f"{base_url_parsed.scheme}://{base_url_parsed.netloc}{pdf_path}"
                            else:
                                pdf_url = urljoin(current_url, pdf_path)
                            
                            # 检查是否包含去年年份
                            if last_year_str in pdf_url:
                                print(f"✓ 在页面源码中找到PDF: {pdf_url}")
                                return pdf_url, last_year_str
                
                # 如果点击后URL变化了，检查新URL
                if current_url != url:
                    # 检查是否是下载接口
                    if 'download' in current_url.lower() or 'file' in current_url.lower():
                        print(f"✓ 找到下载接口: {current_url}")
                        return current_url, last_year_str
                
                # 如果打开了新窗口，切换回原窗口继续尝试
                if len(windows_after) > len(windows_before):
                    driver.close()
                    driver.switch_to.window(current_window)
                
            except Exception as e:
                print(f"  点击元素失败: {e}")
                continue
        
        # 如果点击没找到，尝试直接查找页面中的PDF链接（包含去年年份）
        print("  点击下载按钮未找到PDF，尝试直接查找页面中的PDF链接...")
        try:
            pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
            for link in pdf_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    if href and last_year_str in (href + ' ' + text):
                        print(f"✓ 找到PDF链接: {text or href}")
                        return href, last_year_str
                except:
                    continue
        except:
            pass
        
        # 尝试查找所有包含年份的链接
        try:
            all_links = driver.find_elements(By.XPATH, "//a[@href]")
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    if href and last_year_str in (href + ' ' + text):
                        # 检查是否是文档链接
                        if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx']):
                            print(f"✓ 找到文档链接: {text or href}")
                            return href, last_year_str
                except:
                    continue
        except:
            pass
        
        print("✗ 未找到年报PDF链接")
        return None
        
    except Exception as e:
        print(f"✗ 查找年报链接失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def download_pdf(url, filename, save_dir):
    """下载文件（支持PDF、DOCX、DOC等格式）"""
    try:
        session = requests.Session()
        session.headers.update(get_headers())
        
        print(f"正在下载: {url}")
        response = session.get(url, stream=True, timeout=60, verify=False)
        response.raise_for_status()
        
        # 检查内容类型和文件扩展名
        content_type = response.headers.get('Content-Type', '').lower()
        url_lower = url.lower()
        
        # 检查是否是HTML文件，如果是则拒绝下载
        if 'text/html' in content_type or url_lower.endswith(('.htm', '.html')):
            print(f"✗ 错误: URL指向的是HTML页面，不是文档文件")
            print(f"  请检查页面中是否有PDF/DOCX/DOC文档链接")
            return False
        
        # 根据URL确定文件扩展名
        if url_lower.endswith('.docx'):
            file_ext = '.docx'
        elif url_lower.endswith('.doc'):
            file_ext = '.doc'
        elif url_lower.endswith('.pdf'):
            file_ext = '.pdf'
        else:
            # 根据Content-Type判断
            if 'word' in content_type or 'document' in content_type:
                if 'openxml' in content_type or 'docx' in content_type:
                    file_ext = '.docx'
                else:
                    file_ext = '.doc'
            elif 'pdf' in content_type:
                file_ext = '.pdf'
            else:
                file_ext = '.pdf'  # 默认使用pdf
        
        # 确保文件名有正确的扩展名
        if not filename.lower().endswith(('.pdf', '.docx', '.doc')):
            filename = filename + file_ext
        elif not filename.lower().endswith(file_ext):
            # 如果扩展名不匹配，替换为正确的扩展名
            filename = os.path.splitext(filename)[0] + file_ext
        
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
    print("黑龙江省图书馆年报下载工具")
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
    
    # 黑龙江省图书馆年报页面URL
    report_page_url = "https://wlt.hlj.gov.cn/wlt/c114205/zfxxgk.shtml?tab=zdgknr"
    base_url = "https://wlt.hlj.gov.cn"
    
    print(f"目标年份: {last_year}年")
    print(f"输出路径: {output_folder}")
    print("-" * 60)
    
    # 查找年报链接
    result = find_last_year_report(report_page_url, base_url)
    
    if not result:
        print("\n✗ 未找到年报链接，下载失败")
        return
    
    # 处理返回值：可能是(url, year)元组或只有url
    if isinstance(result, tuple):
        file_url, actual_year = result
        if actual_year and actual_year != last_year_str:
            print(f"⚠️  注意：找到的是 {actual_year} 年的年报，不是 {last_year_str} 年的")
            year_for_filename = actual_year
        else:
            year_for_filename = last_year_str
    else:
        file_url = result
        year_for_filename = last_year_str
    
    # 生成文件名，使用实际找到的年份
    if file_url.lower().endswith('.docx'):
        file_ext = '.docx'
    elif file_url.lower().endswith('.doc'):
        file_ext = '.doc'
    elif file_url.lower().endswith('.pdf'):
        file_ext = '.pdf'
    else:
        file_ext = '.pdf'  # 默认使用pdf
    
    filename = f"黑龙江省图书馆{year_for_filename}年年报{file_ext}"
    filename = clean_filename(filename)
    
    print(f"\n文件名: {filename}")
    print("-" * 60)
    
    # 下载文件
    success = download_pdf(file_url, filename, output_folder)
    
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

