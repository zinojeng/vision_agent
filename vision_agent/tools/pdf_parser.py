from typing import List, Dict, Any
import requests
import base64
from ..utils.config import Config
from ..utils.logger import get_logger


logger = get_logger(__name__)


class PDFParser:
    def __init__(self, config: Config):
        self.config = config
        self.api_url = "https://api.va.landing.ai/v1/tools/agentic-document-analysis"
        self.headers = {
            "Authorization": f"Bearer {config.landing_ai_api_key}",
            "Accept": "application/json"
        }
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """處理 PDF 文件

        Args:
            pdf_path (str): PDF 文件路徑

        Returns:
            Dict[str, Any]: API 回傳的分析結果
        """
        try:
            with open(pdf_path, "rb") as pdf_file:
                # 準備表單數據
                files = {
                    "pdf": ("document.pdf", pdf_file, "application/pdf")
                }
                data = {
                    "include_marginalia": "true",
                    "include_metadata_in_markdown": "true"
                }
                
                response = requests.post(
                    self.api_url,
                    files=files,
                    data=data,
                    headers=self.headers
                )
                
                if response.status_code == 422:
                    logger.error(f"API 回應內容: {response.text}")
                    
                response.raise_for_status()
                return response.json()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API 請求錯誤: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"錯誤詳情: {e.response.text}")
            if getattr(e, 'response', None) and e.response.status_code == 429:
                raise Exception("超過 API 請求限制，請稍後再試")
            raise Exception(f"處理 PDF 時發生錯誤: {str(e)}")
        except Exception as e:
            logger.error(f"處理 PDF 時發生錯誤: {str(e)}")
            raise 