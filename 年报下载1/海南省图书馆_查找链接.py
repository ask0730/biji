# -*- coding: utf-8 -*-
"""
海南省图书馆年报链接查找脚本
功能：访问页面，查找年报相关链接并输出
"""

import time
import re
import urllib3

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
    print("⚠️  警告: 未安装Selenium")
    print("  安装命令: pip install selenium")

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

def extract_year_from_text(text):
    """从文本中提取年份"""
    if not text:
        return None
    year_match = re.search(r'(20[0-3]\d)', text)
    if year_match:
        return year_match.group(1)
    return None

def find_report_links(url, base_url):
    """在页面中查找年报相关链接"""
    # 获取去年的年份
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    last_year_str = str(last_year)
    
    if not SELENIUM_AVAILABLE:
        print("✗ Selenium未安装")
        return []
    
    driver = None
    found_links = []
    
    try:
        print("正在使用浏览器访问页面...")
        driver = setup_driver()
        if not driver:
            return []
        
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
        
        print(f"\n查找 {last_year} 年的年报相关链接...")
        print("=" * 60)
        
        # 查找所有链接
        keywords = ['年报', '年度报告', '年度', '报告']
        all_links = driver.find_elements(By.XPATH, "//a[@href]")
        
        print(f"页面中共找到 {len(all_links)} 个链接")
        print("-" * 60)
        
        for link in all_links:
            try:
                href = link.get_attribute('href')
                text = link.text.strip()
                title_attr = link.get_attribute('title') or ''
                combined_text = text + ' ' + title_attr
                
                # 检查是否包含关键词
                has_keyword = any(kw in combined_text for kw in keywords)
                has_year = last_year_str in combined_text or last_year_str in (href or '')
                
                if has_keyword or has_year:
                    link_info = {
                        'href': href,
                        'text': text,
                        'title': title_attr,
                        'combined_text': combined_text,
                        'has_keyword': has_keyword,
                        'has_year': has_year
                    }
                    found_links.append(link_info)
                    
                    print(f"\n找到链接:")
                    print(f"  文本: {text}")
                    print(f"  标题: {title_attr}")
                    print(f"  链接: {href}")
                    print(f"  包含关键词: {has_keyword}")
                    print(f"  包含年份: {has_year}")
                    print("-" * 60)
            except Exception as e:
                continue
        
        # 如果没有找到，尝试查找所有包含年份的链接
        if not found_links:
            print("\n未找到包含关键词的链接，查找所有包含去年年份的链接...")
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    if href and last_year_str in (href + ' ' + text):
                        link_info = {
                            'href': href,
                            'text': text,
                            'title': link.get_attribute('title') or '',
                            'has_year': True
                        }
                        found_links.append(link_info)
                        
                        print(f"\n找到包含年份的链接:")
                        print(f"  文本: {text}")
                        print(f"  链接: {href}")
                        print("-" * 60)
                except:
                    continue
        
        return found_links
        
    except Exception as e:
        print(f"✗ 查找链接失败: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    """主函数"""
    print("=" * 60)
    print("海南省图书馆年报链接查找工具")
    print("=" * 60)
    
    # 获取去年的年份
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    last_year_str = str(last_year)
    
    # 海南省图书馆页面URL
    page_url = "https://www.hilib.com/sub/article-list?pid=852167302892900352&cid=852167304906166272&t=1766306920929"
    base_url = "https://www.hilib.com"
    
    print(f"目标年份: {last_year}年")
    print(f"页面URL: {page_url}")
    print("=" * 60)
    
    # 查找年报链接
    found_links = find_report_links(page_url, base_url)
    
    print("\n" + "=" * 60)
    print("查找结果汇总")
    print("=" * 60)
    
    if found_links:
        print(f"\n共找到 {len(found_links)} 个相关链接:\n")
        for i, link_info in enumerate(found_links, 1):
            print(f"{i}. {link_info.get('text', '无文本')}")
            print(f"   链接: {link_info['href']}")
            if link_info.get('title'):
                print(f"   标题: {link_info['title']}")
            print()
    else:
        print("\n✗ 未找到年报相关链接")
    
    print("=" * 60)
    print("查找完成（仅查找，未执行下载操作）")
    print("=" * 60)

if __name__ == "__main__":
    main()

