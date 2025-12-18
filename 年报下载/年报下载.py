import requests
import os
import time
import random
import re
import sys
import json
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 图书馆年报URL字典（将从豆包获取或使用默认值）
LIBRARY_URLS = {}

# 图书馆名称映射（根据URL特征识别）
LIBRARY_NAME_MAP = {
    "ncl.edu.tw": "中国国家图书馆",
    "library.sh.cn": "上海图书馆",
    "zjlib.cn": "浙江图书馆",
    "zslib.com.cn": "广东省立中山图书馆",
    "jslib.org.cn": "南京图书馆",
    "clcn.net.cn": "首都图书馆",
    "tjl.tj.cn": "天津图书馆",
    "hebei.gov.cn": "河北省图书馆",
    "shanxi.gov.cn": "山西省图书馆",
    "nmg.gov.cn": "内蒙古图书馆",
}

def identify_library_from_url(url):
    """根据URL识别图书馆名称"""
    if not url:
        return None
    
    # 从URL中提取域名
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # 移除www前缀
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # 查找匹配的图书馆
        for key, library_name in LIBRARY_NAME_MAP.items():
            if key in domain:
                return library_name
        
        # 如果没有精确匹配，尝试部分匹配
        for key, library_name in LIBRARY_NAME_MAP.items():
            key_parts = key.split('.')
            domain_parts = domain.split('.')
            # 检查是否有共同的部分
            if any(part in domain_parts for part in key_parts if len(part) > 3):
                return library_name
        
    except Exception as e:
        print(f"  识别图书馆名称时出错: {e}")
    
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
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

def extract_year_from_url(url):
    """从URL中提取年份"""
    # 查找4位数字年份（2000-2099）
    year_match = re.search(r'(20\d{2})', url)
    if year_match:
        return year_match.group(1)
    return None

def extract_year_from_filename(filename):
    """从文件名中提取年份"""
    year_match = re.search(r'(20\d{2})', filename)
    if year_match:
        return year_match.group(1)
    return None

def clean_filename(filename):
    """清理文件名，移除Windows不允许的字符"""
    # Windows不允许的字符: < > : " / \ | ? *
    invalid_chars = r'[<>:"/\\|?*]'
    # 替换为下划线
    cleaned = re.sub(invalid_chars, '_', filename)
    # 移除首尾空格和点
    cleaned = cleaned.strip(' .')
    # 确保文件名不为空
    if not cleaned:
        cleaned = "unnamed_file"
    return cleaned

def find_pdf_in_html(html_content, base_url):
    """从HTML内容中查找PDF链接"""
    soup = BeautifulSoup(html_content, 'html.parser')
    pdf_links = []
    
    # 获取去年的年份
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    last_year_str = str(last_year)
    
    # 查找所有链接
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if href:
            # 构建完整URL
            full_url = urljoin(base_url, href)
            # 检查是否是PDF链接
            if full_url.lower().endswith('.pdf') or 'pdf' in href.lower():
                pdf_links.append(full_url)
    
    # 也查找直接嵌入的PDF链接
    for tag in soup.find_all(['iframe', 'embed', 'object']):
        src = tag.get('src') or tag.get('data')
        if src:
            full_url = urljoin(base_url, src)
            if full_url.lower().endswith('.pdf'):
                pdf_links.append(full_url)
    
    # 查找包含"年报"或"annual report"的链接
    for link in soup.find_all('a', href=True):
        text = link.get_text().strip()
        href = link.get('href')
        if href and ('年报' in text or '年报' in href or 'annual' in text.lower() or 'annual' in href.lower()):
            full_url = urljoin(base_url, href)
            pdf_links.append(full_url)
    
    return pdf_links

def download_pdf(url, filename, save_dir):
    """下载PDF文件并确保文件名正确"""
    try:
        session = requests.Session()
        session.headers.update(get_headers())
        
        # 随机延迟
        delay = random.uniform(1, 3)
        print(f"  等待 {delay:.1f} 秒...")
        time.sleep(delay)
        
        # 下载文件
        response = session.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # 检查内容类型
        content_type = response.headers.get('Content-Type', '').lower()
        if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
            print(f"  警告: 内容类型可能不是PDF: {content_type}")
        
        # 确保文件名格式正确：图书馆名称年份年报.pdf
        # 如果文件名不符合格式，确保以.pdf结尾
        if not filename.endswith('.pdf'):
            filename = filename + '.pdf'
        
        # 清理文件名
        filename = clean_filename(filename)
        
        # 创建保存目录
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, filename)
        else:
            file_path = filename
        
        # 如果文件已存在，先删除
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"  已删除已存在的文件: {filename}")
            except:
                pass
        
        # 保存文件
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        # 验证文件是否成功保存
        if not os.path.exists(file_path):
            print(f"  ✗ 文件保存失败: {file_path}")
            return False
        
        file_size = os.path.getsize(file_path)
        
        # 验证文件名是否正确
        actual_filename = os.path.basename(file_path)
        if actual_filename != filename:
            # 如果文件名不对，重命名
            try:
                correct_path = os.path.join(os.path.dirname(file_path), filename)
                os.rename(file_path, correct_path)
                file_path = correct_path
                print(f"  ✓ 已重命名为: {filename}")
            except Exception as e:
                print(f"  ⚠️  重命名失败: {e}")
        
        print(f"  ✓ 下载成功: {filename}")
        print(f"    文件大小: {file_size:,} 字节 ({file_size/1024/1024:.2f} MB)")
        print(f"    保存路径: {file_path}")
        
        session.close()
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ 下载失败: {e}")
        return False
    except Exception as e:
        print(f"  ✗ 发生错误: {e}")
        return False

def process_library(library_name, url, save_dir):
    """处理单个图书馆的年报下载"""
    print(f"\n处理: {library_name}")
    print(f"  URL: {url}")
    
    # 获取去年的年份
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    last_year_str = str(last_year)
    
    session = None
    try:
        session = requests.Session()
        session.headers.update(get_headers())
        
        # 先尝试访问URL（使用HEAD请求检查，如果是PDF则直接下载）
        try:
            head_response = session.head(url, timeout=30, allow_redirects=True)
            content_type = head_response.headers.get('Content-Type', '').lower()
            
            if 'pdf' in content_type or url.lower().endswith('.pdf'):
                # 直接是PDF文件
                pdf_url = url
                print("  检测到直接PDF链接")
                # 提取年份
                year = extract_year_from_url(pdf_url)
                
                # 检查是否是去年的年报
                if year:
                    if year != last_year_str:
                        print(f"  ⚠️  跳过：该文件是{year}年的，不是去年的年报（{last_year_str}年）")
                        return False
                    print(f"  提取到年份: {year}（去年的年报）")
                else:
                    print(f"  ⚠️  无法从URL提取年份，跳过下载")
                    return False
                
                filename = f"{library_name}{year}年年报.pdf"
                filename = clean_filename(filename)  # 清理文件名
                print(f"  文件名: {filename}")
                return download_pdf(pdf_url, filename, save_dir)
        except:
            # HEAD请求失败，继续使用GET请求
            pass
        
        # 使用GET请求获取内容
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '').lower()
        
        # 判断是PDF还是HTML
        if 'pdf' in content_type:
            # 直接是PDF文件
            pdf_url = url
            print("  检测到直接PDF链接")
            # 提取年份
            year = extract_year_from_url(pdf_url)
        else:
            # 是HTML页面，需要解析
            print("  检测到HTML页面，正在解析...")
            html_content = response.text
            pdf_links = find_pdf_in_html(html_content, url)
            
            if not pdf_links:
                print("  ✗ 未找到PDF链接")
                return False
            
            # 优先选择包含"年报"的链接，并且是去年的
            pdf_url = None
            for link in pdf_links:
                link_year = extract_year_from_url(link)
                if link_year == last_year_str and ('年报' in link or 'annual' in link.lower()):
                    pdf_url = link
                    print(f"  找到去年的年报链接: {link}")
                    break
            
            # 如果没找到包含"年报"的去年链接，尝试找任何去年的PDF链接
            if not pdf_url:
                for link in pdf_links:
                    link_year = extract_year_from_url(link)
                    if link_year == last_year_str:
                        pdf_url = link
                        print(f"  找到去年的PDF链接: {link}")
                        break
            
            # 如果还是没找到去年的，尝试从URL提取年份
            if not pdf_url:
                year = extract_year_from_url(url)
                if year == last_year_str:
                    # 如果URL本身包含去年的年份，可能需要进一步解析
                    pdf_url = pdf_links[0] if pdf_links else None
                else:
                    print(f"  ⚠️  未找到去年的年报链接（{last_year_str}年）")
                    return False
            
            if not pdf_url:
                print(f"  ⚠️  未找到去年的年报链接（{last_year_str}年）")
                return False
            
            print(f"  找到PDF链接: {pdf_url}")
            # 提取年份
            year = extract_year_from_url(pdf_url) or extract_year_from_url(url)
        
        # 检查是否是去年的年报
        if not year:
            # 尝试从响应头或文件名中提取
            content_disposition = response.headers.get('Content-Disposition', '')
            if content_disposition:
                year = extract_year_from_filename(content_disposition)
            
            if not year:
                print(f"  ⚠️  无法提取年份，跳过下载")
                return False
        
        # 验证年份是否是去年
        if year != last_year_str:
            print(f"  ⚠️  跳过：该文件是{year}年的，不是去年的年报（{last_year_str}年）")
            return False
        
        print(f"  提取到年份: {year}（去年的年报）")
        
        # 生成文件名
        filename = f"{library_name}{year}年年报.pdf"
        filename = clean_filename(filename)  # 清理文件名
        print(f"  文件名: {filename}")
        
        # 下载PDF
        if pdf_url == url and 'pdf' in content_type:
            # 如果就是原始URL且是PDF，直接保存响应内容
            try:
                # 确保文件名格式正确
                if not filename.endswith('.pdf'):
                    filename = filename + '.pdf'
                filename = clean_filename(filename)
                
                if save_dir:
                    os.makedirs(save_dir, exist_ok=True)
                    file_path = os.path.join(save_dir, filename)
                else:
                    file_path = filename
                
                # 如果文件已存在，先删除
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"  已删除已存在的文件: {filename}")
                    except:
                        pass
                
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                
                # 验证文件是否成功保存
                if not os.path.exists(file_path):
                    print(f"  ✗ 文件保存失败: {file_path}")
                    return False
                
                file_size = os.path.getsize(file_path)
                
                # 验证文件名是否正确
                actual_filename = os.path.basename(file_path)
                if actual_filename != filename:
                    # 如果文件名不对，重命名
                    try:
                        correct_path = os.path.join(os.path.dirname(file_path), filename)
                        os.rename(file_path, correct_path)
                        file_path = correct_path
                        print(f"  ✓ 已重命名为: {filename}")
                    except Exception as e:
                        print(f"  ⚠️  重命名失败: {e}")
                
                print(f"  ✓ 下载成功: {filename}")
                print(f"    文件大小: {file_size:,} 字节 ({file_size/1024/1024:.2f} MB)")
                print(f"    保存路径: {file_path}")
                return True
            except Exception as e:
                print(f"  ✗ 保存失败: {e}")
                return False
        else:
            # 如果PDF URL和原始URL不同，需要重新下载
            return download_pdf(pdf_url, filename, save_dir)
            
    except requests.exceptions.RequestException as e:
        print(f"  ✗ 请求失败: {e}")
        return False
    except Exception as e:
        print(f"  ✗ 处理失败: {e}")
        return False
    finally:
        if session:
            session.close()

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
        
        # 使用临时用户数据目录，每次都是全新的浏览器环境
        # 这样可以避免使用之前的会话数据和限制
        import tempfile
        user_data_dir = tempfile.mkdtemp(prefix='chrome_user_data_')
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        print(f"  使用临时用户数据目录: {user_data_dir}")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        print(f"浏览器启动失败: {e}")
        raise

def send_message_to_doubao(driver, message):
    """向豆包发送消息"""
    try:
        print(f"正在输入消息: {message}")
        
        # 查找输入框
        input_selectors = [
            "textarea",
            "input[type='text']",
            "[contenteditable='true']",
            "[placeholder*='发消息']",
            "[placeholder*='消息']",
        ]
        
        input_element = None
        for selector in input_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        input_element = elem
                        break
                if input_element:
                    break
            except:
                continue
        
        if input_element:
            # 滚动到输入框
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_element)
            time.sleep(0.3)
            
            # 点击输入框确保获得焦点
            try:
                input_element.click()
            except:
                driver.execute_script("arguments[0].click();", input_element)
            time.sleep(0.3)
            
            # 清空输入框
            try:
                input_element.clear()
            except:
                if input_element.tag_name in ['textarea', 'input']:
                    driver.execute_script("arguments[0].value = '';", input_element)
                else:
                    driver.execute_script("arguments[0].innerText = ''; arguments[0].textContent = '';", input_element)
            time.sleep(0.3)
            
            # 输入消息
            if input_element.tag_name in ['textarea', 'input']:
                input_element.send_keys(message)
                # 触发input事件，确保界面更新
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", input_element)
            else:
                # contenteditable元素，使用JavaScript设置
                driver.execute_script(f"arguments[0].innerText = '{message}'; arguments[0].textContent = '{message}';", input_element)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", input_element)
            
            print(f"✓ 已输入消息")
            time.sleep(2)  # 增加等待时间，确保按钮状态更新
        else:
            print("⚠️  未找到输入框，尝试使用JavaScript输入...")
            # 使用JavaScript输入
            script = f"""
            var inputs = document.querySelectorAll('textarea, input[type="text"], [contenteditable="true"]');
            for (var i = 0; i < inputs.length; i++) {{
                if (inputs[i].offsetParent !== null) {{
                    inputs[i].focus();
                    inputs[i].value = '{message}';
                    inputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                    break;
                }}
            }}
            """
            driver.execute_script(script)
            time.sleep(1)
        
        # 查找并点击发送按钮
        print("正在查找并点击发送按钮...")
        send_button = None
        
        # 方法1: 使用精确的aria-label查找
        try:
            wait = WebDriverWait(driver, 5)
            send_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="发送"]')))
            print("✓ 找到发送按钮（通过aria-label）")
        except TimeoutException:
            print("通过aria-label未找到发送按钮，尝试其他方法...")
        
        # 方法2: 如果方法1失败，尝试其他选择器
        if not send_button:
            send_selectors = [
                'button[aria-label="发送"]',  # 精确匹配
                "button[aria-label*='发送']",  # 包含匹配
                "button[title*='发送']",
                "button[type='submit']",
                "button:has(svg[class*='arrow-up'])",
                "button:has(svg[class*='arrow'])",
            ]
            
            for selector in send_selectors:
                try:
                    send_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in send_buttons:
                        try:
                            # 检查按钮是否可见和可点击
                            if btn.is_displayed():
                                # 获取aria-label属性进行验证
                                aria_label = btn.get_attribute('aria-label')
                                if aria_label and '发送' in aria_label:
                                    send_button = btn
                                    print(f"✓ 找到发送按钮（通过选择器: {selector}）")
                                    break
                        except:
                            continue
                    if send_button:
                        break
                except:
                    continue
        
        # 方法3: 使用XPath精确查找
        if not send_button:
            try:
                send_buttons = driver.find_elements(By.XPATH, "//button[@aria-label='发送']")
                for btn in send_buttons:
                    if btn.is_displayed():
                        send_button = btn
                        print("✓ 找到发送按钮（通过XPath）")
                        break
            except:
                pass
        
        # 方法4: 使用JavaScript查找
        if not send_button:
            print("尝试使用JavaScript查找发送按钮...")
            try:
                script = """
                var buttons = document.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {
                    var btn = buttons[i];
                    var ariaLabel = btn.getAttribute('aria-label');
                    if (ariaLabel && ariaLabel.includes('发送')) {
                        var rect = btn.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            return btn;
                        }
                    }
                }
                return null;
                """
                send_button = driver.execute_script(script)
                if send_button:
                    print("✓ 找到发送按钮（通过JavaScript）")
            except:
                pass
        
        # 点击发送按钮
        if send_button:
            try:
                print("正在点击发送按钮...")
                # 滚动到按钮位置
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", send_button)
                time.sleep(0.5)
                
                # 尝试多种点击方式
                try:
                    # 方式1: 直接点击
                    send_button.click()
                    print("✓ 已点击发送按钮（直接点击）")
                except:
                    # 方式2: 使用JavaScript点击
                    driver.execute_script("arguments[0].click();", send_button)
                    print("✓ 已点击发送按钮（JavaScript点击）")
            except Exception as e:
                print(f"⚠️  点击发送按钮时出错: {e}")
                # 最后尝试：使用JavaScript强制点击
                try:
                    driver.execute_script("""
                    var btn = arguments[0];
                    btn.dispatchEvent(new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    }));
                    """, send_button)
                    print("✓ 已点击发送按钮（事件触发）")
                except:
                    print("✗ 无法点击发送按钮")
        else:
            print("⚠️  未找到发送按钮，尝试按回车键发送...")
            try:
                if input_element:
                    input_element.send_keys(Keys.RETURN)
                    print("✓ 已按回车键发送")
                else:
                    # 使用JavaScript模拟回车
                    script = """
                    var inputs = document.querySelectorAll('textarea, input[type="text"], [contenteditable="true"]');
                    for (var i = 0; i < inputs.length; i++) {
                        if (inputs[i].offsetParent !== null) {
                            var event = new KeyboardEvent('keydown', {
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                which: 13,
                                bubbles: true,
                                cancelable: true
                            });
                            inputs[i].dispatchEvent(event);
                            var event2 = new KeyboardEvent('keyup', {
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                which: 13,
                                bubbles: true,
                                cancelable: true
                            });
                            inputs[i].dispatchEvent(event2);
                            break;
                        }
                    }
                    """
                    driver.execute_script(script)
                    print("✓ 已通过JavaScript模拟回车键")
            except Exception as e:
                print(f"⚠️  按回车键失败: {e}")
        
        print("✓ 消息已发送")
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"发送消息失败: {e}")
        raise

def wait_for_response(driver, timeout=120):
    """等待豆包返回响应"""
    print("正在等待豆包处理并返回结果...")
    
    start_time = time.time()
    last_text_length = 0
    stable_count = 0
    
    while time.time() - start_time < timeout:
        try:
            # 查找最新的消息内容
            message_selectors = [
                "[class*='message']",
                "[class*='response']",
                "[class*='content']",
                "article",
                "[role='article']",
            ]
            
            all_text = ""
            for selector in message_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            try:
                                all_text += elem.text + "\n"
                            except:
                                pass
                except:
                    continue
            
            all_text = all_text.strip()
            current_length = len(all_text)
            
            # 如果文本长度稳定（3秒内没有变化），认为响应完成
            if current_length == last_text_length and current_length > 0:
                stable_count += 1
                if stable_count >= 3:  # 3次检查都稳定
                    print("✓ 响应已完成")
                    return True
            else:
                stable_count = 0
                last_text_length = current_length
            
            time.sleep(1)
            
        except Exception as e:
            print(f"等待响应时出错: {e}")
            time.sleep(1)
    
    print("⚠️  等待响应超时，将尝试提取已有内容")
    return False

def extract_json_from_response(driver):
    """从响应中提取JSON格式的数据"""
    try:
        print("正在提取JSON格式的数据...")
        
        # 获取所有可见文本，包括HTML内容
        message_selectors = [
            "[class*='message']",
            "[class*='response']",
            "[class*='content']",
            "[class*='markdown']",
            "article",
            "[role='article']",
            "[class*='prose']",
            "pre",
            "code",
        ]
        
        all_text = ""
        all_html = ""
        
        # 方法1: 获取文本内容
        for selector in message_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed():
                        try:
                            all_text += elem.text + "\n"
                            # 也获取HTML内容，可能包含代码块
                            all_html += elem.get_attribute('innerHTML') or ""
                        except:
                            pass
            except:
                continue
        
        # 方法2: 直接获取页面源码中的JSON
        try:
            page_source = driver.page_source
            all_html += page_source
        except:
            pass
        
        if not all_text and not all_html:
            print("⚠️  未找到任何文本内容")
            return None
        
        # 打印部分文本用于调试
        preview_text = (all_text[:500] if all_text else "") + (all_html[:500] if all_html else "")
        if preview_text:
            print(f"  提取到的文本预览: {preview_text[:200]}...")
        
        # 尝试提取JSON
        # 方法1: 查找代码块中的JSON (```json ... ```)
        json_pattern = r'```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```'
        for text_source in [all_text, all_html]:
            matches = re.findall(json_pattern, text_source, re.DOTALL)
            if matches:
                for match in matches:
                    try:
                        data = json.loads(match)
                        print(f"✓ 从代码块提取了JSON数据")
                        return data
                    except Exception as e:
                        print(f"  解析JSON代码块失败: {e}")
                        continue
        
        # 方法2: 查找纯JSON对象或数组（使用非贪婪匹配）
        json_patterns = [
            r'(\{[\s\S]*?\})',  # JSON对象
            r'(\[[\s\S]*?\])',  # JSON数组
        ]
        
        for pattern in json_patterns:
            for text_source in [all_text, all_html]:
                matches = re.findall(pattern, text_source, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        print(f"✓ 从文本提取了JSON数据（模式: {pattern[:20]}...）")
                        return data
                    except Exception as e:
                        continue
        
        # 方法3: 尝试从整个文本中提取JSON（通过匹配括号）
        for text_source in [all_text, all_html]:
            # 查找可能的JSON开始位置
            start_idx = text_source.find('{')
            if start_idx == -1:
                start_idx = text_source.find('[')
            
            if start_idx != -1:
                # 尝试找到匹配的结束位置
                bracket_count = 0
                brace_count = 0
                in_string = False
                escape_next = False
                
                for i in range(start_idx, len(text_source)):
                    char = text_source[i]
                    
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                    
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if not in_string:
                        if char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                        elif char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                        
                        if bracket_count == 0 and brace_count == 0 and i > start_idx:
                            json_str = text_source[start_idx:i+1]
                            try:
                                data = json.loads(json_str)
                                print(f"✓ 从完整文本提取了JSON数据（长度: {len(json_str)}）")
                                return data
                            except Exception as e:
                                # 继续尝试下一个可能的JSON
                                continue
        
        # 方法4: 尝试查找所有可能的JSON片段
        print("  尝试查找所有JSON片段...")
        json_candidates = []
        for text_source in [all_text, all_html]:
            # 查找所有 { 和 [ 的位置
            for start_char in ['{', '[']:
                start_idx = 0
                while True:
                    start_idx = text_source.find(start_char, start_idx)
                    if start_idx == -1:
                        break
                    
                    # 尝试从这个位置提取JSON
                    bracket_count = 0
                    brace_count = 0
                    in_string = False
                    escape_next = False
                    
                    for i in range(start_idx, min(start_idx + 10000, len(text_source))):  # 限制最大长度
                        char = text_source[i]
                        
                        if escape_next:
                            escape_next = False
                            continue
                        
                        if char == '\\':
                            escape_next = True
                            continue
                        
                        if char == '"' and not escape_next:
                            in_string = not in_string
                            continue
                        
                        if not in_string:
                            if char == '[':
                                bracket_count += 1
                            elif char == ']':
                                bracket_count -= 1
                            elif char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                            
                            if bracket_count == 0 and brace_count == 0 and i > start_idx:
                                json_str = text_source[start_idx:i+1]
                                if len(json_str) > 10:  # 至少要有一定长度
                                    json_candidates.append(json_str)
                                break
                    
                    start_idx += 1
        
        # 尝试解析所有候选JSON
        for candidate in json_candidates:
            try:
                data = json.loads(candidate)
                print(f"✓ 从候选片段提取了JSON数据（长度: {len(candidate)}）")
                return data
            except:
                continue
        
        print("⚠️  未能提取到有效的JSON数据")
        print(f"  文本长度: {len(all_text)}, HTML长度: {len(all_html)}")
        return None
        
    except Exception as e:
        print(f"提取JSON失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_library_urls_from_doubao():
    """通过豆包获取图书馆年报下载链接"""
    driver = None
    try:
        print("=" * 60)
        print("正在通过豆包获取图书馆年报下载链接...")
        print("=" * 60)
        
        # 启动浏览器
        print("正在启动浏览器...")
        driver = setup_driver()
        
        # 打开豆包聊天页面
        print("正在打开豆包聊天页面...")
        driver.get("https://www.doubao.com/chat")
        time.sleep(5)  # 等待页面加载
        
        # 清除所有存储数据（localStorage, sessionStorage, cookies等）
        try:
            print("正在清除浏览器存储数据...")
            # 清除 localStorage 和 sessionStorage
            driver.execute_script("""
                try {
                    localStorage.clear();
                    sessionStorage.clear();
                } catch(e) {
                    console.log('清除存储时出错:', e);
                }
            """)
            # 清除 cookies
            driver.delete_all_cookies()
            print("✓ 已清除浏览器存储数据")
            
            # 重新加载页面，确保使用干净的状态
            driver.refresh()
            time.sleep(3)
        except Exception as e:
            print(f"⚠️  清除存储数据时出错: {e}")
            # 即使清除失败也继续执行
        
        # 发送指令
        message = "【中国国家图书馆、上海图书馆、浙江图书馆找这些图书馆去年年报下载链接，可以点击直接下载，以json的形式返还】"
        send_message_to_doubao(driver, message)
        
        # 等待响应
        wait_for_response(driver, timeout=120)
        
        # 提取JSON响应
        json_data = extract_json_from_response(driver)
        
        if json_data:
            print("✓ 成功获取到JSON数据")
            # 解析JSON并更新LIBRARY_URLS
            # 直接使用JSON中的键名作为图书馆名称
            library_urls = {}
            if isinstance(json_data, dict):
                # 字典格式：{"图书馆名称": "URL"}
                library_urls = json_data
                print(f"  解析到字典格式，包含 {len(library_urls)} 个图书馆")
                for library_name, url in library_urls.items():
                    print(f"    {library_name}: {url}")
            elif isinstance(json_data, list):
                # 列表格式：[{"图书馆名称": "URL"}, ...]
                for item in json_data:
                    if isinstance(item, dict):
                        library_urls.update(item)
                print(f"  解析到列表格式，包含 {len(library_urls)} 个图书馆")
                for library_name, url in library_urls.items():
                    print(f"    {library_name}: {url}")
            
            if library_urls:
                print(f"✓ 成功解析到 {len(library_urls)} 个图书馆链接")
                return library_urls
            else:
                print("⚠️  JSON数据格式不正确，使用默认链接")
                return None
        else:
            print("⚠️  未能提取到JSON数据，使用默认链接")
            return None
            
    except Exception as e:
        print(f"✗ 通过豆包获取链接失败: {e}")
        print("将使用默认链接")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def load_config_from_txt(config_path):
    """从TXT配置文件读取配置，格式：key=value，支持#注释和空行"""
    config = {}
    try:
        if not os.path.exists(config_path):
            return config
        
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                # 解析 key=value 格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # 去掉引号（如果有）
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    config[key] = value
    except Exception as e:
        print(f"读取配置文件时出错: {str(e)}")
        return {}
    return config

def main():
    """主函数"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 读取配置文件
    config_path = os.path.join(script_dir, "config.txt")
    config = load_config_from_txt(config_path)
    
    # 从配置文件读取输出路径，如果未配置则使用默认路径
    output_folder = config.get("output_folder", "").strip()
    if output_folder:
        save_dir = output_folder
    else:
        # 默认保存目录（当前脚本所在目录）
        save_dir = os.path.join(script_dir, "下载的年报")
    
    # 全局变量，用于存储图书馆URL
    global LIBRARY_URLS
    
    # 首先通过豆包获取图书馆年报链接
    doubao_urls = get_library_urls_from_doubao()
    if doubao_urls:
        # 更新LIBRARY_URLS，保留豆包返回的链接，如果豆包没有返回的则使用默认链接
        for library_name, url in doubao_urls.items():
            LIBRARY_URLS[library_name] = url
        print(f"\n✓ 已更新 {len(doubao_urls)} 个图书馆链接")
    else:
        print("\n使用默认链接列表")
    
    print("\n" + "=" * 60)
    print("图书馆年报下载工具")
    print("=" * 60)
    print(f"保存目录: {save_dir}")
    print(f"共 {len(LIBRARY_URLS)} 个图书馆")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    # 遍历所有图书馆
    for library_name, url in LIBRARY_URLS.items():
        if process_library(library_name, url, save_dir):
            success_count += 1
        else:
            fail_count += 1
    
    # 输出统计信息
    print("\n" + "=" * 60)
    print("下载完成")
    print("=" * 60)
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print(f"总计: {len(LIBRARY_URLS)} 个")
    print(f"文件保存在: {save_dir}")

if __name__ == "__main__":
    main()

