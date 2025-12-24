# -*- coding: utf-8 -*-
"""
大连图书馆年报下载脚本
功能：从大连图书馆官网下载去年的年报，并重命名为"大连图书馆年份年报"格式
"""

import requests
import os
import time
import re
import urllib3
import base64
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Selenium相关导入
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  警告: 未安装Selenium，HTML页面将保存为HTML文件")
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

def save_html_as_pdf(url, filename, save_dir):
    """使用Selenium将HTML页面保存为PDF（截屏方式）"""
    if not SELENIUM_AVAILABLE:
        print("✗ Selenium未安装，无法将HTML保存为PDF")
        return False
    
    driver = None
    try:
        print(f"正在使用浏览器访问页面并保存为PDF...")
        driver = setup_driver()
        if not driver:
            return False
        
        # 访问页面
        driver.get(url)
        
        # 等待页面完全加载
        print("  等待页面完全加载...")
        try:
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            # 额外等待图片和资源加载
            time.sleep(3)
            
            # 滚动页面确保所有内容加载
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
        except TimeoutException:
            print("  ⚠️ 页面加载超时，继续保存...")
        
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
        print("  正在将页面保存为PDF...")
        
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
        pdf_data = base64.b64decode(result['data'])
        
        with open(file_path, 'wb') as f:
            f.write(pdf_data)
        
        # 验证文件
        if not os.path.exists(file_path):
            print(f"✗ PDF保存失败")
            return False
        
        file_size = os.path.getsize(file_path)
        
        if file_size < 1024:
            print(f"⚠️ 文件大小异常小 ({file_size} 字节)，可能是错误页面")
            os.remove(file_path)
            return False
        
        print(f"✓ PDF保存成功: {filename}")
        print(f"  文件大小: {file_size:,} 字节 ({file_size/1024/1024:.2f} MB)")
        print(f"  保存路径: {file_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ 保存HTML为PDF失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def find_last_year_report(url, base_url):
    """在页面中查找去年的年报链接"""
    # 获取去年的年份
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    last_year_str = str(last_year)
    
    # 使用requests方式直接查找
    print("正在访问页面查找年报...")
    session = requests.Session()
    session.headers.update(get_headers())
    
    try:
        # 尝试访问页面
        print(f"正在访问页面: {url}")
        try:
            response = session.get(url, timeout=30, verify=False)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"访问页面失败: {e}")
            raise
        
        response.encoding = response.apparent_encoding or 'utf-8'
        
        # 显示页面基本信息
        print(f"\n页面访问成功")
        print(f"页面大小: {len(response.text):,} 字符")
        print(f"页面编码: {response.encoding}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 检查页面标题
        title_tag = soup.find('title')
        if title_tag:
            print(f"页面标题: {title_tag.get_text().strip()}")
        
        print(f"\n查找 {last_year} 年的年报...")
        
        # 在页面中查找PDF链接
        pdf_links = []
        
        # 1. 查找所有a标签中的PDF链接
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            title = link.get('title', '')
            
            if not href:
                continue
            
            # 跳过javascript链接和无效链接
            if href.startswith('javascript:') or href.startswith('#') or href.strip() == '':
                continue
            
            # 检查是否是PDF文件
            if href.lower().endswith('.pdf') or '.pdf' in href.lower():
                full_url = urljoin(url, href)
                pdf_links.append({
                    'url': full_url,
                    'text': text or title or href,
                    'year': extract_year_from_text(text or title or href) or extract_year_from_url_params(full_url)
                })
        
        # 2. 在页面源码中深度查找PDF URL
        print("  正在深度分析页面源码查找PDF链接...")
        page_source = response.text
        
        # 多种PDF URL匹配模式
        pdf_patterns = [
            r'https?://[^\s<>"\'\)]+\.pdf',  # 完整URL
            r'["\']([^"\']*\.pdf)["\']',  # 引号中的PDF路径
            r'href=["\']([^"\']*\.pdf)["\']',  # href属性中的PDF
            r'src=["\']([^"\']*\.pdf)["\']',  # src属性中的PDF
            r'data-src=["\']([^"\']*\.pdf)["\']',  # data-src属性中的PDF
            r'data-url=["\']([^"\']*\.pdf)["\']',  # data-url属性中的PDF
            r'data-href=["\']([^"\']*\.pdf)["\']',  # data-href属性中的PDF
            r'url\(["\']?([^"\'\)]+\.pdf)["\']?\)',  # CSS url()中的PDF
            r'/([^/\s<>"\'\)]+\.pdf)',  # 以/开头的PDF路径
        ]
        
        found_pdf_urls = []
        found_pdf_paths = set()  # 用于去重
        
        # 遍历所有模式查找PDF
        for pattern in pdf_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            for match in matches:
                pdf_path = None
                if isinstance(match, tuple):
                    pdf_path = next((m for m in match if m), None)
                else:
                    pdf_path = match
                
                if not pdf_path or not pdf_path.lower().endswith('.pdf'):
                    continue
                
                # 跳过已经处理过的
                if pdf_path in found_pdf_paths:
                    continue
                found_pdf_paths.add(pdf_path)
                
                # 构建完整URL
                if pdf_path.startswith('http'):
                    pdf_url = pdf_path
                elif pdf_path.startswith('/'):
                    # 绝对路径
                    base_url_parsed = urlparse(url)
                    pdf_url = f"{base_url_parsed.scheme}://{base_url_parsed.netloc}{pdf_path}"
                else:
                    # 相对路径
                    pdf_url = urljoin(url, pdf_path)
                
                if pdf_url not in found_pdf_urls:
                    found_pdf_urls.append(pdf_url)
                    pdf_links.append({
                        'url': pdf_url,
                        'text': pdf_path,
                        'year': extract_year_from_text(pdf_path) or extract_year_from_url_params(pdf_url) or last_year_str
                    })
        
        # 打印找到的PDF链接
        if pdf_links:
            print(f"找到 {len(pdf_links)} 个PDF链接")
            for link_info in pdf_links[:5]:
                print(f"  - {link_info['text']} | 年份: {link_info['year']} | URL: {link_info['url'][:80]}")
        
        # 优先查找去年的PDF
        last_year_pdf_links = [link for link in pdf_links if link['year'] == last_year_str]
        
        if last_year_pdf_links:
            print(f"✓ 找到去年的PDF链接: {last_year_pdf_links[0]['text']}")
            print(f"  URL: {last_year_pdf_links[0]['url']}")
            return last_year_pdf_links[0]['url'], last_year_str
        
        # 如果没有找到去年的，返回第一个PDF（假设当前页面就是去年的）
        if pdf_links:
            print(f"✓ 找到PDF链接: {pdf_links[0]['text']}")
            print(f"  URL: {pdf_links[0]['url']}")
            return pdf_links[0]['url'], pdf_links[0]['year'] or last_year_str
        
        # 如果没有找到PDF，检查页面内容，可能需要保存HTML
        # 检查页面标题或内容中是否包含年份信息
        page_title = title_tag.get_text().strip() if title_tag else ''
        page_text = soup.get_text()
        
        # 如果页面标题或内容中包含去年的年份，说明这个HTML页面就是年报
        if last_year_str in page_title or last_year_str in page_text[:1000]:
            print(f"✓ 页面内容包含 {last_year} 年信息，将保存为HTML")
            print(f"  URL: {url}")
            return url, last_year_str
        
        # 如果都没找到
        print("✗ 未找到PDF链接，且页面内容不匹配")
        return None
        
    except Exception as e:
        print(f"✗ 查找年报链接失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        session.close()

def download_pdf(url, filename, save_dir):
    """下载文件（支持PDF、DOCX、DOC、HTML等格式）"""
    try:
        session = requests.Session()
        session.headers.update(get_headers())
        
        print(f"正在下载: {url}")
        
        # 先检查是否是HTML页面
        url_lower = url.lower()
        is_html_page = url_lower.endswith(('.aspx', '.html', '.htm', '.jhtml'))
        
        # 如果是HTML页面，使用Selenium保存为PDF
        if is_html_page:
            print("检测到HTML页面，将使用浏览器截屏保存为PDF...")
            session.close()
            return save_html_as_pdf(url, filename, save_dir)
        
        response = session.get(url, stream=True, timeout=60, verify=False)
        response.raise_for_status()
        
        # 检查内容类型和文件扩展名
        content_type = response.headers.get('Content-Type', '').lower()
        
        # 如果Content-Type是HTML，也使用Selenium保存为PDF
        if 'text/html' in content_type:
            print("检测到HTML内容，将使用浏览器截屏保存为PDF...")
            session.close()
            return save_html_as_pdf(url, filename, save_dir)
        
        # 检查是否是PDF文件
        is_pdf = False
        if 'application/pdf' in content_type:
            is_pdf = True
        elif url_lower.endswith('.pdf'):
            is_pdf = True
        else:
            # 检查文件内容的前几个字节是否是PDF签名
            try:
                # 读取前几个字节
                first_bytes = response.content[:4]
                if first_bytes == b'%PDF':
                    is_pdf = True
                    print("  检测到PDF文件签名")
            except:
                pass
        
        # 根据内容确定文件扩展名
        if is_pdf:
            file_ext = '.pdf'
        elif url_lower.endswith('.docx') or 'word' in content_type and 'openxml' in content_type:
            file_ext = '.docx'
        elif url_lower.endswith('.doc') or 'word' in content_type or 'document' in content_type:
            file_ext = '.doc'
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
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("大连图书馆年报下载工具")
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
    
    # 大连图书馆年报页面URL（根据年份动态构建）
    # URL格式：http://regulations.dl-library.net.cn/{年份}servicedata.aspx
    report_page_url = f"http://regulations.dl-library.net.cn/{last_year_str}servicedata.aspx"
    base_url = "http://regulations.dl-library.net.cn"
    
    print(f"目标年份: {last_year}年")
    print(f"年报页面URL: {report_page_url}")
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
        # 使用实际找到的年份，而不是预设的去年年份
        if actual_year and actual_year != last_year_str:
            print(f"⚠️  注意：找到的是 {actual_year} 年的年报，不是 {last_year_str} 年的")
            year_for_filename = actual_year
        else:
            year_for_filename = last_year_str
    else:
        file_url = result
        year_for_filename = last_year_str
    
    # 生成文件名，使用实际找到的年份
    # 根据URL确定文件扩展名（HTML页面会保存为PDF）
    if file_url.lower().endswith('.docx'):
        file_ext = '.docx'
    elif file_url.lower().endswith('.doc'):
        file_ext = '.doc'
    elif file_url.lower().endswith(('.html', '.htm', '.aspx', '.jhtml')):
        file_ext = '.pdf'  # HTML页面会保存为PDF
    elif file_url.lower().endswith('.pdf'):
        file_ext = '.pdf'
    else:
        file_ext = '.pdf'  # 默认使用pdf（HTML页面会保存为PDF）
    
    filename = f"大连图书馆{year_for_filename}年年报{file_ext}"
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

