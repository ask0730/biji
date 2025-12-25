#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
海南省图书馆决算报告下载工具
"""

import os
import re
import time
import glob
import requests
from urllib.parse import urljoin, urlparse

# 尝试导入Selenium相关模块
SELENIUM_AVAILABLE = False
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
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

def setup_driver_with_download(save_dir):
    """设置浏览器驱动，配置下载目录"""
    if not SELENIUM_AVAILABLE:
        print("✗ Selenium未安装，无法使用浏览器自动化功能")
        return None
    
    try:
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        
        # 设置下载目录
        prefs = {
            "download.default_directory": save_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True,
            "plugins.plugins_disabled": ["Chrome PDF Viewer"],
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # 其他选项
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 不使用headless模式，可以看到浏览器操作过程
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        print(f"✗ 启动浏览器失败: {e}")
        print("  请确保已安装Chrome浏览器和ChromeDriver")
        return None

def wait_for_download_complete(download_dir, expected_filename=None, timeout=60):
    """等待下载完成"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # 查找下载目录中的文件
        files = glob.glob(os.path.join(download_dir, "*"))
        
        # 查找.crdownload文件（Chrome下载中）
        downloading_files = [f for f in files if f.endswith('.crdownload')]
        
        if not downloading_files:
            # 没有正在下载的文件，检查是否有新文件
            if expected_filename:
                expected_path = os.path.join(download_dir, expected_filename)
                if os.path.exists(expected_path):
                    return expected_path
            
            # 查找最新的zip文件
            zip_files = [f for f in files if f.lower().endswith('.zip')]
            if zip_files:
                # 返回最新的文件
                latest_file = max(zip_files, key=os.path.getmtime)
                return latest_file
        
        time.sleep(1)
    
    return None

def simulate_human_click(driver, element):
    """模拟人类点击行为"""
    try:
        # 滚动到元素可见
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
        time.sleep(0.5)  # 模拟人类反应时间
        
        # 移动到元素上并点击
        ActionChains(driver).move_to_element(element).pause(0.2).click().perform()
        time.sleep(1)  # 等待页面响应
        return True
    except Exception as e:
        # 如果ActionChains失败，尝试直接点击
        try:
            driver.execute_script("arguments[0].click();", element)
            time.sleep(1)
            return True
        except:
            print(f"  点击失败: {e}")
            return False

def find_and_click_juesuan_item(driver, last_year_str):
    """查找并点击决算列表项"""
    print(f"\n查找包含'{last_year_str}年'和'决算'的列表项...")
    
    # 等待列表加载
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.ant-list-item, .article-item, .article-title"))
        )
    except TimeoutException:
        print("  列表加载超时，继续尝试...")
    
    time.sleep(2)  # 模拟人类浏览时间
    
    # 方法1: 查找列表项（li.ant-list-item）
    try:
        list_items = driver.find_elements(By.CSS_SELECTOR, "li.ant-list-item")
        print(f"找到 {len(list_items)} 个列表项")
        
        for item in list_items:
            try:
                item_text = item.text.strip()
                
                # 检查是否包含"决算"和去年年份
                if '决算' in item_text and last_year_str in item_text:
                    print(f"✓ 找到匹配的列表项: {item_text[:80]}")
                    
                    # 尝试点击标题元素
                    try:
                        title_element = item.find_element(By.CSS_SELECTOR, "p.article-title")
                        print(f"  点击标题元素")
                        if simulate_human_click(driver, title_element):
                            return True
                    except:
                        pass
                    
                    # 尝试点击整个列表项
                    try:
                        print(f"  点击整个列表项")
                        if simulate_human_click(driver, item):
                            return True
                    except:
                        pass
                    
                    # 尝试查找并点击链接
                    try:
                        link = item.find_element(By.TAG_NAME, "a")
                        href = link.get_attribute('href')
                        if href:
                            print(f"  找到链接: {href}")
                            if simulate_human_click(driver, link):
                                return True
                    except:
                        pass
            except:
                continue
    except Exception as e:
        print(f"  查找列表项时出错: {e}")
    
    # 方法2: 查找所有包含"决算"的链接
    try:
        all_links = driver.find_elements(By.TAG_NAME, "a")
        for link in all_links:
            try:
                href = link.get_attribute('href')
                text = link.text.strip()
                combined = text + ' ' + (href or '')
                
                if '决算' in combined and last_year_str in combined:
                    print(f"✓ 找到决算链接: {text or href}")
                    if simulate_human_click(driver, link):
                        return True
            except:
                continue
    except Exception as e:
        print(f"  查找链接时出错: {e}")
    
    # 方法3: 查找包含"决算"的标题元素
    try:
        title_elements = driver.find_elements(By.XPATH, 
            "//p[contains(@class, 'article-title') and contains(text(), '决算')]")
        for title in title_elements:
            try:
                title_text = title.text.strip()
                if last_year_str in title_text:
                    print(f"✓ 找到决算标题: {title_text[:80]}")
                    if simulate_human_click(driver, title):
                        return True
            except:
                continue
    except Exception as e:
        print(f"  查找标题时出错: {e}")
    
    return False

def find_and_click_zip_file(driver):
    """在新标签页中查找并点击.zip文件"""
    print("\n在新标签页中查找.zip文件...")
    time.sleep(2)  # 模拟人类浏览时间
    
    # 方法1: 查找包含".zip"的链接
    try:
        zip_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.zip')]")
        print(f"找到 {len(zip_links)} 个.zip链接")
        
        for link in zip_links:
            try:
                if link.is_displayed() and link.is_enabled():
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    print(f"✓ 找到.zip链接: {text or href}")
                    if simulate_human_click(driver, link):
                        return True
            except:
                continue
    except Exception as e:
        print(f"  查找.zip链接时出错: {e}")
    
    # 方法2: 查找包含"下载"和"zip"的元素
    try:
        download_elements = driver.find_elements(By.XPATH, 
            "//*[contains(text(), '下载') or contains(text(), 'zip') or contains(text(), 'ZIP')]")
        for element in download_elements:
            try:
                if element.is_displayed():
                    # 检查是否是链接
                    if element.tag_name == 'a':
                        href = element.get_attribute('href')
                        if href and '.zip' in href.lower():
                            print(f"✓ 找到.zip下载链接: {element.text.strip() or href}")
                            if simulate_human_click(driver, element):
                                return True
                    # 检查父级是否有链接
                    else:
                        try:
                            parent_link = element.find_element(By.XPATH, "./ancestor::a[contains(@href, '.zip')]")
                            if parent_link:
                                print(f"✓ 找到.zip链接（通过父级）")
                                if simulate_human_click(driver, parent_link):
                                    return True
                        except:
                            pass
            except:
                continue
    except Exception as e:
        print(f"  查找下载元素时出错: {e}")
    
    # 方法3: 在页面源码中查找.zip链接
    try:
        page_source = driver.page_source
        zip_pattern = r'href=["\']([^"\']*\.zip)["\']'
        matches = re.findall(zip_pattern, page_source, re.IGNORECASE)
        if matches:
            zip_url = matches[0]
            if not zip_url.startswith('http'):
                base_url = f"{driver.current_url.split('/')[0]}//{driver.current_url.split('/')[2]}"
                zip_url = urljoin(base_url, zip_url)
            print(f"✓ 在页面源码中找到.zip链接: {zip_url}")
            driver.get(zip_url)
            time.sleep(2)
            return True
    except Exception as e:
        print(f"  在页面源码中查找时出错: {e}")
    
    return False

def download_report_by_clicking(list_url, save_dir, filename):
    """通过模拟点击操作下载决算报告"""
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    last_year_str = str(last_year)
    
    driver = None
    try:
        print("=" * 60)
        print("海南省图书馆决算报告下载工具")
        print("=" * 60)
        
        # 设置浏览器（配置下载目录）
        print("\n正在启动浏览器...")
        driver = setup_driver_with_download(save_dir)
        if not driver:
            return False
        
        # 访问列表页
        print(f"\n正在访问列表页: {list_url}")
        driver.get(list_url)
        
        # 等待页面加载
        print("等待页面加载...")
        time.sleep(5)
        
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            print("  页面加载超时，继续尝试...")
        
        # 保存主窗口句柄
        main_window = driver.current_window_handle
        print(f"主窗口句柄: {main_window}")
        
        # 查找并点击决算列表项
        if not find_and_click_juesuan_item(driver, last_year_str):
            print("✗ 未找到匹配的决算列表项")
            return False
        
        # 等待新标签页打开
        print("\n等待新标签页打开...")
        time.sleep(3)
        
        # 检查是否有新窗口打开
        all_windows = driver.window_handles
        print(f"当前窗口数量: {len(all_windows)}")
        
        if len(all_windows) > 1:
            # 切换到新窗口
            for window_handle in all_windows:
                if window_handle != main_window:
                    driver.switch_to.window(window_handle)
                    print(f"✓ 已切换到新标签页")
                    print(f"  新窗口URL: {driver.current_url}")
                    break
        else:
            print("⚠️  未检测到新标签页，可能在同一窗口打开")
        
        # 等待新页面加载
        time.sleep(3)
        
        # 在新标签页中查找并点击.zip文件
        if not find_and_click_zip_file(driver):
            print("✗ 未找到.zip文件")
            return False
        
        # 等待下载完成
        print("\n等待下载完成...")
        downloaded_file = wait_for_download_complete(save_dir, timeout=120)
        
        if downloaded_file:
            # 重命名文件
            final_filename = clean_filename(filename)
            final_path = os.path.join(save_dir, final_filename)
            
            if os.path.exists(final_path):
                try:
                    os.remove(final_path)
                except:
                    pass
            
            try:
                os.rename(downloaded_file, final_path)
                print(f"✓ 下载完成并重命名: {final_filename}")
                print(f"  文件路径: {final_path}")
                
                # 验证文件大小
                file_size = os.path.getsize(final_path)
                print(f"  文件大小: {file_size:,} 字节 ({file_size/1024/1024:.2f} MB)")
                
                return True
            except Exception as e:
                print(f"⚠️  重命名失败，但文件已下载: {downloaded_file}")
                print(f"  错误: {e}")
                return True  # 文件已下载，只是重命名失败
        else:
            print("✗ 下载超时或失败")
            return False
        
    except Exception as e:
        print(f"✗ 下载过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            try:
                time.sleep(3)  # 等待下载完成
                driver.quit()
            except:
                pass

def main():
    """主函数"""
    print("=" * 60)
    print("海南省图书馆决算报告下载工具")
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
    
    # 海南省图书馆列表页URL
    list_url = "https://www.hilib.com/sub/article-list?pid=852167302892900352&cid=852167304906166272&t=1766306920929"
    
    print(f"目标年份: {last_year}年")
    print(f"列表页URL: {list_url}")
    print(f"输出路径: {output_folder}")
    print("-" * 60)
    
    # 生成文件名
    filename = f"海南省图书馆{last_year_str}年决算报告.zip"
    filename = clean_filename(filename)
    
    print(f"文件名: {filename}")
    print("-" * 60)
    
    # 通过模拟点击下载
    success = download_report_by_clicking(list_url, output_folder, filename)
    
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

