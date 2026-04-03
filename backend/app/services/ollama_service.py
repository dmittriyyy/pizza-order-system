import os
import requests
from typing import List, Dict, Any, Optional, Callable


class OllamaService:    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        print(f"🦙 Ollama service initialized: {self.base_url}/{self.model}")
        self._warmup()
    
    def _warmup(self):
        try:
            requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "привет"}],
                    "stream": False
                },
                timeout=60
            )
            print("✅ Ollama модель прогрета")
        except Exception as e:
            print(f"⚠️ Прогрев не удался: {e}")
    
    def send_message(
        self, 
        messages: List[Dict], 
        temperature: float = 0.7,
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "max_tokens": 1000
                }
            }
            
            if tools:
                payload["tools"] = tools
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=180  # 180 секунд таймаут
            )
            response.raise_for_status()
            
            data = response.json()
            message = data.get("message", {})
            
            tool_calls = message.get("tool_calls", [])
            
            return {
                "content": message.get("content", ""),
                "tool_calls": tool_calls
            }
                
        except requests.exceptions.Timeout:
            print("⏱️ Timeout Ollama — модель думает слишком долго")
            return {
                "content": "Извините, я сейчас перегружен. Попробуйте ещё раз через минуту.",
                "tool_calls": []
            }
        except requests.exceptions.ConnectionError:
            print("❌ Ollama не запущена! Выполните: ollama serve")
            raise Exception("Ollama не запущена. Выполните: ollama serve")
        except Exception as e:
            print(f"❌ Ошибка Ollama: {e}")
            raise


ollama_service = OllamaService()

CART_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_to_cart",
            "description": "Добавить товар в корзину пользователя. Вызывай когда пользователь хочет добавить товар.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "integer",
                        "description": "ID товара из меню. Бери из поля 'id' в предоставленном меню."
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Количество товара. По умолчанию 1."
                    },
                    "comment": {
                        "type": "string",
                        "description": "Комментарий к заказу, например 'без лука', 'без помидор'. Если нет пожеланий — пустая строка."
                    }
                },
                "required": ["product_id", "quantity"]
            }
        }
    }
]
