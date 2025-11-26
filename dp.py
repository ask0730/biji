import os
import subprocess
import time

def run_umi_ocr_commands():
    # 切换到指定目录
    target_dir = r"D:\Desktop\1\Umi-OCR_Paddle_v2.1.5"
    
    # 检查目录是否存在
    if not os.path.exists(target_dir):
        print(f"错误: 目录不存在 - {target_dir}")
        return False
    
    try:
        os.chdir(target_dir)
        print(f"✓ 已切换到目录: {target_dir}")
    except Exception as e:
        print(f"✗ 切换目录失败: {e}")
        return False
    
    commands = [
        {
            "cmd": "umi-ocr --all_pages",
            "desc": "设置所有页面"
        },
        {
            "cmd": "umi-ocr --add_page 3", 
            "desc": "添加第3页"
        },
        {
            "cmd": "umi-ocr --call_qml BatchDOC --func addDocs \"[ \\\"D:/Desktop/demo/PDF_OCR/职称参评-毛雅君20251114V1.0(1).pdf\\\" ]\"",
            "desc": "添加PDF文档"
        },
        {
            "cmd": "umi-ocr --call_qml BatchDOC --func docStart",
            "desc": "开始OCR处理"
        }
    ]
    
    success_count = 0
    
    for i, command_info in enumerate(commands, 1):
        cmd = command_info["cmd"]
        desc = command_info["desc"]
        
        print(f"\n[{i}/{len(commands)}] {desc}")
        print(f"执行: {cmd}")
        
        try:
            # 执行命令，设置较长的超时时间
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30  # 30秒超时
            )
            
            # 输出结果
            if result.stdout:
                print(f"输出: {result.stdout.strip()}")
            if result.stderr:
                print(f"警告/错误: {result.stderr.strip()}")
            
            if result.returncode == 0:
                print(f"✓ 命令执行成功")
                success_count += 1
            else:
                print(f"✗ 命令执行失败，返回码: {result.returncode}")
            
            # 命令间延迟3秒
            if i < len(commands):
                print("等待10秒...")
                time.sleep(10)
                
        except subprocess.TimeoutExpired:
            print(f"✗ 命令执行超时")
        except Exception as e:
            print(f"✗ 执行命令时出错: {e}")
    
    print(f"\n执行完成: {success_count}/{len(commands)} 个命令成功")
    return success_count == len(commands)

if __name__ == "__main__":
    print("开始执行Umi-OCR自动化流程...")
    success = run_umi_ocr_commands()
    
    if success:
        print("\n🎉 所有步骤执行成功！")
    else:
        print("\n⚠️ 部分步骤执行失败，请检查输出信息。")