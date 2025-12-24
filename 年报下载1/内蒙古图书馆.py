# -*- coding: utf-8 -*-
"""
内蒙古图书馆年报下载脚本
功能：从内蒙古图书馆官网下载去年的年报，并重命名为"内蒙古图书馆年份年报"格式
"""

import requests
import os
import time
import re
import urllib3
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Selenium相关导入
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
    print("⚠️  警告: 未安装Selenium，将使用requests方式（可能无法处理JavaScript动态内容）")
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

def verify_year_in_text(text, target_year):
    """严格验证文本中是否包含目标年份（避免误匹配）"""
    if not text or not target_year:
        return False
    # 查找完整的4位年份
    years = re.findall(r'20[0-3]\d', text)
    # 检查是否包含目标年份
    return target_year in years

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

def setup_selenium_driver():
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

def find_last_year_report_selenium(url, base_url):
    """使用Selenium在页面中查找去年的年报链接"""
    # 获取去年的年份（动态计算）
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    last_year_str = str(last_year)
    
    # 目标年份就是去年（动态计算，确保准确）
    target_year = last_year_str
    print(f"目标年份: {target_year}年（严格匹配，只查找{target_year}年的年报）")
    
    if not SELENIUM_AVAILABLE:
        return None
    
    driver = None
    try:
        print("正在使用浏览器访问页面查找年报...")
        driver = setup_selenium_driver()
        if not driver:
            return None
        
        # 第一步：访问年报页面
        print(f"正在访问页面: {url}")
        driver.get(url)
        
        # 等待页面加载
        print("等待页面加载...")
        time.sleep(5)  # 等待JavaScript执行
        
        # 尝试等待页面元素加载
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            print("  页面加载超时，继续尝试...")
        
        # 再次等待，确保JavaScript内容加载完成
        time.sleep(3)
        
        # 第二步：查找并点击"决算"链接/按钮
        print("查找'决算'链接...")
        report_entry_keywords = ['决算']  # 只查找"决算"
        entry_elements = []
        
        # 查找所有包含"决算"文字的元素
        try:
            # 方法1: 使用XPath查找所有包含"决算"文字的元素
            xpath_selectors = [
                "//*[contains(text(), '决算')]",
                "//a[contains(text(), '决算')]",
                "//div[contains(text(), '决算')]",
                "//span[contains(text(), '决算')]",
                "//li[contains(text(), '决算')]",
                "//td[contains(text(), '决算')]",
                "//p[contains(text(), '决算')]",
                "//button[contains(text(), '决算')]",
            ]
            for selector in xpath_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        try:
                            text = elem.text.strip()
                            if text and '决算' in text and len(text) < 200:  # 限制文本长度
                                entry_elements.append(elem)
                                print(f"  找到包含'决算'的元素: {text[:50]}")
                        except:
                            continue
                except:
                    pass
        except:
            pass
        
        # 方法2: 如果XPath没找到，查找所有链接
        if not entry_elements:
            print("  使用XPath未找到，尝试查找所有链接...")
            try:
                all_links = driver.find_elements(By.TAG_NAME, "a")
                for link in all_links:
                    try:
                        text = link.text.strip()
                        if text and '决算' in text:
                            entry_elements.append(link)
                            print(f"  找到包含'决算'的链接: {text[:50]}")
                    except:
                        continue
            except:
                pass
        
        # 方法3: 查找所有包含文字的元素
        if not entry_elements:
            print("  尝试查找所有包含文字的元素...")
            try:
                all_elements = driver.find_elements(By.XPATH, "//*[text()]")
                for elem in all_elements:
                    try:
                        text = elem.text.strip()
                        if text and '决算' in text and len(text) < 100:
                            tag_name = elem.tag_name.lower()
                            if tag_name in ['a', 'button', 'div', 'span', 'li', 'td', 'p', 'label', 'h1', 'h2', 'h3', 'h4']:
                                entry_elements.append(elem)
                                print(f"  找到包含'决算'的元素: {text[:50]}")
                    except:
                        continue
            except:
                pass
        
        print(f"共找到 {len(entry_elements)} 个包含'决算'的元素")
        
        # 第三步：点击包含"决算"的文字元素，进入年报页面
        entered_report_page = False
        report_page_url = None
        
        for i, entry_elem in enumerate(entry_elements[:10]):  # 最多尝试前10个
            try:
                text = entry_elem.text.strip()
                print(f"  尝试点击元素 {i+1}: {text[:50]}")
                
                # 滚动到元素可见
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", entry_elem)
                time.sleep(1)
                
                # 确保元素在视口中
                try:
                    WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(entry_elem)
                    )
                except:
                    pass
                
                # 记录点击前的URL和窗口句柄
                url_before = driver.current_url
                window_handles_before = len(driver.window_handles)
                
                # 尝试多种点击方式
                clicked = False
                try:
                    # 方式1: 直接点击
                    entry_elem.click()
                    clicked = True
                except:
                    try:
                        # 方式2: 使用ActionChains点击
                        from selenium.webdriver.common.action_chains import ActionChains
                        ActionChains(driver).move_to_element(entry_elem).click().perform()
                        clicked = True
                    except:
                        try:
                            # 方式3: 使用JavaScript点击
                            driver.execute_script("arguments[0].click();", entry_elem)
                            clicked = True
                        except:
                            pass
                
                if not clicked:
                    print(f"    无法点击该元素，跳过")
                    continue
                
                # 等待页面响应
                time.sleep(3)
                
                # 检查URL是否变化
                url_after = driver.current_url
                if url_after != url_before:
                    print(f"✓ 已跳转到新页面: {url_after}")
                    report_page_url = url_after
                    entered_report_page = True
                    break
                
                # 检查是否有新窗口打开
                window_handles_after = len(driver.window_handles)
                if window_handles_after > window_handles_before:
                    driver.switch_to.window(driver.window_handles[-1])
                    report_page_url = driver.current_url
                    print(f"✓ 已打开新窗口（年报页面）: {report_page_url}")
                    entered_report_page = True
                    break
                
                # 检查页面内容是否变化（通过检查页面标题或特定元素）
                try:
                    page_title = driver.title
                    if page_title and page_title != driver.execute_script("return document.title"):
                        print(f"✓ 页面内容已变化，可能已跳转")
                        report_page_url = driver.current_url
                        entered_report_page = True
                        break
                except:
                    pass
                
            except Exception as e:
                print(f"  点击元素失败: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        if not entered_report_page:
            print("✗ 未能进入年报页面，下载失败")
            return None
        
        # 第四步：等待年报页面完全加载，然后保存为PDF
        print(f"年报页面已打开，等待页面完全加载...")
        
        # 等待页面完全加载
        try:
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            # 额外等待图片和资源加载
            time.sleep(5)
            
            # 滚动页面确保所有内容加载
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
        except:
            print("  页面加载超时，继续保存...")
        
        # 返回特殊标记，表示需要保存当前页面为PDF
        # 返回格式：(url, year, driver, 'save_as_pdf')
        print(f"✓ 年报页面已加载完成，准备保存为PDF")
        return (report_page_url, target_year, driver, 'save_as_pdf')
        
    except Exception as e:
        print(f"✗ Selenium查找失败: {e}")
        import traceback
        traceback.print_exc()
        if driver:
            driver.quit()
        return None
    # 注意：如果返回了save_as_pdf标记，driver不应该在这里关闭，需要在主函数中处理

def find_last_year_report(url, base_url):
    """在页面中查找去年的年报链接（优先使用Selenium）"""
    # 先尝试使用Selenium
    if SELENIUM_AVAILABLE:
        result = find_last_year_report_selenium(url, base_url)
        if result:
            return result
        print("Selenium方式未找到，尝试使用requests方式...")
    
    # 如果Selenium失败或不可用，使用requests方式
    # 获取去年的年份
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    last_year_str = str(last_year)
    
    # 使用requests方式直接查找
    print("正在使用requests访问页面查找年报...")
    session = requests.Session()
    session.headers.update(get_headers())
    
    try:
        # 处理哈希路由URL（SPA应用）
        # 如果URL包含#，先尝试访问基础URL（去掉#部分）
        original_url = url
        if '#' in url:
            # 分离基础URL和哈希部分
            base_url_part = url.split('#')[0]
            hash_part = url.split('#', 1)[1] if '#' in url else ''
            print(f"检测到哈希路由URL，基础URL: {base_url_part}")
            
            # 先尝试访问基础URL
            try:
                response = session.get(base_url_part, timeout=30, verify=False)
                response.raise_for_status()
                url = base_url_part  # 使用基础URL
            except requests.exceptions.RequestException:
                # 如果基础URL失败，尝试完整URL
                print(f"基础URL访问失败，尝试完整URL: {original_url}")
                try:
                    response = session.get(original_url, timeout=30, verify=False)
                    response.raise_for_status()
                    url = original_url
                except requests.exceptions.RequestException:
                    raise
        else:
            # 尝试访问页面，如果http失败则尝试https
            print(f"正在访问页面: {url}")
            try:
                response = session.get(url, timeout=30, verify=False)
                response.raise_for_status()
            except requests.exceptions.RequestException:
                # 如果http失败，尝试https
                if url.startswith('http://'):
                    https_url = url.replace('http://', 'https://', 1)
                    print(f"HTTP访问失败，尝试HTTPS: {https_url}")
                    try:
                        response = session.get(https_url, timeout=30, verify=False)
                        response.raise_for_status()
                        url = https_url  # 更新url为https版本
                    except requests.exceptions.RequestException as e2:
                        print(f"HTTPS访问也失败: {e2}")
                        raise
                else:
                    raise
        
        response.encoding = response.apparent_encoding or 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"查找 {last_year} 年的年报...")
        
        # 查找所有链接
        all_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            
            if not href:
                continue
            
            # 跳过javascript链接和无效链接
            if href.startswith('javascript:') or href.startswith('#') or href.strip() == '':
                continue
            
            # 构建完整URL
            full_url = urljoin(base_url, href)
            
            # 检查链接文本或URL中是否包含年报相关关键词
            keywords = ['年报', '年度报告', '年度', 'annual', 'report', '单位决算', '决算', '工作年报']
            is_report_link = any(keyword in text or keyword in href.lower() for keyword in keywords)
            # 特别标记"单位决算"链接，需要进入页面查找文档
            is_juesuan_link = '单位决算' in text or '决算' in text
            
            # 检查是否是PDF或DOCX文件
            is_pdf = (full_url.lower().endswith('.pdf') or href.lower().endswith('.pdf')) and not href.startswith('javascript:')
            is_docx = (full_url.lower().endswith('.docx') or href.lower().endswith('.docx')) and not href.startswith('javascript:')
            is_doc = (full_url.lower().endswith('.doc') or href.lower().endswith('.doc')) and not href.startswith('javascript:')
            # 优先从文本中提取年份，然后从URL参数中提取，最后从URL路径中提取
            year_in_text = extract_year_from_text(text)
            year_in_url_params = extract_year_from_url_params(full_url)
            year_in_url_path = extract_year_from_text(href)
            # 优先使用文本中的年份，然后是URL参数中的年份，最后是URL路径中的年份
            extracted_year = year_in_text or year_in_url_params or year_in_url_path
            
            # 如果包含年报关键词或者是PDF/DOCX，或者包含年份，都记录下来
            if is_report_link or is_pdf or is_docx or is_doc or extracted_year:
                all_links.append({
                    'url': full_url,
                    'text': text,
                    'year': extracted_year,
                    'is_pdf': is_pdf,
                    'is_docx': is_docx,
                    'is_doc': is_doc,
                    'is_report': is_report_link,
                    'is_juesuan': is_juesuan_link
                })
        
        # 尝试在页面文本中查找PDF URL（SPA应用可能将链接放在JavaScript或文本中）
        page_text = response.text
        pdf_url_pattern = r'https?://[^\s<>"\']+\.pdf'
        pdf_matches = re.findall(pdf_url_pattern, page_text, re.IGNORECASE)
        if pdf_matches:
            print(f"在页面文本中找到 {len(pdf_matches)} 个PDF URL")
            for pdf_url in pdf_matches:
                year = extract_year_from_text(pdf_url)
                if year == last_year_str:
                    print(f"✓ 在页面文本中找到去年的PDF URL: {pdf_url}")
                    return pdf_url, last_year_str
        
        # 打印所有找到的链接（用于调试）
        if all_links:
            print(f"找到 {len(all_links)} 个可能的链接")
            print("详细链接信息:")
            for link_info in all_links[:10]:  # 只显示前10个
                print(f"  - {link_info['text']} | 年份: {link_info['year']} | URL: {link_info['url'][:80]}")
        
        # 优先查找去年的年报
        last_year_links = []
        for link_info in all_links:
            # 更严格的年份匹配：必须完全匹配去年的年份
            if link_info['year'] == last_year_str:
                last_year_links.append(link_info)
        
        if last_year_links:
            # 优先选择PDF链接
            pdf_links = [link for link in last_year_links if link['is_pdf'] and link['url'].lower().endswith('.pdf')]
            if pdf_links:
                # 优先选择包含"年报"的PDF链接
                for link_info in pdf_links:
                    if '年报' in link_info['text'] or '年报' in link_info['url'] or '年度报告' in link_info['text']:
                        print(f"✓ 找到去年的年报PDF链接: {link_info['text']} (年份: {link_info['year']})")
                        print(f"  URL: {link_info['url']}")
                        return link_info['url'], link_info['year']
                # 如果没有明确标注"年报"的，返回第一个PDF链接
                print(f"✓ 找到去年的PDF链接: {pdf_links[0]['text']} (年份: {pdf_links[0]['year']})")
                print(f"  URL: {pdf_links[0]['url']}")
                return pdf_links[0]['url'], pdf_links[0]['year']
            
            # 如果没有PDF，尝试DOCX格式
            docx_links = [link for link in last_year_links if link['is_docx'] and link['url'].lower().endswith('.docx')]
            if docx_links:
                # 优先选择包含"年报"的DOCX链接
                for link_info in docx_links:
                    if '年报' in link_info['text'] or '年报' in link_info['url'] or '年度报告' in link_info['text']:
                        print(f"✓ 找到去年的年报DOCX链接: {link_info['text']} (年份: {link_info['year']})")
                        print(f"  URL: {link_info['url']}")
                        return link_info['url'], link_info['year']
                # 如果没有明确标注"年报"的，返回第一个DOCX链接
                print(f"✓ 找到去年的DOCX链接: {docx_links[0]['text']} (年份: {docx_links[0]['year']})")
                print(f"  URL: {docx_links[0]['url']}")
                return docx_links[0]['url'], docx_links[0]['year']
            
            # 如果没有DOCX，尝试DOC格式
            doc_links = [link for link in last_year_links if link['is_doc'] and link['url'].lower().endswith('.doc')]
            if doc_links:
                for link_info in doc_links:
                    if '年报' in link_info['text'] or '年报' in link_info['url'] or '年度报告' in link_info['text']:
                        print(f"✓ 找到去年的年报DOC链接: {link_info['text']} (年份: {link_info['year']})")
                        print(f"  URL: {link_info['url']}")
                        return link_info['url'], link_info['year']
                print(f"✓ 找到去年的DOC链接: {doc_links[0]['text']} (年份: {doc_links[0]['year']})")
                print(f"  URL: {doc_links[0]['url']}")
                return doc_links[0]['url'], doc_links[0]['year']
            
            # 优先处理"单位决算"链接，进入页面查找年报文档
            juesuan_links = [link for link in last_year_links if link.get('is_juesuan', False)]
            if juesuan_links:
                print(f"找到 {len(juesuan_links)} 个去年的单位决算链接，正在进入页面查找年报文档...")
                for link_info in juesuan_links:
                    print(f"访问单位决算页面: {link_info['text']}")
                    juesuan_url = link_info['url']
                    print(f"  URL: {juesuan_url}")
                    try:
                        link_response = session.get(juesuan_url, timeout=30, verify=False)
                        link_response.raise_for_status()
                        link_response.encoding = link_response.apparent_encoding or 'utf-8'
                        link_soup = BeautifulSoup(link_response.text, 'html.parser')
                        
                        # 在这个页面中查找文档链接（PDF/DOCX/DOC）
                        found_doc = False
                        doc_candidates = []  # 存储找到的文档候选
                        
                        for doc_link in link_soup.find_all('a', href=True):
                            doc_href = doc_link.get('href')
                            doc_text = doc_link.get_text().strip()
                            
                            if not doc_href or doc_href.startswith('javascript:') or doc_href.startswith('#'):
                                continue
                            
                            doc_full_url = urljoin(juesuan_url, doc_href)
                            
                            # 检查是否是文档文件（必须是真正的文档文件）
                            is_doc_file = (doc_full_url.lower().endswith(('.pdf', '.docx', '.doc')) or 
                                         doc_href.lower().endswith(('.pdf', '.docx', '.doc')))
                            
                            # 只处理真正的文档文件
                            if not is_doc_file:
                                continue
                            
                            # 检查是否包含年报相关关键词
                            doc_keywords = ['年报', '年度报告', '决算', '报告', '附件', '下载']
                            has_report_keyword = any(keyword in doc_text or keyword in doc_href.lower() for keyword in doc_keywords)
                            
                            # 检查年份
                            doc_year = extract_year_from_text(doc_text) or extract_year_from_text(doc_href) or extract_year_from_url_params(doc_full_url)
                            
                            # 记录所有找到的文档
                            doc_candidates.append({
                                'url': doc_full_url,
                                'text': doc_text,
                                'year': doc_year,
                                'has_keyword': has_report_keyword,
                                'is_pdf': doc_full_url.lower().endswith('.pdf')
                            })
                        
                        # 优先选择PDF格式且包含关键词的文档
                        for candidate in doc_candidates:
                            if candidate['is_pdf'] and candidate['has_keyword'] and (candidate['year'] == last_year_str or not candidate['year']):
                                print(f"✓ 在单位决算页面找到年报PDF: {candidate['text']}")
                                print(f"  URL: {candidate['url']}")
                                return candidate['url'], candidate['year'] or last_year_str
                        
                        # 其次选择任何PDF文档
                        for candidate in doc_candidates:
                            if candidate['is_pdf'] and (candidate['year'] == last_year_str or not candidate['year']):
                                print(f"✓ 在单位决算页面找到PDF文档: {candidate['text']}")
                                print(f"  URL: {candidate['url']}")
                                return candidate['url'], candidate['year'] or last_year_str
                        
                        # 最后选择其他格式的文档
                        for candidate in doc_candidates:
                            if candidate['has_keyword'] and (candidate['year'] == last_year_str or not candidate['year']):
                                print(f"✓ 在单位决算页面找到年报文档: {candidate['text']}")
                                print(f"  URL: {candidate['url']}")
                                return candidate['url'], candidate['year'] or last_year_str
                        
                        # 如果都没找到，尝试查找所有文档链接（不限制年份）
                        if doc_candidates:
                            # 优先PDF
                            for candidate in doc_candidates:
                                if candidate['is_pdf']:
                                    print(f"✓ 在单位决算页面找到PDF文档（未验证年份）: {candidate['text']}")
                                    print(f"  URL: {candidate['url']}")
                                    return candidate['url'], candidate['year'] or last_year_str
                            # 其他格式
                            print(f"✓ 在单位决算页面找到文档（未验证年份）: {doc_candidates[0]['text']}")
                            print(f"  URL: {doc_candidates[0]['url']}")
                            return doc_candidates[0]['url'], doc_candidates[0]['year'] or last_year_str
                        
                        # 如果没找到文档链接，尝试查找iframe或embed标签中的PDF
                        for iframe in link_soup.find_all(['iframe', 'embed']):
                            src = iframe.get('src') or iframe.get('data-src')
                            if src:
                                iframe_url = urljoin(juesuan_url, src)
                                if iframe_url.lower().endswith(('.pdf', '.docx', '.doc')):
                                    print(f"✓ 在单位决算页面找到文档（iframe）: {iframe_url}")
                                    return iframe_url, last_year_str
                        
                        # 尝试在页面文本中查找PDF URL（可能以文本形式存在）
                        page_text = link_soup.get_text()
                        pdf_url_pattern = r'https?://[^\s<>"]+\.pdf'
                        pdf_matches = re.findall(pdf_url_pattern, page_text, re.IGNORECASE)
                        if pdf_matches:
                            for pdf_url in pdf_matches:
                                if last_year_str in pdf_url:
                                    print(f"✓ 在单位决算页面文本中找到PDF URL: {pdf_url}")
                                    return pdf_url, last_year_str
                        
                        if not doc_candidates:
                            print(f"  在单位决算页面未找到文档链接")
                    except Exception as e:
                        print(f"  访问单位决算页面失败: {e}")
                        continue
            
            # 如果没有找到直接的文档链接，尝试根据年份构建URL
            possible_formats = [
                f"{last_year_str}年报.pdf",
                f"{last_year_str}年度报告.pdf",
                f"{last_year_str}年报.docx",
                f"{last_year_str}年度报告.docx",
                f"{last_year_str}年报.doc",
                f"{last_year_str}年度报告.doc",
            ]
            
            print(f"未找到直接的文档链接，尝试构建可能的URL...")
            for doc_filename in possible_formats:
                possible_doc_url = f"{base_url}/{doc_filename}"
                print(f"尝试访问可能的文档链接: {possible_doc_url}")
                try:
                    test_response = session.head(possible_doc_url, timeout=10, verify=False, allow_redirects=True)
                    if test_response.status_code == 200:
                        content_type = test_response.headers.get('Content-Type', '').lower()
                        if 'pdf' in content_type or 'word' in content_type or 'document' in content_type or possible_doc_url.lower().endswith(('.pdf', '.docx', '.doc')):
                            print(f"✓ 找到去年的年报文档链接 (年份: {last_year_str})")
                            print(f"  URL: {possible_doc_url}")
                            return possible_doc_url, last_year_str
                except:
                    try:
                        test_response = session.get(possible_doc_url, timeout=10, verify=False, allow_redirects=True, stream=True)
                        if test_response.status_code == 200:
                            content_type = test_response.headers.get('Content-Type', '').lower()
                            if 'pdf' in content_type or 'word' in content_type or 'document' in content_type:
                                print(f"✓ 找到去年的年报文档链接 (年份: {last_year_str})")
                                print(f"  URL: {possible_doc_url}")
                                return possible_doc_url, last_year_str
                    except:
                        pass
            
            # 如果构建URL失败，尝试访问找到的链接，看看是否能找到文档
            # 注意：单位决算链接已经在前面处理过了，这里只处理其他链接
            print(f"构建URL失败，尝试访问找到的其他链接页面查找文档...")
            for link_info in last_year_links:
                # 跳过已经处理过的单位决算链接
                if link_info.get('is_juesuan', False):
                    continue
                    
                if '年报' in link_info['text'] or '年度报告' in link_info['text']:
                    # 如果链接不是文档格式，访问这个链接看看
                    if not link_info['url'].lower().endswith(('.docx', '.doc', '.pdf')):
                        print(f"访问链接页面: {link_info['url']}")
                        try:
                            link_response = session.get(link_info['url'], timeout=30, verify=False)
                            link_response.raise_for_status()
                            link_response.encoding = link_response.apparent_encoding or 'utf-8'
                            link_soup = BeautifulSoup(link_response.text, 'html.parser')
                            
                            # 在这个页面中查找文档链接
                            for doc_link in link_soup.find_all('a', href=True):
                                doc_href = doc_link.get('href')
                                if doc_href and (doc_href.lower().endswith(('.pdf', '.docx', '.doc'))):
                                    doc_full_url = urljoin(link_info['url'], doc_href)
                                    # 检查是否包含年份
                                    if last_year_str in doc_full_url or last_year_str in doc_link.get_text():
                                        print(f"✓ 在链接页面找到文档: {doc_link.get_text().strip()}")
                                        print(f"  URL: {doc_full_url}")
                                        return doc_full_url, last_year_str
                        except Exception as e:
                            print(f"  访问链接页面失败: {e}")
                            continue
            
            # 如果还是没有找到，返回第一个有效的去年的文档链接（必须是文档文件，不能是HTML页面）
            valid_doc_links = [link for link in last_year_links 
                             if not link['url'].startswith('javascript:') 
                             and (link['is_pdf'] or link['is_docx'] or link['is_doc'])]
            if valid_doc_links:
                print(f"✓ 找到去年的文档链接: {valid_doc_links[0]['text']} (年份: {valid_doc_links[0]['year']})")
                return valid_doc_links[0]['url'], valid_doc_links[0]['year']
        
        # 如果没有找到去年的年报，列出所有找到的链接供参考
        report_links = [link for link in all_links if (link['is_pdf'] or link['is_docx'] or link['is_doc'] or link['is_report']) and ('年报' in link['text'] or '年报' in link['url'])]
        if report_links:
            print(f"\n⚠️  未找到 {last_year} 年的年报，但找到其他年份的年报:")
            for link_info in report_links:
                print(f"    {link_info['text']} (年份: {link_info['year'] or '未知年份'})")
            print(f"\n✗ 未找到 {last_year} 年的年报，下载失败")
        else:
            print("✗ 未找到年报链接")
        
        return None
        
    except Exception as e:
        print(f"✗ 查找年报链接失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        session.close()

def save_page_as_pdf(driver, url, filename, save_dir):
    """使用Selenium将网页保存为PDF"""
    try:
        print(f"正在将网页保存为PDF: {url}")
        
        # 第一步：滚动页面加载所有内容
        print("  正在滚动页面加载所有内容...")
        
        # 等待页面初始加载
        try:
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except:
            pass
        
        time.sleep(2)
        
        # 获取页面总高度
        last_height = driver.execute_script("return document.body.scrollHeight")
        print(f"  页面初始高度: {last_height}px")
        
        # 滚动到顶部
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # 检查并点击"加载更多"、"查看更多"等按钮
        print("  检查是否有'加载更多'按钮...")
        load_more_keywords = ['加载更多', '查看更多', '显示更多', '展开', '更多']
        for keyword in load_more_keywords:
            try:
                buttons = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
                for btn in buttons:
                    try:
                        if btn.is_displayed() and btn.is_enabled():
                            print(f"  找到并点击'{keyword}'按钮")
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(2)
                    except:
                        continue
            except:
                pass
        
        # 更彻底的滚动策略：多次完整滚动，确保所有内容加载
        print("  开始第一次完整滚动...")
        
        # 第一次：快速滚动到底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        height_after_first = driver.execute_script("return document.body.scrollHeight")
        print(f"  第一次滚动后页面高度: {height_after_first}px")
        
        # 第二次：逐步滚动，更细致地加载
        print("  开始第二次逐步滚动...")
        scroll_step = 300  # 减小步长，更细致
        current_position = 0
        no_change_count = 0
        max_no_change = 5  # 连续5次高度不变才停止
        
        while no_change_count < max_no_change:
            # 滚动到当前位置
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(1)  # 增加等待时间
            
            # 更新当前位置
            current_position += scroll_step
            
            # 获取新的页面高度
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # 如果已经滚动到底部
            if current_position >= new_height:
                # 滚动到底部
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)  # 增加等待时间
                
                # 再次检查页面高度
                final_height = driver.execute_script("return document.body.scrollHeight")
                if final_height > new_height:
                    print(f"  检测到新内容加载，页面高度: {final_height}px")
                    current_position = new_height
                    new_height = final_height
                    no_change_count = 0  # 重置计数器
                else:
                    no_change_count += 1
                    if no_change_count < max_no_change:
                        # 还没到最大次数，继续尝试
                        current_position = 0  # 重新从顶部开始
                        print(f"  重新从顶部开始滚动（第{no_change_count+1}次）...")
                        time.sleep(1)
                    else:
                        break
            else:
                # 检查高度是否变化
                if new_height > last_height:
                    last_height = new_height
                    no_change_count = 0
                else:
                    no_change_count += 1
            
            # 显示进度
            if current_position % 3000 == 0 or current_position >= new_height:
                print(f"  已滚动到: {min(current_position, new_height)}px / {new_height}px")
        
        # 第三次：非常慢速的完整滚动，确保所有内容都被触发加载
        print("  开始第三次慢速完整滚动...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        final_height = driver.execute_script("return document.body.scrollHeight")
        scroll_increment = 100  # 更小的步长，更细致
        print(f"  使用步长 {scroll_increment}px 进行细致滚动...")
        
        # 从0滚动到最终高度+额外空间
        for pos in range(0, final_height + 2000, scroll_increment):
            driver.execute_script(f"window.scrollTo(0, {pos});")
            time.sleep(0.5)  # 增加等待时间，确保内容加载
            
            # 每滚动1000px检查一次页面高度
            if pos % 1000 == 0:
                current_height = driver.execute_script("return document.body.scrollHeight")
                if current_height > final_height:
                    print(f"  检测到页面高度增加到: {current_height}px")
                    final_height = current_height
        
        # 最后滚动到底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)  # 增加等待时间
        
        # 再次检查最终高度
        ultimate_height = driver.execute_script("return document.body.scrollHeight")
        if ultimate_height > final_height:
            print(f"  最终检测到新内容，页面高度: {ultimate_height}px")
            # 再完整滚动一次
            print("  进行第四次完整滚动...")
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            for pos in range(0, ultimate_height + 2000, scroll_increment):
                driver.execute_script(f"window.scrollTo(0, {pos});")
                time.sleep(0.4)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)
            
            # 再次检查
            final_ultimate_height = driver.execute_script("return document.body.scrollHeight")
            if final_ultimate_height > ultimate_height:
                print(f"  再次检测到新内容，页面高度: {final_ultimate_height}px")
                ultimate_height = final_ultimate_height
        
        final_page_height = driver.execute_script("return document.body.scrollHeight")
        print(f"  最终页面高度: {final_page_height}px")
        
        # 检查并点击"加载更多"、"查看更多"等按钮
        print("  检查是否有'加载更多'按钮...")
        load_more_keywords = ['加载更多', '查看更多', '显示更多', '展开', '更多', 'Load More', 'Show More']
        clicked_any = False
        for keyword in load_more_keywords:
            try:
                buttons = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
                for btn in buttons:
                    try:
                        if btn.is_displayed() and btn.is_enabled():
                            print(f"  找到并点击'{keyword}'按钮")
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(3)
                            clicked_any = True
                            # 点击后再次滚动到底部
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(2)
                            # 检查高度是否增加
                            new_height = driver.execute_script("return document.body.scrollHeight")
                            if new_height > final_page_height:
                                print(f"  点击后页面高度增加到: {new_height}px")
                                final_page_height = new_height
                    except:
                        continue
            except:
                pass
        
        # 如果点击了按钮，再次完整滚动
        if clicked_any:
            print("  检测到新内容，再次完整滚动...")
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            scroll_increment = 200
            for pos in range(0, final_page_height + 500, scroll_increment):
                driver.execute_script(f"window.scrollTo(0, {pos});")
                time.sleep(0.2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            final_page_height = driver.execute_script("return document.body.scrollHeight")
            print(f"  再次滚动后页面高度: {final_page_height}px")
        
        # 滚动回顶部，确保PDF从顶部开始
        print("  滚动回顶部...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # 处理iframe中的内容（如果有）
        print("  检查是否有iframe需要处理...")
        try:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                print(f"  找到 {len(iframes)} 个iframe")
                for i, iframe in enumerate(iframes):
                    try:
                        driver.switch_to.frame(iframe)
                        iframe_height = driver.execute_script("return document.body.scrollHeight")
                        print(f"  iframe {i+1} 高度: {iframe_height}px")
                        # 滚动iframe内容
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        driver.switch_to.default_content()
                    except:
                        driver.switch_to.default_content()
                        continue
        except:
            pass
        
        # 等待所有图片和资源加载完成
        print("  等待所有资源加载完成...")
        try:
            # 等待所有图片加载
            driver.execute_script("""
                var images = document.getElementsByTagName('img');
                var promises = [];
                for (var i = 0; i < images.length; i++) {
                    if (!images[i].complete) {
                        var promise = new Promise(function(resolve) {
                            images[i].onload = resolve;
                            images[i].onerror = resolve;
                        });
                        promises.push(promise);
                    }
                }
                return Promise.all(promises);
            """)
            time.sleep(5)  # 增加等待时间
        except:
            pass
        
        # 最后一次完整滚动，确保所有内容都在视口中被渲染
        print("  进行最后一次完整滚动以确保所有内容被渲染...")
        final_height_before_save = driver.execute_script("return document.body.scrollHeight")
        print(f"  保存前页面高度: {final_height_before_save}px")
        
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # 非常慢速地滚动，确保每个部分都被渲染
        scroll_step_final = 50  # 非常小的步长
        for pos in range(0, final_height_before_save + 1000, scroll_step_final):
            driver.execute_script(f"window.scrollTo(0, {pos});")
            time.sleep(0.1)  # 短暂等待，让浏览器渲染
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # 最终等待，确保所有内容都加载完成
        print("  最终等待所有内容加载...")
        time.sleep(8)  # 增加最终等待时间
        
        # 最后一次检查页面高度
        final_check_height = driver.execute_script("return document.body.scrollHeight")
        print(f"  最终检查页面高度: {final_check_height}px")
        
        # 如果高度又增加了，再滚动一次
        if final_check_height > final_page_height:
            print(f"  检测到最终高度增加，再次滚动...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
        
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
                print(f"  已删除已存在的文件: {filename}")
            except:
                pass
        
        # 使用Chrome的打印功能保存为PDF
        print(f"  正在将页面保存为PDF（包含所有内容）...")
        
        # 计算所需的纸张高度（根据页面内容高度）
        page_height_px = driver.execute_script("return document.body.scrollHeight")
        # 转换为英寸（假设96 DPI，1英寸=96像素）
        # 增加一些余量，确保所有内容都能打印
        required_height_inches = (page_height_px / 96) * 1.1  # 增加10%的余量
        # 最小使用A4高度，最大不超过200英寸（防止过大）
        paper_height = max(11.69, min(required_height_inches, 200))
        
        print(f"  页面内容高度: {page_height_px}px ({page_height_px/96:.2f}英寸)")
        print(f"  使用纸张高度: {paper_height:.2f}英寸")
        
        # 设置打印选项
        print_options = {
            'printBackground': True,  # 包含背景图片和颜色
            'paperWidth': 8.27,  # A4宽度（英寸）
            'paperHeight': paper_height,  # 根据内容动态调整高度
            'marginTop': 0.4,
            'marginBottom': 0.4,
            'marginLeft': 0.4,
            'marginRight': 0.4,
            'preferCSSPageSize': False,  # 不使用CSS页面大小
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
            print(f"✗ PDF保存失败: {file_path}")
            return False
        
        file_size = os.path.getsize(file_path)
        
        if file_size < 1024:
            print(f"✗ 文件大小异常小 ({file_size} 字节)，可能是错误页面")
            os.remove(file_path)
            return False
        
        print(f"✓ PDF保存成功: {filename}")
        print(f"  文件大小: {file_size:,} 字节 ({file_size/1024/1024:.2f} MB)")
        print(f"  保存路径: {file_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ 保存PDF失败: {e}")
        import traceback
        traceback.print_exc()
        return False

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
    print("内蒙古图书馆年报下载工具")
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
    
    # 获取去年的年份（动态计算）
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    target_year = str(last_year)
    
    # 内蒙古图书馆年报页面URL
    report_page_url = "https://www.nmglib.com/#/GongZuoNianBao"
    base_url = "https://www.nmglib.com"
    
    print(f"目标年份: {target_year}年（严格匹配，只下载{target_year}年的年报）")
    print(f"输出路径: {output_folder}")
    print("-" * 60)
    
    # 查找年报链接
    result = find_last_year_report(report_page_url, base_url)
    
    if not result:
        print(f"\n✗ 未找到 {target_year} 年的年报链接，下载失败")
        return
    
    # 处理返回值：可能是(url, year)元组、(url, year, driver, 'save_as_pdf')或只有url
    driver_to_close = None
    if isinstance(result, tuple):
        if len(result) == 4 and result[3] == 'save_as_pdf':
            # 需要保存页面为PDF的情况
            file_url, actual_year, driver_to_close, _ = result
            # 严格验证年份
            if actual_year != target_year:
                print(f"✗ 错误：找到的是 {actual_year} 年的年报，不是 {target_year} 年的")
                print(f"  为了确保年份准确，拒绝下载")
                if driver_to_close:
                    driver_to_close.quit()
                return
            year_for_filename = target_year
            
            # 生成文件名
            filename = f"内蒙古图书馆{year_for_filename}年年报.pdf"
            filename = clean_filename(filename)
            
            print(f"\n文件名: {filename}")
            print("-" * 60)
            
            # 保存页面为PDF
            success = save_page_as_pdf(driver_to_close, file_url, filename, output_folder)
            
            # 关闭driver
            if driver_to_close:
                driver_to_close.quit()
            
            if success:
                print("\n" + "=" * 60)
                print("✓ 保存完成")
                print("=" * 60)
                print(f"文件已保存到: {os.path.join(output_folder, filename)}")
            else:
                print("\n" + "=" * 60)
                print("✗ 保存失败")
                print("=" * 60)
            return
        else:
            # 普通的(url, year)元组
            file_url, actual_year = result
            # 严格验证年份
            if actual_year != target_year:
                print(f"✗ 错误：找到的是 {actual_year} 年的年报，不是 {target_year} 年的")
                print(f"  为了确保年份准确，拒绝下载")
                return
            year_for_filename = target_year
    else:
        file_url = result
        # 如果返回的只有URL，验证URL中是否包含目标年份
        if target_year not in file_url:
            print(f"✗ 错误：URL中不包含 {target_year} 年，拒绝下载")
            print(f"  URL: {file_url}")
            return
        year_for_filename = target_year
    
    # 生成文件名，使用实际找到的年份
    # 根据URL确定文件扩展名
    if file_url.lower().endswith('.docx'):
        file_ext = '.docx'
    elif file_url.lower().endswith('.doc'):
        file_ext = '.doc'
    elif file_url.lower().endswith('.pdf'):
        file_ext = '.pdf'
    else:
        file_ext = '.pdf'  # 默认使用pdf
    
    filename = f"内蒙古图书馆{year_for_filename}年年报{file_ext}"
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

