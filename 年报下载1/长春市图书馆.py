#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
长春市图书馆年报下载工具
"""

import os
import re
import time
import requests
from urllib.parse import urljoin, urlparse

# 尝试导入Selenium相关模块
SELENIUM_AVAILABLE = False
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    SELENIUM_AVAILABLE = True
except ImportError:
    print("警告: 未安装selenium，将无法使用浏览器自动化功能")

def get_headers():
    """获取请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def clean_filename(filename):
    """清理文件名，移除非法字符"""
    # 移除Windows文件名不允许的字符
    illegal_chars = r'[<>:"/\\|?*]'
    filename = re.sub(illegal_chars, '_', filename)
    # 移除多余的空格
    filename = re.sub(r'\s+', ' ', filename).strip()
    return filename

def extract_year_from_text(text):
    """从文本中提取年份"""
    if not text:
        return None
    # 查找4位数字年份（1900-2099）
    matches = re.findall(r'(19|20)\d{2}', text)
    if matches:
        return matches[-1]  # 返回最后一个匹配的年份
    return None

def extract_year_from_url_params(url):
    """从URL参数中提取年份"""
    if not url:
        return None
    matches = re.findall(r'(?:year|y|date)=(\d{4})', url, re.IGNORECASE)
    if matches:
        return matches[-1]
    return None

def load_config(config_path):
    """加载配置文件"""
    if not os.path.exists(config_path):
        print(f"✗ 配置文件不存在: {config_path}")
        print("  请创建配置文件并设置 output_folder 路径")
        return None
    
    config = {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        return config
    except Exception as e:
        print(f"✗ 读取配置文件失败: {e}")
        return None

def setup_driver():
    """设置并返回Selenium WebDriver"""
    if not SELENIUM_AVAILABLE:
        print("✗ Selenium未安装，无法使用浏览器自动化功能")
        return None
    
    try:
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
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
        print("  正在查找'长春市图书馆'（排除少年儿童图书馆）的文档链接...")
        
        # 查找包含去年年份和"长春市图书馆"的链接（排除"少年儿童图书馆"）
        keywords = ['年报', '年度报告', '年度', '报告']
        exclude_keywords = ['少年儿童', '少儿']
        library_report_link = None
        library_report_text = None
        
        try:
            # 方法1: 查找包含"图书馆"和去年年份的链接，但排除"少年儿童图书馆"
            all_links = driver.find_elements(By.XPATH, "//a[@href]")
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    title_attr = link.get_attribute('title') or ''
                    combined_text = text + ' ' + title_attr + ' ' + (href or '')
                    
                    # 检查是否包含"图书馆"、关键词和去年年份
                    has_library = '图书馆' in combined_text
                    has_keyword = any(kw in combined_text for kw in keywords)
                    has_year = last_year_str in combined_text
                    # 排除"少年儿童图书馆"
                    is_excluded = any(exclude_kw in combined_text for exclude_kw in exclude_keywords)
                    
                    if has_library and has_keyword and has_year and not is_excluded:
                        # 如果是PDF链接，直接返回
                        if href.lower().endswith('.pdf'):
                            print(f"✓ 找到PDF链接: {text or title_attr or href}")
                            print(f"  链接: {href}")
                            return href, last_year_str
                        # 否则记录为详情页链接
                        else:
                            library_report_link = href
                            library_report_text = text or title_attr
                            print(f"✓ 找到文档链接: {library_report_text}")
                            print(f"  链接: {href}")
                            break
                except:
                    continue
        except Exception as e:
            print(f"  查找链接时出错: {e}")
        
        # 如果没找到，尝试只查找包含"图书馆"和年份的链接（不要求关键词，但排除少年儿童）
        if not library_report_link:
            print("  尝试查找包含'图书馆'和年份的链接（排除少年儿童图书馆）...")
            try:
                all_links = driver.find_elements(By.XPATH, "//a[@href]")
                for link in all_links:
                    try:
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        title_attr = link.get_attribute('title') or ''
                        combined_text = text + ' ' + title_attr + ' ' + (href or '')
                        
                        # 检查是否包含"图书馆"和去年年份，但排除"少年儿童图书馆"
                        has_library = '图书馆' in combined_text
                        has_year = last_year_str in combined_text
                        is_excluded = any(exclude_kw in combined_text for exclude_kw in exclude_keywords)
                        
                        if has_library and has_year and not is_excluded:
                            # 如果是PDF链接，直接返回
                            if href.lower().endswith('.pdf'):
                                print(f"✓ 找到PDF链接: {text or title_attr or href}")
                                print(f"  链接: {href}")
                                return href, last_year_str
                            # 否则记录为详情页链接
                            else:
                                library_report_link = href
                                library_report_text = text or title_attr
                                print(f"✓ 找到文档链接: {library_report_text}")
                                print(f"  链接: {href}")
                                break
                    except:
                        continue
            except Exception as e:
                print(f"  查找链接时出错: {e}")
        
        # 如果找到文档链接，进入详情页查找PDF
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
                
            except Exception as e:
                print(f"  访问详情页失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 如果列表页直接有PDF链接，也尝试查找
        print("  尝试在列表页直接查找PDF链接（排除少年儿童图书馆）...")
        try:
            pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
            for link in pdf_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    title_attr = link.get_attribute('title') or ''
                    combined_text = text + ' ' + title_attr + ' ' + (href or '')
                    
                    # 检查是否包含"图书馆"和年份，但排除"少年儿童图书馆"
                    has_library = '图书馆' in combined_text
                    has_year = last_year_str in combined_text
                    is_excluded = any(exclude_kw in combined_text for exclude_kw in ['少年儿童', '少儿'])
                    
                    if href and has_library and has_year and not is_excluded:
                        print(f"✓ 找到PDF链接: {text or title_attr or href}")
                        return href, last_year_str
                except:
                    continue
        except:
            pass
        
        print("✗ 未找到年报链接")
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
    print("长春市图书馆年报下载工具")
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
    
    # 长春市图书馆年报页面URL
    report_page_url = "http://wglj.changchun.gov.cn/zgxxgk_44800/zfxxgkzl/czyjsgk/"
    base_url = "http://wglj.changchun.gov.cn"
    
    print(f"目标年份: {last_year}年")
    print(f"页面URL: {report_page_url}")
    print(f"输出路径: {output_folder}")
    print("-" * 60)
    
    # 查找年报PDF链接
    result = find_last_year_report(report_page_url, base_url)
    
    if not result:
        print("\n✗ 未找到年报PDF链接，下载失败")
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
    
    filename = f"长春市图书馆{year_for_filename}年年报{file_ext}"
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

