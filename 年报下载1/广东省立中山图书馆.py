# -*- coding: utf-8 -*-
"""
广东省立中山图书馆年报下载脚本
功能：从广东省立中山图书馆官网下载去年的年报，并重命名为"广东省立中山图书馆年份年报"格式
"""

import requests
import os
import time
import re
import urllib3
from urllib.parse import urljoin, urlparse, quote
from bs4 import BeautifulSoup

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
        print(f"正在访问页面: {url}")
        response = session.get(url, timeout=30, verify=False)
        response.raise_for_status()
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
            # 如果href是绝对URL，直接使用；否则使用urljoin构建完整URL
            if href.startswith('http://') or href.startswith('https://'):
                full_url = href
            else:
                # 对于相对路径，使用urljoin构建完整URL
                # urljoin会自动处理中文文件名
                full_url = urljoin(url, href)  # 使用当前页面URL作为base，这样能正确处理相对路径
            
            # 检查链接文本或URL中是否包含年报相关关键词
            keywords = ['年报', '年度报告', '年度', 'annual', 'report']
            is_report_link = any(keyword in text or keyword in href.lower() for keyword in keywords)
            
            # 检查是否是PDF文件（必须是真正的PDF链接，不能只是包含pdf字符串）
            # 只有URL以.pdf结尾，或者href以.pdf结尾，才认为是PDF
            is_pdf = (full_url.lower().endswith('.pdf') or href.lower().endswith('.pdf')) and not href.startswith('javascript:')
            # 优先从文本中提取年份，然后从URL参数中提取，最后从URL路径中提取
            year_in_text = extract_year_from_text(text)
            year_in_url_params = extract_year_from_url_params(full_url)
            year_in_url_path = extract_year_from_text(href)
            # 优先使用文本中的年份，然后是URL参数中的年份，最后是URL路径中的年份
            extracted_year = year_in_text or year_in_url_params or year_in_url_path
            
            # 如果包含年报关键词或者是PDF，或者包含年份，都记录下来
            if is_report_link or is_pdf or extracted_year:
                all_links.append({
                    'url': full_url,
                    'text': text,
                    'year': extracted_year,
                    'is_pdf': is_pdf,
                    'is_report': is_report_link
                })
        
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
            # 优先选择PDF链接（必须是真正的PDF链接，URL必须以.pdf结尾）
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
            
            # 如果没有找到真正的PDF链接，先尝试根据年份构建PDF URL
            # 尝试多种可能的PDF文件名格式（根据其他年份的格式）
            possible_formats = [
                f"{last_year_str}年报.pdf",
                f"{last_year_str}年度报告.pdf",
                f"{last_year_str}年报官网版.pdf",
                f"{last_year_str}年年度报告.pdf",
            ]
            
            print(f"未找到直接的PDF链接，尝试构建可能的PDF URL...")
            for pdf_filename in possible_formats:
                possible_pdf_url = f"{base_url}/{pdf_filename}"
                print(f"尝试访问可能的PDF链接: {possible_pdf_url}")
                # 验证这个URL是否存在（使用HEAD请求）
                try:
                    test_response = session.head(possible_pdf_url, timeout=10, verify=False, allow_redirects=True)
                    if test_response.status_code == 200:
                        content_type = test_response.headers.get('Content-Type', '').lower()
                        if 'pdf' in content_type or possible_pdf_url.lower().endswith('.pdf'):
                            print(f"✓ 找到去年的年报PDF链接 (年份: {last_year_str})")
                            print(f"  URL: {possible_pdf_url}")
                            return possible_pdf_url, last_year_str
                except Exception as e:
                    # 如果HEAD请求失败，尝试GET请求（有些服务器不支持HEAD）
                    try:
                        test_response = session.get(possible_pdf_url, timeout=10, verify=False, allow_redirects=True, stream=True)
                        if test_response.status_code == 200:
                            content_type = test_response.headers.get('Content-Type', '').lower()
                            if 'pdf' in content_type:
                                print(f"✓ 找到去年的年报PDF链接 (年份: {last_year_str})")
                                print(f"  URL: {possible_pdf_url}")
                                return possible_pdf_url, last_year_str
                    except:
                        pass
            
            # 如果构建URL失败，尝试访问找到的链接，看看是否能找到PDF
            print(f"构建URL失败，尝试访问找到的链接页面查找PDF...")
            for link_info in last_year_links:
                if '年报' in link_info['text'] or '年度报告' in link_info['text']:
                    # 如果链接不是PDF，访问这个链接看看
                    if not link_info['url'].lower().endswith('.pdf'):
                        print(f"访问链接页面: {link_info['url']}")
                        try:
                            link_response = session.get(link_info['url'], timeout=30, verify=False)
                            link_response.raise_for_status()
                            link_response.encoding = link_response.apparent_encoding or 'utf-8'
                            link_soup = BeautifulSoup(link_response.text, 'html.parser')
                            
                            # 在这个页面中查找PDF链接
                            for pdf_link in link_soup.find_all('a', href=True):
                                pdf_href = pdf_link.get('href')
                                if pdf_href and pdf_href.lower().endswith('.pdf'):
                                    pdf_full_url = urljoin(link_info['url'], pdf_href)
                                    # 检查是否包含年份
                                    if last_year_str in pdf_full_url or last_year_str in pdf_link.get_text():
                                        print(f"✓ 在链接页面找到PDF: {pdf_link.get_text().strip()}")
                                        print(f"  URL: {pdf_full_url}")
                                        return pdf_full_url, last_year_str
                        except Exception as e:
                            print(f"  访问链接页面失败: {e}")
                            continue
            
            # 如果还是没有找到，返回第一个有效的去年的链接（排除javascript链接）
            valid_links = [link for link in last_year_links if not link['url'].startswith('javascript:')]
            if valid_links:
                print(f"✓ 找到去年的链接: {valid_links[0]['text']} (年份: {valid_links[0]['year']})")
                return valid_links[0]['url'], valid_links[0]['year']
        
        # 如果没有找到去年的年报，列出所有找到的链接供参考
        report_links = [link for link in all_links if (link['is_pdf'] or link['is_report']) and ('年报' in link['text'] or '年报' in link['url'])]
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

def download_pdf(url, filename, save_dir):
    """下载PDF文件"""
    try:
        session = requests.Session()
        session.headers.update(get_headers())
        
        print(f"正在下载: {url}")
        # requests库会自动处理URL编码，包括中文文件名
        response = session.get(url, stream=True, timeout=60, verify=False)
        response.raise_for_status()
        
        # 检查内容类型
        content_type = response.headers.get('Content-Type', '').lower()
        if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
            print(f"⚠️  警告: 内容类型可能不是PDF: {content_type}")
        
        # 确保文件名以.pdf结尾
        if not filename.endswith('.pdf'):
            filename = filename + '.pdf'
        
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
    print("广东省立中山图书馆年报下载工具")
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
    
    # 广东省立中山图书馆年报页面URL
    report_page_url = "https://www.zslib.com.cn/jingtaiyemian/zwgk/bgnb.html"
    base_url = "https://www.zslib.com.cn"
    
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
        pdf_url, actual_year = result
        # 使用实际找到的年份，而不是预设的去年年份
        if actual_year and actual_year != last_year_str:
            print(f"⚠️  注意：找到的是 {actual_year} 年的年报，不是 {last_year_str} 年的")
            # 如果找到的不是去年的，询问是否继续
            if actual_year < last_year_str:
                print(f"⚠️  这是前年的年报，是否继续下载？")
                # 继续下载，但使用实际年份
                year_for_filename = actual_year
            else:
                year_for_filename = actual_year
        else:
            year_for_filename = last_year_str
    else:
        pdf_url = result
        year_for_filename = last_year_str
    
    # 生成文件名，使用实际找到的年份
    filename = f"广东省立中山图书馆{year_for_filename}年年报.pdf"
    filename = clean_filename(filename)
    
    print(f"\n文件名: {filename}")
    print("-" * 60)
    
    # 下载文件
    success = download_pdf(pdf_url, filename, output_folder)
    
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

