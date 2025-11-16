import sys
import os
from pathlib import Path

# Добавляем корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

print("=== Проверка импортов ===")

try:
    from app import create_app
    print("✅ app.create_app импортирован успешно")
    
    from app.services.parser_service import ParserService
    print("✅ app.services.parser_service импортирован успешно")
    
    from app.parsers.yclients_parser import YClientsParser
    print("✅ app.parsers.yclients_parser импортирован успешно")
    
    from app.models import TennisCourt
    print("✅ app.models.TennisCourt импортирован успешно")
    
    print("\n🎉 Все импорты работают корректно!")
    
except Exception as e:
    print(f"❌ Ошибка при импорте: {str(e)}")
    print("Текущий PYTHONPATH:", sys.path)
    sys.exit(1)
