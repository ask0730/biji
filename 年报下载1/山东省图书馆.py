# -*- coding: utf-8 -*-
"""
山东省图书馆年报下载脚本
功能：从山东省图书馆官网下载去年的年报，并重命名为"山东省图书馆年份年报"格式
"""

import requests
import os
import time
import re
import urllib3
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from io import BytesIO

# 用于将截图转换为PDF
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  警告: 未安装Pillow，无法将截图转换为PDF")
    print("  安装命令: pip install Pillow")

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
        # 抑制DNS和其他警告
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"✗ 启动浏览器失败: {e}")
        print("  请确保已安装Chrome浏览器和ChromeDriver")
        return None

def save_page_as_pdf(driver, save_path):
    """将页面截图保存为PDF"""
    try:
        if not PIL_AVAILABLE:
            print("✗ 无法保存为PDF：未安装Pillow库")
            return False
        
        print("  正在截图页面...")
        
        # 滚动到顶部
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.2)
        
        # 获取页面总高度和视口高度
        total_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
        viewport_height = driver.execute_script("return window.innerHeight")
        viewport_width = driver.execute_script("return window.innerWidth")
        
        print(f"  页面总高度: {total_height}px，视口高度: {viewport_height}px")
        
        # 如果页面高度超过视口高度，需要滚动截图
        if total_height > viewport_height:
            print(f"  需要滚动截图，预计 {((total_height + viewport_height - 1) // viewport_height)} 张截图...")
            
            # 滚动并拼接截图（避免重叠）
            images = []
            scroll_position = 0
            screenshot_count = 0
            
            while scroll_position < total_height:
                # 滚动到当前位置
                driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                time.sleep(0.3)  # 减少等待时间，只等待基本渲染
                
                # 截图
                screenshot = driver.get_screenshot_as_png()
                img = Image.open(BytesIO(screenshot))
                images.append(img)
                screenshot_count += 1
                print(f"    已截图 {screenshot_count} 张...", end='\r', flush=True)
                
                # 更新滚动位置（每次滚动视口高度的90%，避免完全重叠）
                scroll_position += int(viewport_height * 0.9)
                
                # 如果已经滚动到底部，停止
                if scroll_position >= total_height - 50:  # 留50px余量
                    break
            
            print()  # 换行
            
            # 滚动回顶部
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.1)
            
            print(f"  开始合并 {len(images)} 张截图...")
            
            # 合并所有截图（处理重叠部分）
            if len(images) > 1:
                # 计算实际需要的总高度（考虑重叠）
                # 第一张图片完整高度，后续图片只取不重叠的部分
                overlap = int(viewport_height * 0.1)  # 10%重叠
                total_img_height = images[0].height + sum(img.height - overlap for img in images[1:])
                
                # 创建新图片
                merged_img = Image.new('RGB', (images[0].width, total_img_height))
                y_offset = 0
                
                for i, img in enumerate(images):
                    if i == 0:
                        # 第一张图片完整粘贴
                        merged_img.paste(img, (0, y_offset))
                        y_offset += img.height
                    else:
                        # 后续图片只粘贴不重叠的部分
                        # 从overlap位置开始裁剪
                        crop_box = (0, overlap, img.width, img.height)
                        cropped_img = img.crop(crop_box)
                        merged_img.paste(cropped_img, (0, y_offset))
                        y_offset += cropped_img.height
            else:
                merged_img = images[0]
        else:
            # 页面不需要滚动，直接截图
            screenshot = driver.get_screenshot_as_png()
            merged_img = Image.open(BytesIO(screenshot))
        
        # 转换为RGB模式（PDF需要RGB）
        if merged_img.mode != 'RGB':
            merged_img = merged_img.convert('RGB')
        
        print("  正在保存为PDF...")
        # 保存为PDF（提高分辨率）
        merged_img.save(save_path, 'PDF', resolution=100.0, quality=95)
        print(f"✓ 页面已保存为PDF: {save_path}")
        return True
        
    except Exception as e:
        print(f"✗ 保存PDF失败: {e}")
        import traceback
        traceback.print_exc()
        return False

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
        print("  正在查找包含去年年份的文档链接...")
        
        # 首先尝试在列表页面查找包含去年年份的链接
        library_report_link = None
        library_report_text = None
        
        try:
            # 方法1: 查找包含"年报"、"年度报告"或"年度"和去年年份的链接
            keywords = ['年报', '年度报告', '年度', '报告']
            all_links = driver.find_elements(By.XPATH, "//a[@href]")
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    title_attr = link.get_attribute('title') or ''
                    combined_text = text + ' ' + title_attr
                    
                    # 检查是否包含关键词和去年年份
                    has_keyword = any(kw in combined_text for kw in keywords)
                    has_year = last_year_str in combined_text or last_year_str in (href or '')
                    
                    if has_keyword and has_year:
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
                
                # 查找包含"点击下载"的按钮或链接
                try:
                    click_download_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '点击下载') or contains(text(), '下载')]")
                    for element in click_download_elements:
                        try:
                            # 如果是链接
                            if element.tag_name == 'a':
                                href = element.get_attribute('href')
                                if href:
                                    if href.startswith('/'):
                                        pdf_url = urljoin(base_url, href)
                                    elif not href.startswith('http'):
                                        pdf_url = urljoin(detail_url, href)
                                    else:
                                        pdf_url = href
                                    print(f"✓ 找到下载链接: {pdf_url}")
                                    return pdf_url, last_year_str
                            # 如果是按钮，尝试点击
                            else:
                                try:
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                    time.sleep(1)
                                    element.click()
                                    time.sleep(3)
                                    
                                    # 检查当前URL是否是PDF
                                    current_url = driver.current_url
                                    if current_url.lower().endswith('.pdf') or '.pdf' in current_url.lower():
                                        print(f"✓ 点击后找到PDF: {current_url}")
                                        return current_url, last_year_str
                                except:
                                    pass
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
                
                # 如果没有找到PDF链接，使用截图保存为PDF
                print("  未找到PDF下载链接，将使用页面截图保存为PDF...")
                # 返回一个特殊标记，表示需要截图
                return ('SCREENSHOT', detail_url, last_year_str)
                
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
                    if href and last_year_str in (href + ' ' + text):
                        print(f"✓ 找到PDF链接: {text or href}")
                        return href, last_year_str
                except:
                    continue
        except:
            pass
        
        # 查找包含"年报"、"年度报告"和去年年份的链接
        try:
            report_links = driver.find_elements(By.XPATH, "//a[contains(text(), '年报') or contains(text(), '年度报告') or contains(text(), '年度')]")
            for link in report_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    if href and last_year_str in (href + ' ' + text):
                        print(f"✓ 找到年报链接: {text or href}")
                        # 如果是详情页链接，需要进入详情页查找PDF
                        if not href.lower().endswith('.pdf'):
                            # 尝试访问详情页
                            if href.startswith('/'):
                                detail_url = urljoin(base_url, href)
                            elif not href.startswith('http'):
                                detail_url = urljoin(base_url, '/' + href)
                            else:
                                detail_url = href
                            
                            try:
                                driver.get(detail_url)
                                time.sleep(3)
                                
                                # 在详情页查找PDF
                                pdf_links_detail = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                                if pdf_links_detail:
                                    pdf_href = pdf_links_detail[0].get_attribute('href')
                                    if pdf_href:
                                        if pdf_href.startswith('/'):
                                            pdf_url = urljoin(base_url, pdf_href)
                                        elif not pdf_href.startswith('http'):
                                            pdf_url = urljoin(detail_url, pdf_href)
                                        else:
                                            pdf_url = pdf_href
                                        print(f"✓ 在详情页找到PDF: {pdf_url}")
                                        return pdf_url, last_year_str
                            except:
                                pass
                        else:
                            return href, last_year_str
                except:
                    continue
        except:
            pass
        
        # 查找所有包含去年年份的文档链接
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
    print("山东省图书馆年报下载工具")
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
    
    # 山东省图书馆年报页面URL
    report_page_url = "http://www.sdlib.com/channels/ch00734/"
    base_url = "http://www.sdlib.com"
    
    print(f"目标年份: {last_year}年")
    print(f"输出路径: {output_folder}")
    print("-" * 60)
    
    # 查找年报链接
    result = find_last_year_report(report_page_url, base_url)
    
    if not result:
        print("\n✗ 未找到年报链接，下载失败")
        return
    
    # 处理返回值：可能是(url, year)元组、('SCREENSHOT', detail_url, year)元组或只有url
    if isinstance(result, tuple) and len(result) == 3 and result[0] == 'SCREENSHOT':
        # 需要截图保存
        _, detail_url, actual_year = result
        if actual_year and actual_year != last_year_str:
            print(f"⚠️  注意：找到的是 {actual_year} 年的年报，不是 {last_year_str} 年的")
            year_for_filename = actual_year
        else:
            year_for_filename = last_year_str
        
        filename = f"山东省图书馆{year_for_filename}年年报.pdf"
        filename = clean_filename(filename)
        
        print(f"\n文件名: {filename}")
        print("-" * 60)
        
        # 创建保存目录
        os.makedirs(output_folder, exist_ok=True)
        file_path = os.path.join(output_folder, filename)
        
        # 打开浏览器访问详情页并截图
        driver = None
        try:
            driver = setup_driver()
            if not driver:
                print("✗ 无法启动浏览器进行截图")
                return
            
            print(f"正在访问详情页进行截图: {detail_url}")
            driver.get(detail_url)
            
            # 等待页面基本加载完成
            try:
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                # 等待页面稳定（DOM和图片加载）
                # 使用JavaScript检查图片是否加载完成
                driver.execute_script("""
                    return new Promise((resolve) => {
                        let images = document.querySelectorAll('img');
                        let loaded = 0;
                        let total = images.length;
                        if (total === 0) {
                            resolve();
                            return;
                        }
                        images.forEach(img => {
                            if (img.complete) {
                                loaded++;
                            } else {
                                img.onload = img.onerror = () => {
                                    loaded++;
                                    if (loaded === total) resolve();
                                };
                            }
                        });
                        if (loaded === total) resolve();
                        setTimeout(resolve, 2000); // 最多等待2秒
                    });
                """)
            except TimeoutException:
                print("  页面加载超时，继续尝试...")
            except:
                pass
            
            # 额外等待一小段时间确保渲染完成
            time.sleep(1)
            
            # 截图保存为PDF
            success = save_page_as_pdf(driver, file_path)
            
            if success:
                actual_size = os.path.getsize(file_path)
                print("\n" + "=" * 60)
                print("✓ 截图保存完成")
                print("=" * 60)
                print(f"文件大小: {actual_size:,} 字节 ({actual_size/1024/1024:.2f} MB)")
                print(f"文件已保存到: {file_path}")
            else:
                print("\n" + "=" * 60)
                print("✗ 截图保存失败")
                print("=" * 60)
                
        except Exception as e:
            print(f"✗ 截图过程出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    else:
        # 正常下载PDF文件
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
        
        filename = f"山东省图书馆{year_for_filename}年年报{file_ext}"
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

