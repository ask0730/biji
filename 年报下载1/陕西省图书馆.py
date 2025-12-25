#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
陕西省图书馆决算报告下载工具
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
    """在页面中查找去年的决算报告PDF链接"""
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
        
        # 第一步：访问起始页面
        print(f"正在访问起始页面: {url}")
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
        
        # 第二步：查找包含"年部门所属单位决算"的链接
        print(f"\n查找包含'年部门所属单位决算'的链接...")
        juesuan_link = None
        juesuan_text = None
        
        try:
            all_links = driver.find_elements(By.XPATH, "//a[@href]")
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    title_attr = link.get_attribute('title') or ''
                    combined_text = text + ' ' + title_attr
                    
                    # 检查是否包含"年部门所属单位决算"
                    if '年部门所属单位决算' in combined_text:
                        juesuan_link = href
                        juesuan_text = text or title_attr
                        print(f"✓ 找到决算链接: {juesuan_text}")
                        print(f"  链接: {href}")
                        break
                except:
                    continue
        except Exception as e:
            print(f"  查找链接时出错: {e}")
        
        if not juesuan_link:
            print("✗ 未找到'年部门所属单位决算'链接")
            return None
        
        # 第三步：进入决算页面
        print(f"\n正在访问决算页面...")
        if juesuan_link.startswith('/'):
            juesuan_url = urljoin(base_url, juesuan_link)
        elif not juesuan_link.startswith('http'):
            juesuan_url = urljoin(base_url, '/' + juesuan_link)
        else:
            juesuan_url = juesuan_link
        
        print(f"  决算页面URL: {juesuan_url}")
        driver.get(juesuan_url)
        time.sleep(3)
        
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            print("  页面加载超时，继续尝试...")
        
        time.sleep(2)
        
        # 第四步：查找包含"图书馆"的链接
        print(f"\n查找包含'图书馆'的链接...")
        library_link = None
        library_text = None
        
        try:
            all_links = driver.find_elements(By.XPATH, "//a[@href]")
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    title_attr = link.get_attribute('title') or ''
                    combined_text = text + ' ' + title_attr
                    
                    # 检查是否包含"图书馆"
                    if '图书馆' in combined_text:
                        library_link = href
                        library_text = text or title_attr
                        print(f"✓ 找到图书馆链接: {library_text}")
                        print(f"  链接: {href}")
                        break
                except:
                    continue
        except Exception as e:
            print(f"  查找链接时出错: {e}")
        
        if not library_link:
            print("✗ 未找到'图书馆'链接")
            return None
        
        # 第五步：进入图书馆页面
        print(f"\n正在访问图书馆页面...")
        if library_link.startswith('/'):
            library_url = urljoin(base_url, library_link)
        elif not library_link.startswith('http'):
            library_url = urljoin(juesuan_url, library_link)
        else:
            library_url = library_link
        
        print(f"  图书馆页面URL: {library_url}")
        driver.get(library_url)
        time.sleep(3)
        
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            print("  页面加载超时，继续尝试...")
        
        time.sleep(2)
        
        # 第六步：读取页面源码，查找PDF链接
        print(f"\n读取页面源码，查找PDF链接...")
        pdf_url = None
        
        # 方法1: 直接查找PDF链接元素
        try:
            pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
            if pdf_links:
                for link in pdf_links:
                    try:
                        href = link.get_attribute('href')
                        if href:
                            if href.startswith('http'):
                                pdf_url = href
                            elif href.startswith('/'):
                                pdf_url = urljoin(base_url, href)
                            else:
                                pdf_url = urljoin(library_url, href)
                            print(f"✓ 找到PDF链接: {href}")
                            break
                    except:
                        continue
        except Exception as e:
            print(f"  查找PDF链接元素时出错: {e}")
        
        # 方法2: 在页面源码中查找PDF链接
        if not pdf_url:
            print("  在页面源码中查找PDF链接...")
            try:
                page_source = driver.page_source
                pdf_patterns = [
                    r'href=["\']([^"\']*\.pdf)["\']',
                    r'["\']([^"\']*\.pdf)["\']',
                    r'https?://[^\s<>"\'\)]+\.pdf',
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
                                pdf_url = urljoin(library_url, pdf_path)
                            print(f"✓ 在页面源码中找到PDF: {pdf_url}")
                            break
                    
                    if pdf_url:
                        break
            except Exception as e:
                print(f"  在页面源码中查找时出错: {e}")
        
        # 方法3: 查找包含"下载"的链接
        if not pdf_url:
            print("  尝试查找包含'下载'的链接...")
            try:
                download_links = driver.find_elements(By.XPATH, "//a[contains(text(), '下载')]")
                for link in download_links:
                    try:
                        href = link.get_attribute('href')
                        if href and '.pdf' in href.lower():
                            if href.startswith('http'):
                                pdf_url = href
                            elif href.startswith('/'):
                                pdf_url = urljoin(base_url, href)
                            else:
                                pdf_url = urljoin(library_url, href)
                            print(f"✓ 找到下载链接: {pdf_url}")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"  查找下载链接时出错: {e}")
        
        if pdf_url:
            # 尝试从URL或页面文本中提取年份
            extracted_year = extract_year_from_text(driver.page_source)
            if extracted_year:
                return pdf_url, extracted_year
            else:
                return pdf_url, last_year_str
        
        print("✗ 未找到PDF链接")
        return None
        
    except Exception as e:
        print(f"✗ 查找决算报告链接失败: {e}")
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
    print("陕西省图书馆决算报告下载工具")
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
    
    # 陕西省财政厅页面URL
    report_page_url = "https://czt.shaanxi.gov.cn/xxgk/zdgk/zdly/snyjsgkpt/bmssdwyjs/"
    base_url = "https://czt.shaanxi.gov.cn"
    
    print(f"目标年份: {last_year}年")
    print(f"起始页面URL: {report_page_url}")
    print(f"输出路径: {output_folder}")
    print("-" * 60)
    
    # 查找决算报告PDF链接
    result = find_last_year_report(report_page_url, base_url)
    
    if not result:
        print("\n✗ 未找到陕西省图书馆的决算报告PDF链接，下载失败")
        return
    
    # 处理返回值：可能是(url, year)元组或只有url
    if isinstance(result, tuple):
        file_url, actual_year = result
        if actual_year and actual_year != last_year_str:
            print(f"⚠️  注意：找到的是 {actual_year} 年的决算报告，不是 {last_year_str} 年的")
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
    
    filename = f"陕西省图书馆{year_for_filename}年决算报告{file_ext}"
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

