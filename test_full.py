import sys
import os
from pathlib import Path
from app.parsers.yclients_parser import YClientsParser
from app.services.parser_service import ParserService
from app import create_app, db

def test_full_system():
    print("=== ТЕСТ ПОЛНОЙ СИСТЕМЫ ===")
    
    # Тест 1: Импорты
    print("\n🔍 Тест 1: Проверка импортов")
    try:
        from app import create_app
        from app.services.parser_service import ParserService
        from app.parsers.yclients_parser import YClientsParser
        print("✅ Все импорты работают")
    except Exception as e:
        print(f"❌ Ошибка импортов: {str(e)}")
        return False
    
    # Тест 2: ChromeDriver
    print("\n🔍 Тест 2: Проверка ChromeDriver")
    parser = YClientsParser()
    driver_path = parser.get_chromedriver_path()
    if driver_path:
        print(f"✅ ChromeDriver найден: {driver_path}")
    else:
        print("⚠️ ChromeDriver не найден, но система продолжит работу с тестовыми данными")
    
    # Тест 3: Парсинг данных
    print("\n🔍 Тест 3: Парсинг данных")
    try:
        data = parser.get_courts_data()
        print(f"✅ Получено данных: {len(data)} записей")
        
        if data:
            print("Пример данных:")
            for i, item in enumerate(data[:3], 1):
                print(f"  {i}. {item}")
    except Exception as e:
        print(f"❌ Ошибка парсинга: {str(e)}")
        return False
    
    # Тест 4: Работа с базой данных
    print("\n🔍 Тест 4: Работа с базой данных")
    app = create_app()
    with app.app_context():
        try:
            # Очищаем старые данные
            from app.models import TennisCourt
            db.session.query(TennisCourt).delete()
            db.session.commit()
            
            # Сохраняем тестовые данные
            service = ParserService()
            saved_count = service.save_to_database(data)
            print(f"✅ Сохранено в БД: {saved_count} записей")
            
            # Проверяем чтение из БД
            courts = TennisCourt.query.all()
            print(f"✅ Прочитано из БД: {len(courts)} записей")
            
        except Exception as e:
            print(f"❌ Ошибка работы с БД: {str(e)}")
            return False
    
    print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    return True

if __name__ == "__main__":
    success = test_full_system()
    sys.exit(0 if success else 1)