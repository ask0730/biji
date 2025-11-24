import os
import sys
import time
import json
import re
import logging
from pathlib import Path
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

if not SELENIUM_AVAILABLE:
    print("错误: 需要安装 selenium 库")
    print("请运行: pip install selenium")
    sys.exit(1)

if not PANDAS_AVAILABLE:
    print("错误: 需要安装 pandas 库")
    print("请运行: pip install pandas openpyxl")
    sys.exit(1)


def init_logger():
    """初始化日志"""
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "doubao_table_extract.log")

    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    
    logger = logging.getLogger("doubao_extractor")
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    return logger


logger = init_logger()


def get_cookies_path():
    """获取cookies文件路径"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "doubao_cookies.json")


def save_cookies(driver, cookies_path):
    """保存cookies到文件"""
    try:
        cookies = driver.get_cookies()
        with open(cookies_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        logger.info(f"Cookies已保存到: {cookies_path}")
        return True
    except Exception as e:
        logger.error(f"保存cookies失败: {str(e)}")
        return False


def load_cookies(driver, cookies_path):
    """从文件加载cookies"""
    try:
        if not os.path.exists(cookies_path):
            return False
        
        with open(cookies_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        
        driver.get("https://www.doubao.com/")
        time.sleep(2)
        
        for cookie in cookies:
            try:
                cookie.pop('sameSite', None)
                driver.add_cookie(cookie)
            except Exception as e:
                logger.warning(f"添加cookie失败: {str(e)}")
        
        driver.refresh()
        time.sleep(2)
        
        logger.info(f"Cookies已从 {cookies_path} 加载")
        return True
    except Exception as e:
        logger.error(f"加载cookies失败: {str(e)}")
        return False


def check_login_status(driver):
    """检查是否已登录"""
    try:
        current_url = driver.current_url
        if 'login' in current_url or 'sign' in current_url:
            return False
        
        # 检查是否有登录按钮
        try:
            login_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '登录')]")
            if login_buttons:
                return False
        except:
            pass
        
        return True
    except:
        return False


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
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        logger.error(f"浏览器启动失败: {e}")
        raise


def ensure_login(driver):
    """确保已登录（可选，豆包可以不登录使用）"""
    cookies_path = get_cookies_path()
    
    # 尝试加载cookies（如果有）
    if load_cookies(driver, cookies_path):
        if check_login_status(driver):
            print("✓ 已使用保存的登录状态")
            return True
    
    # 豆包可以不登录使用，直接返回True
    print("ℹ️  豆包可以不登录使用，继续运行...")
    return True


def upload_file_to_doubao(driver, file_path):
    """上传文件到豆包"""
    try:
        print(f"正在上传文件: {os.path.basename(file_path)}")
        
        # 查找附件按钮
        attachment_button = None
        
        # 方法1: 通过输入框查找附件按钮
        try:
            input_area = driver.find_element(By.CSS_SELECTOR, "textarea, input[type='text'], [contenteditable='true']")
            parent = input_area.find_element(By.XPATH, "./..")
            buttons = parent.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                if btn.is_displayed():
                    try:
                        svg = btn.find_element(By.TAG_NAME, "svg")
                        svg_html = svg.get_attribute('outerHTML')
                        if 'paperclip' in svg_html.lower() or 'attach' in svg_html.lower():
                            attachment_button = btn
                            break
                    except:
                        pass
        except:
            pass
        
        # 方法2: 直接查找附件按钮
        if not attachment_button:
            selectors = [
                "button svg[class*='paperclip']",
                "button svg[class*='attach']",
                "button[aria-label*='附件']",
                "button[aria-label*='上传']",
            ]
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.tag_name == 'svg':
                            try:
                                parent_btn = elem.find_element(By.XPATH, "./ancestor::button")
                                if parent_btn.is_displayed():
                                    attachment_button = parent_btn
                                    break
                            except:
                                continue
                        elif elem.tag_name == 'button' and elem.is_displayed():
                            attachment_button = elem
                            break
                    if attachment_button:
                        break
                except:
                    continue
        
        if attachment_button:
            print("找到附件按钮，正在点击...")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", attachment_button)
            time.sleep(0.5)
            attachment_button.click()
            time.sleep(1.5)
        
        # 查找文件输入框
        wait = WebDriverWait(driver, 5)
        try:
            file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        except TimeoutException:
            file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            if file_inputs:
                file_input = file_inputs[-1]
            else:
                raise Exception("未找到文件输入框")
        
        file_input.send_keys(os.path.abspath(file_path))
        print("✓ 文件上传成功")
        time.sleep(3)  # 等待文件上传完成
        
        # 查找输入框并输入消息
        print("正在输入消息：提取第一页的表格...")
        message = "请提取这个PDF第一页的表格，并以表格格式返回"
        
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
            # 清空输入框
            input_element.clear()
            time.sleep(0.5)
            
            # 输入消息
            if input_element.tag_name == 'textarea' or input_element.tag_name == 'input':
                input_element.send_keys(message)
            else:
                # contenteditable元素
                input_element.send_keys(message)
            
            print(f"✓ 已输入消息: {message}")
            time.sleep(1)
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
        send_selectors = [
            "button[aria-label*='发送']",
            "button[title*='发送']",
            "button[type='submit']",
            "button svg[class*='send']",
            "button:has(svg[class*='send'])",
        ]
        
        send_button = None
        for selector in send_selectors:
            try:
                send_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                for btn in send_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        send_button = btn
                        break
                if send_button:
                    break
            except:
                continue
        
        # 如果找不到发送按钮，尝试通过回车键发送
        if send_button:
            print("找到发送按钮，正在点击...")
            send_button.click()
        else:
            print("未找到发送按钮，尝试按回车键发送...")
            if input_element:
                input_element.send_keys(Keys.RETURN)
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
                            bubbles: true
                        });
                        inputs[i].dispatchEvent(event);
                        break;
                    }
                }
                """
                driver.execute_script(script)
        
        print("✓ 消息已发送")
        time.sleep(2)
        
        return True
        
    except Exception as e:
        logger.error(f"上传文件失败: {str(e)}")
        raise


def wait_for_response(driver, timeout=60):
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
                            text = elem.text.strip()
                            if len(text) > len(all_text):
                                all_text = text
                except:
                    continue
            
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
            logger.warning(f"等待响应时出错: {str(e)}")
            time.sleep(1)
    
    print("⚠️  等待响应超时，将尝试提取已有内容")
    return False


def extract_table_from_response(driver):
    """从响应中提取表格数据"""
    try:
        print("正在提取表格数据...")
        
        # 方法1: 查找HTML表格（优先）
        tables = driver.find_elements(By.TAG_NAME, "table")
        if tables:
            print(f"找到 {len(tables)} 个HTML表格")
            all_dataframes = []
            
            # 提取所有表格
            for table_idx, table in enumerate(tables):
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    if not rows:
                        continue
                    
                    data = []
                    headers = []
                    
                    for i, row in enumerate(rows):
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if not cells:
                            cells = row.find_elements(By.TAG_NAME, "th")
                        
                        if cells:
                            row_data = [cell.text.strip() for cell in cells]
                            if i == 0:
                                # 检查是否是表头（通常th标签或第一行）
                                if row.find_elements(By.TAG_NAME, "th"):
                                    headers = row_data
                                else:
                                    # 第一行可能是数据，也可能是表头
                                    headers = row_data
                                    data.append(row_data)
                            else:
                                data.append(row_data)
                    
                    if data or headers:
                        # 如果只有表头没有数据，使用表头作为第一行
                        if not data and headers:
                            data = [headers]
                            headers = []
                        
                        # 创建DataFrame
                        if headers:
                            # 确保列数一致
                            max_cols = max(len(headers), max([len(row) for row in data] if data else [0]))
                            headers = headers + [''] * (max_cols - len(headers))
                            for i, row in enumerate(data):
                                data[i] = row + [''] * (max_cols - len(row))
                            df = pd.DataFrame(data, columns=headers[:max_cols])
                        else:
                            # 没有表头，使用第一行作为表头
                            if data:
                                max_cols = max([len(row) for row in data])
                                for i, row in enumerate(data):
                                    data[i] = row + [''] * (max_cols - len(row))
                                df = pd.DataFrame(data[1:], columns=data[0][:max_cols] if data else None)
                            else:
                                continue
                        
                        if len(df) > 0:
                            all_dataframes.append(df)
                            print(f"  表格 {table_idx + 1}: {len(df)} 行 × {len(df.columns)} 列")
                except Exception as e:
                    logger.warning(f"提取表格 {table_idx + 1} 失败: {str(e)}")
                    continue
            
            # 如果有多个表格，合并它们
            if all_dataframes:
                if len(all_dataframes) == 1:
                    df = all_dataframes[0]
                else:
                    # 合并多个表格（垂直堆叠）
                    print(f"合并 {len(all_dataframes)} 个表格...")
                    df = pd.concat(all_dataframes, ignore_index=True)
                
                logger.info(f"从HTML表格提取了 {len(df)} 行数据")
                return df
        
        # 方法2: 从Markdown表格提取
        print("尝试从Markdown格式提取表格...")
        message_selectors = [
            "[class*='message']",
            "[class*='response']",
            "[class*='content']",
            "[class*='markdown']",
            "article",
            "[role='article']",
            "[class*='prose']",
        ]
        
        all_text = ""
        for selector in message_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed():
                        text = elem.text
                        if len(text) > len(all_text):
                            all_text = text
            except:
                continue
        
        # 从完整文本中提取所有表格
        if '|' in all_text:
            df = parse_markdown_table(all_text)
            if df is not None and len(df) > 0:
                print(f"从Markdown表格提取了 {len(df)} 行数据")
                logger.info(f"从Markdown表格提取了 {len(df)} 行数据")
                return df
        
        # 方法3: 从代码块中的表格提取
        print("尝试从代码块提取表格...")
        try:
            code_blocks = driver.find_elements(By.TAG_NAME, "pre")
            for code_block in code_blocks:
                if code_block.is_displayed():
                    text = code_block.text
                    if '|' in text:
                        df = parse_markdown_table(text)
                        if df is not None and len(df) > 0:
                            print(f"从代码块表格提取了 {len(df)} 行数据")
                            logger.info(f"从代码块表格提取了 {len(df)} 行数据")
                            return df
        except Exception as e:
            logger.warning(f"从代码块提取表格失败: {str(e)}")
        
        # 方法4: 尝试从所有文本中提取结构化数据
        print("尝试从文本内容提取结构化数据...")
        try:
            # 获取所有可见文本
            body = driver.find_element(By.TAG_NAME, "body")
            full_text = body.text
            
            # 如果文本中包含类似表格的结构（多行，每行有分隔符）
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            if len(lines) > 2:
                # 检查是否有表格特征（多行，每行长度相似）
                potential_table_lines = []
                for line in lines:
                    # 检查是否包含多个字段（通过制表符、多个空格或特殊字符分隔）
                    if '\t' in line or '  ' in line or '|' in line:
                        potential_table_lines.append(line)
                
                if len(potential_table_lines) >= 2:
                    # 尝试解析为表格
                    data = []
                    for line in potential_table_lines:
                        # 尝试不同的分隔符
                        if '|' in line:
                            cells = [c.strip() for c in line.split('|') if c.strip()]
                        elif '\t' in line:
                            cells = line.split('\t')
                        else:
                            # 多个空格分隔
                            cells = [c.strip() for c in line.split('  ') if c.strip()]
                        
                        if len(cells) >= 2:  # 至少2列
                            data.append(cells)
                    
                    if data:
                        # 确保所有行列数一致
                        max_cols = max([len(row) for row in data])
                        for i, row in enumerate(data):
                            data[i] = row + [''] * (max_cols - len(row))
                        
                        df = pd.DataFrame(data[1:], columns=data[0][:max_cols] if data else None)
                        if len(df) > 0:
                            print(f"从文本结构提取了 {len(df)} 行数据")
                            logger.info(f"从文本结构提取了 {len(df)} 行数据")
                            return df
        except Exception as e:
            logger.warning(f"从文本提取表格失败: {str(e)}")
        
        print("⚠️  未找到表格数据，请检查豆包是否返回了表格格式的数据")
        return None
        
    except Exception as e:
        logger.error(f"提取表格失败: {str(e)}")
        return None


def parse_markdown_table(text):
    """解析Markdown格式的表格"""
    try:
        lines = text.split('\n')
        table_lines = []
        in_table = False
        
        for line in lines:
            stripped = line.strip()
            # 检测表格行（包含|分隔符）
            if '|' in stripped and not stripped.startswith('|---'):
                table_lines.append(stripped)
                in_table = True
            elif in_table and '|' not in stripped:
                break
        
        if not table_lines:
            return None
        
        # 解析表格
        rows = []
        for line in table_lines:
            # 移除首尾的|
            cells = [cell.strip() for cell in line.split('|')]
            # 过滤空字符串
            cells = [c for c in cells if c]
            if cells:
                rows.append(cells)
        
        if len(rows) < 2:
            return None
        
        # 第一行作为表头
        headers = rows[0]
        data = rows[1:]
        
        # 确保所有行的列数一致
        max_cols = max(len(headers), max([len(row) for row in data] if data else [0]))
        headers = headers + [''] * (max_cols - len(headers))
        
        for i, row in enumerate(data):
            data[i] = row + [''] * (max_cols - len(row))
        
        df = pd.DataFrame(data, columns=headers[:max_cols])
        return df
        
    except Exception as e:
        logger.error(f"解析Markdown表格失败: {str(e)}")
        return None


def save_to_excel(df, output_path):
    """保存DataFrame到Excel"""
    try:
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"✓ 表格已保存到: {output_path}")
        logger.info(f"表格已保存到: {output_path}, 共 {len(df)} 行, {len(df.columns)} 列")
        return True
    except Exception as e:
        logger.error(f"保存Excel失败: {str(e)}")
        raise


def main():
    """主函数"""
    driver = None
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 查找要上传的文件（PDF、图片等）
        file_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.txt', '.doc', '.docx']
        files = []
        for ext in file_extensions:
            files.extend(list(Path(script_dir).glob(f"*{ext}")))
        
        if not files:
            print(f"错误: 在 {script_dir} 目录下未找到可上传的文件")
            print(f"支持的文件格式: {', '.join(file_extensions)}")
            return
        
        # 自动选择第一个文件（优先选择PDF）
        pdf_files = [f for f in files if f.suffix.lower() == '.pdf']
        if pdf_files:
            file_path = pdf_files[0]
            print(f"\n找到 {len(files)} 个文件，自动选择PDF文件: {file_path.name}")
        else:
            file_path = files[0]
            print(f"\n找到 {len(files)} 个文件，自动选择: {file_path.name}")
        
        print(f"\n正在处理文件: {file_path.name}")
        logger.info(f"开始处理文件: {file_path}")
        
        # 启动浏览器
        print("正在启动浏览器...")
        driver = setup_driver()
        
        # 检查登录状态（可选）
        print("正在检查登录状态...")
        ensure_login(driver)  # 即使未登录也继续
        
        # 打开豆包聊天页面
        print("正在打开豆包聊天页面...")
        driver.get("https://www.doubao.com/")
        time.sleep(3)
        
        # 上传文件
        upload_file_to_doubao(driver, str(file_path))
        
        # 等待响应
        wait_for_response(driver, timeout=120)
        
        # 提取表格
        df = extract_table_from_response(driver)
        
        if df is not None and len(df) > 0:
            # 保存到Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(script_dir, f"{file_path.stem}_表格_{timestamp}.xlsx")
            save_to_excel(df, output_path)
            
            print(f"\n✓ 处理完成！")
            print(f"  输入文件: {file_path.name}")
            print(f"  输出文件: {output_path}")
            print(f"  表格大小: {len(df)} 行 × {len(df.columns)} 列")
        else:
            print("\n⚠️  未能提取到表格数据")
            print("提示: 请确保豆包返回了表格格式的数据")
        
        # 保持浏览器打开
        print("\n浏览器将保持打开10秒，您可以查看结果...")
        time.sleep(10)
        
    except Exception as e:
        error_msg = f"处理失败: {str(e)}"
        print(f"错误: {error_msg}")
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        
    finally:
        # 保存cookies
        if driver:
            try:
                cookies_path = get_cookies_path()
                save_cookies(driver, cookies_path)
            except:
                pass
            
            try:
                driver.quit()
            except:
                pass


if __name__ == "__main__":
    main()

