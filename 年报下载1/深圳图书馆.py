#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
深圳图书馆年报下载工具
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
    """在页面源码中查找去年的年报PDF链接"""
    # 获取去年的年份
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    last_year_str = str(last_year)
    
    if not SELENIUM_AVAILABLE:
        print("✗ Selenium未安装，无法访问页面")
        return None
    
    driver = None
    try:
        print("正在使用浏览器访问页面...")
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
        
        print(f"\n查找 {last_year} 年的年报PDF链接...")
        print("  正在读取页面源码...")
        
        # 获取页面源码
        page_source = driver.page_source
        
        # 查找PDF链接
        keywords = ['年报', '年度报告', '年度', '报告']
        pdf_urls = []
        
        # 方法1: 查找所有PDF链接
        pdf_patterns = [
            r'href=["\']([^"\']*\.pdf)["\']',  # href="xxx.pdf"
            r'["\']([^"\']*\.pdf)["\']',       # "xxx.pdf"
            r'https?://[^\s<>"\'\)]+\.pdf',    # http://xxx.pdf
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
                    # 转换为绝对URL
                    if pdf_path.startswith('http'):
                        pdf_url = pdf_path
                    elif pdf_path.startswith('/'):
                        pdf_url = urljoin(base_url, pdf_path)
                    else:
                        pdf_url = urljoin(url, pdf_path)
                    
                    # 检查URL中是否包含年份
                    if last_year_str in pdf_url:
                        pdf_urls.append(pdf_url)
                        print(f"✓ 找到PDF链接（URL包含年份）: {pdf_url}")
        
        # 方法2: 查找包含年份和关键词的文本附近的PDF链接
        # 查找包含去年年份和关键词的文本元素
        try:
            text_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{last_year_str}')]")
            for element in text_elements:
                try:
                    text = element.text.strip()
                    if not text or len(text) < 5:
                        continue
                    
                    # 检查是否包含年报关键词
                    if any(kw in text for kw in keywords):
                        print(f"✓ 找到年报项: {text}")
                        
                        # 在该元素附近查找PDF链接
                        try:
                            # 查找父元素中的链接
                            parent = element.find_element(By.XPATH, "./..")
                            parent_html = parent.get_attribute('outerHTML')
                            
                            # 在父元素HTML中查找PDF链接
                            parent_pdf_matches = re.findall(r'href=["\']([^"\']*\.pdf)["\']', parent_html, re.IGNORECASE)
                            for pdf_path in parent_pdf_matches:
                                if pdf_path.lower().endswith('.pdf'):
                                    if pdf_path.startswith('http'):
                                        pdf_url = pdf_path
                                    elif pdf_path.startswith('/'):
                                        pdf_url = urljoin(base_url, pdf_path)
                                    else:
                                        pdf_url = urljoin(url, pdf_path)
                                    
                                    if pdf_url not in pdf_urls:
                                        pdf_urls.append(pdf_url)
                                        print(f"✓ 找到PDF链接（在年报项附近）: {pdf_url}")
                        except:
                            pass
                        
                        # 查找同一行的链接
                        try:
                            row = element.find_element(By.XPATH, "./ancestor::tr | ./ancestor::div[contains(@class, 'item')] | ./ancestor::li")
                            row_html = row.get_attribute('outerHTML')
                            
                            row_pdf_matches = re.findall(r'href=["\']([^"\']*\.pdf)["\']', row_html, re.IGNORECASE)
                            for pdf_path in row_pdf_matches:
                                if pdf_path.lower().endswith('.pdf'):
                                    if pdf_path.startswith('http'):
                                        pdf_url = pdf_path
                                    elif pdf_path.startswith('/'):
                                        pdf_url = urljoin(base_url, pdf_path)
                                    else:
                                        pdf_url = urljoin(url, pdf_path)
                                    
                                    if pdf_url not in pdf_urls:
                                        pdf_urls.append(pdf_url)
                                        print(f"✓ 找到PDF链接（在同一行）: {pdf_url}")
                        except:
                            pass
                except:
                    continue
        except Exception as e:
            print(f"  查找年报项时出错: {e}")
        
        # 方法3: 查找所有链接元素，检查其文本和href
        try:
            all_links = driver.find_elements(By.XPATH, "//a[@href]")
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    title_attr = link.get_attribute('title') or ''
                    combined_text = text + ' ' + title_attr
                    
                    if href and '.pdf' in href.lower():
                        # 检查链接文本或URL中是否包含年份和关键词
                        has_keyword = any(kw in combined_text for kw in keywords)
                        has_year = last_year_str in combined_text or last_year_str in href
                        
                        if has_keyword and has_year:
                            if href.startswith('http'):
                                pdf_url = href
                            elif href.startswith('/'):
                                pdf_url = urljoin(base_url, href)
                            else:
                                pdf_url = urljoin(url, href)
                            
                            if pdf_url not in pdf_urls:
                                pdf_urls.append(pdf_url)
                                print(f"✓ 找到PDF链接（通过链接元素）: {text or title_attr or pdf_url}")
                except:
                    continue
        except Exception as e:
            print(f"  查找链接元素时出错: {e}")
        
        # 如果找到多个PDF链接，优先选择包含年份的
        if pdf_urls:
            # 优先选择URL中包含年份的
            for pdf_url in pdf_urls:
                if last_year_str in pdf_url:
                    print(f"\n选择PDF链接: {pdf_url}")
                    return pdf_url, last_year_str
            
            # 如果没有包含年份的，返回第一个
            print(f"\n选择PDF链接: {pdf_urls[0]}")
            return pdf_urls[0], last_year_str
        
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
    print("深圳图书馆年报下载工具")
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
    
    # 深圳图书馆年报页面URL
    report_page_url = "https://www.szlib.org.cn/work-report-article/work-report.html"
    base_url = "https://www.szlib.org.cn"
    
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
    
    filename = f"深圳图书馆{year_for_filename}年年报{file_ext}"
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

