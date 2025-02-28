import logging


def get_logger(name: str) -> logging.Logger:
    """獲取日誌記錄器

    Args:
        name (str): 日誌記錄器名稱

    Returns:
        logging.Logger: 配置好的日誌記錄器
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger 