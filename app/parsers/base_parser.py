from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import logging
import time
import os
import platform
import subprocess
from pathlib import Path

class BaseParser(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_logger()
        
    def setup_logger(self):
        """Настройка логгера для парсера"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    @abstractmethod
    def get_courts_data(self):
        """
        Абстрактный метод для получения данных о кортах
        Должен возвращать список словарей с данными:
        {
            'club_name': str,
            'court_number': str, 
            'date': datetime.date,
            'time_slot': str,
            'status': str  # 'свободен' или 'занят'
        }
        """
        pass
    
    def safe_parse(self, func, max_retries=3, delay=2):
        """
        Безопасное выполнение парсинга с повторными попытками
        """
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                self.logger.warning(f"Попытка {attempt + 1} не удалась: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(delay * (attempt + 1))
                else:
                    self.logger.error(f"Все попытки парсинга не удалась после {max_retries} попыток")
                    raise
    
    def normalize_time(self, time_str):
        """Нормализация формата времени"""
        time_str = time_str.strip().lower()
        
        # Замена общих форматов
        replacements = {
            'утро': '09:00',
            'день': '13:00', 
            'вечер': '18:00',
            'ночь': '21:00',
            'полдень': '12:00'
        }
        
        for key, value in replacements.items():
            if key in time_str:
                return value
        
        # Очистка от лишних символов
        time_str = ''.join(c for c in time_str if c.isdigit() or c in ':.-')
        
        # Если есть точка - заменяем на двоеточие
        time_str = time_str.replace('.', ':')
        
        # Если только часы - добавляем минуты
        if ':' not in time_str and len(time_str) <= 2:
            return f"{int(time_str):02d}:00"
        
        # Если формат HH:MM
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) >= 2:
                hours = int(parts[0])
                minutes = int(parts[1][:2]) if len(parts[1]) >= 2 else 0
                
                # Нормализация часов (24-часовой формат)
                if hours > 23:
                    hours = hours % 24
                
                return f"{hours:02d}:{minutes:02d}"
        
        return time_str
    
    def normalize_date(self, date_str, base_date=None):
        """Нормализация даты"""
        if not base_date:
            base_date = datetime.now()
        
        date_str = date_str.strip().lower()
        
        # Сегодня/завтра
        if 'сегодня' in date_str:
            return base_date.date()
        elif 'завтра' in date_str:
            return (base_date + timedelta(days=1)).date()
        
        # Дни недели
        weekdays = {
            'пн': 0, 'понедельник': 0,
            'вт': 1, 'вторник': 1,
            'ср': 2, 'среда': 2,
            'чт': 3, 'четверг': 3,
            'пт': 4, 'пятница': 4,
            'сб': 5, 'суббота': 5,
            'вс': 6, 'воскресенье': 6
        }
        
        for weekday_name, weekday_num in weekdays.items():
            if weekday_name in date_str:
                # Находим следующий такой день недели
                days_ahead = weekday_num - base_date.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                return (base_date + timedelta(days=days_ahead)).date()
        
        # Попытка распарсить стандартные форматы даты
        from dateutil import parser
        try:
            parsed_date = parser.parse(date_str, dayfirst=True)
            return parsed_date.date()
        except:
            self.logger.warning(f"Не удалось распарсить дату: {date_str}")
            return base_date.date()
    
    def get_chromedriver_path(self):
        """Надежный поиск пути к ChromeDriver для snap-версии"""
        import platform
        
        # Список возможных путей для snap-версии
        snap_paths = [
            '/snap/bin/chromium.chromedriver',
            '/snap/chromium/current/usr/lib/chromium-browser/chromedriver'
        ]
        
        # Стандартные пути
        standard_paths = [
            str(Path(__file__).parent.parent.parent / 'drivers' / 'chromedriver'),
            str(Path(__file__).parent.parent.parent / 'drivers' / 'chromedriver_linux64'),
            '/usr/bin/chromedriver',
            '/usr/local/bin/chromedriver',
            '/usr/lib/chromium-browser/chromedriver'
        ]
        
        all_paths = snap_paths + standard_paths
        
        for path in all_paths:
            if os.path.exists(path):
                self.logger.info(f"Найден файл драйвера: {path}")
                
                # Проверяем права на выполнение
                if not os.access(path, os.X_OK):
                    try:
                        os.chmod(path, 0o755)
                        self.logger.info(f"Права на выполнение установлены для: {path}")
                    except Exception as e:
                        self.logger.warning(f"Не удалось установить права для {path}: {str(e)}")
                
                # Проверяем версию
                try:
                    result = subprocess.run([path, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        version_info = result.stdout.strip()
                        self.logger.info(f"✅ ChromeDriver найден: {path}")
                        self.logger.info(f"Версия: {version_info}")
                        return path
                    else:
                        self.logger.warning(f"Файл существует, но не является ChromeDriver: {path}")
                except Exception as e:
                    self.logger.warning(f"Ошибка при проверке {path}: {str(e)}")
        
        # Если ничего не найдено, пробуем установить автоматически
        self.logger.error("❌ ChromeDriver не найден ни в одном из путей:")
        for path in all_paths:
            self.logger.error(f"  - {path}")
        
        # Emergency: используем тестовые данные
        self.logger.error("🚨 EMERGENCY MODE: ChromeDriver недоступен. Будут использоваться ТОЛЬКО тестовые данные.")
        return None
