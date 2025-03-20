# /tenismatch/apps/tenis_admin/utils.py

import time
import logging
from functools import wraps

logger = logging.getLogger('tenismatch')

class TimingUtil:
    @staticmethod
    def log_execution_time(func):
        """Decorator para medir e logar o tempo de execução de funções"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Função {func.__name__} executada em {execution_time:.4f} segundos")
            return result
        return wrapper
    
    @staticmethod
    def time_block(block_name):
        """Context manager para medir e logar o tempo de blocos de código"""
        class TimerContext:
            def __init__(self, name):
                self.name = name
                
            def __enter__(self):
                self.start_time = time.time()
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                execution_time = time.time() - self.start_time
                logger.info(f"Bloco {self.name} executado em {execution_time:.4f} segundos")
        
        return TimerContext(block_name)