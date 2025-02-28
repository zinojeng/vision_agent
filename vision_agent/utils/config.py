import os
from pydantic import BaseModel, ConfigDict


class Config(BaseModel):
    """配置類
    
    Attributes:
        landing_ai_api_key (str): LandingAI API 金鑰
        anthropic_api_key (str): Anthropic API 金鑰
        openai_api_key (str): OpenAI API 金鑰
        max_tokens (int): 最大 token 數
        model (str): 使用的模型名稱
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    landing_ai_api_key: str
    anthropic_api_key: str
    openai_api_key: str
    max_tokens: int = 8000
    model: str = "gpt-4-turbo"  # 使用正確的模型名稱

    def __init__(self, **data):
        """初始化配置
        
        從環境變數讀取配置信息
        """
        super().__init__(**data)
        self.landing_ai_api_key = os.getenv("LANDING_AI_API_KEY")
        if not self.landing_ai_api_key:
            raise ValueError("需要設置 LANDING_AI_API_KEY 環境變數")
            
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            raise ValueError("需要設置 ANTHROPIC_API_KEY 環境變數")
            
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("需要設置 OPENAI_API_KEY 環境變數") 