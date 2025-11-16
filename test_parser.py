import sys
import os
from pathlib import Path

# Добавляем корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from app.parsers.yclients_parser import YClientsParser

def test_yclients_parser():
    print("=== Тестирование YClients парсера ===")
    
    try:
        parser = YClientsParser()
        print("Парсер создан успешно")
        
        print("Запуск парсинга...")
        data = parser.get_courts_data()
        
        print(f"Получено записей: {len(data)}")
        
        if data:
            print("\nПример полученных данных:")
            for i, record in enumerate(data[:5], 1):
                print(f"{i}. {record}")
        
        print("\n✅ Тест успешно завершен!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {str(e)}")
        return False

if __name__ == "__main__":
    test_yclients_parser()
