import os
from pathlib import Path
from datetime import datetime
import time
from dotenv import load_dotenv
from vision_agent.tools.pdf_parser import PDFParser
from vision_agent.utils.config import Config
import PyPDF2
import tempfile
import requests.exceptions


def split_pdf(pdf_path: str) -> list:
    """將 PDF 檔案分割成單頁

    Args:
        pdf_path (str): PDF 檔案路徑

    Returns:
        list: 臨時檔案路徑列表
    """
    temp_files = []
    
    # 開啟原始 PDF
    with open(pdf_path, 'rb') as file:
        # 創建 PDF reader 物件
        pdf_reader = PyPDF2.PdfReader(file)
        
        # 獲取頁數
        num_pages = len(pdf_reader.pages)
        
        # 逐頁處理
        for page_num in range(num_pages):
            # 創建新的 PDF writer 物件
            pdf_writer = PyPDF2.PdfWriter()
            
            # 添加當前頁
            pdf_writer.add_page(pdf_reader.pages[page_num])
            
            # 創建臨時文件
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            temp_files.append(temp_file.name)
            
            # 將單頁內容寫入臨時文件
            with open(temp_file.name, 'wb') as output_file:
                pdf_writer.write(output_file)
    
    return temp_files


def save_as_markdown(results: dict, output_path: str = "examples/output/", page_num: int = None) -> str:
    """將結果保存為 Markdown 文件

    Args:
        results (dict): API 回傳的結果
        output_path (str, optional): 輸出目錄. Defaults to "examples/output/".
        page_num (int, optional): 頁碼. Defaults to None.

    Returns:
        str: 保存的文件路徑
    """
    # 確保輸出目錄存在
    os.makedirs(output_path, exist_ok=True)
    
    # 生成檔案名稱，包含時間戳和頁碼
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    page_suffix = f"_page_{page_num}" if page_num is not None else ""
    output_file = os.path.join(output_path, f"pdf_analysis_{timestamp}{page_suffix}.md")
    
    # 從結果中提取 markdown 內容
    if "data" in results and "markdown" in results["data"]:
        markdown_content = results["data"]["markdown"]
        
        # 添加處理時間資訊
        header = f"""# PDF 分析結果
處理時間：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{f"頁碼：{page_num}" if page_num is not None else ""}

---

"""
        # 保存為 markdown 文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(header + markdown_content)
            
        return output_file
    else:
        raise ValueError("結果中沒有找到 markdown 內容")


def combine_markdown_files(file_paths: list, output_path: str = "examples/output/") -> str:
    """合併多個 Markdown 文件

    Args:
        file_paths (list): Markdown 文件路徑列表
        output_path (str, optional): 輸出目錄. Defaults to "examples/output/".

    Returns:
        str: 合併後的文件路徑
    """
    # 生成合併後的檔案名稱
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_path, f"pdf_analysis_{timestamp}_combined.md")
    
    # 合併內容
    combined_content = f"""# PDF 分析結果（合併版）
處理時間：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
總頁數：{len(file_paths)}

---

"""
    
    # 讀取並合併所有文件
    for i, file_path in enumerate(sorted(file_paths), 1):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 跳過其他文件的標題部分
            if i > 1:
                content = content.split('---\n', 1)[1] if '---\n' in content else content
            combined_content += f"\n## 第 {i} 頁\n\n{content}\n"
    
    # 保存合併後的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_content)
    
    return output_file


def process_pdf_with_retry(parser, pdf_path, max_retries=3, retry_delay=5):
    """處理 PDF 並在失敗時重試

    Args:
        parser: PDF 解析器實例
        pdf_path (str): PDF 文件路徑
        max_retries (int): 最大重試次數
        retry_delay (int): 重試間隔（秒）

    Returns:
        dict: 處理結果
    """
    for attempt in range(max_retries):
        try:
            return parser.process_pdf(pdf_path)
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"處理失敗（第 {attempt + 1} 次嘗試）：{str(e)}")
                print(f"等待 {retry_delay} 秒後重試...")
                time.sleep(retry_delay)
            else:
                raise e


def main():
    # 載入 .env 檔案
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    
    # 設置配置
    config = Config(
        landing_ai_api_key=os.getenv("LANDING_AI_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    # 初始化 PDF 解析器
    parser = PDFParser(config)
    
    # PDF 文件路徑
    pdf_path = "examples/data/test.pdf"
    
    # 檢查文件是否存在
    if not os.path.exists(pdf_path):
        print(f"錯誤：找不到 PDF 文件：{pdf_path}")
        print("請將 PDF 文件放在 examples/data 目錄下並命名為 test.pdf")
        return
    
    try:
        # 分割 PDF
        print("正在分割 PDF...")
        temp_files = split_pdf(pdf_path)
        print(f"PDF 已分割為 {len(temp_files)} 頁")
        
        # 儲存每頁處理結果的文件路徑
        output_files = []
        
        # 逐頁處理
        for i, temp_file in enumerate(temp_files, 1):
            print(f"\n處理第 {i} 頁...")
            try:
                # 處理單頁 PDF（使用重試機制）
                results = process_pdf_with_retry(parser, temp_file)
                
                # 如果成功，保存結果
                if "error" not in results:
                    try:
                        output_file = save_as_markdown(results, page_num=i)
                        output_files.append(output_file)
                        print(f"第 {i} 頁分析結果已保存至 {output_file}")
                        
                        # 顯示簡短摘要
                        if "data" in results and "markdown" in results["data"]:
                            chunks = results["data"].get("chunks", [])
                            content_types = set(chunk.get("chunk_type", "") for chunk in chunks)
                            print(f"- 識別出的內容區塊數：{len(chunks)}")
                            print(f"- 內容類型：{', '.join(content_types)}")
                            
                    except ValueError as e:
                        print(f"保存第 {i} 頁失敗：{str(e)}")
                else:
                    print(f"處理第 {i} 頁失敗：{results['error']}")
                    
            except Exception as e:
                print(f"處理第 {i} 頁時發生錯誤: {str(e)}")
            
            # 刪除臨時文件
            os.unlink(temp_file)
        
        # 合併所有結果
        if output_files:
            print("\n正在合併結果...")
            combined_file = combine_markdown_files(output_files)
            print(f"合併結果已保存至：{combined_file}")
            
    except Exception as e:
        print(f"處理 PDF 時發生錯誤: {str(e)}")


if __name__ == "__main__":
    main() 