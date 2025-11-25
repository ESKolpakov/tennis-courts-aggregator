import asyncio
from app.parsers.yclients_adv_parser import YClientsAdvParser
from app.parsers.findsport_parser import FindSportParser
from app.parsers.tsaritsyno_parser import TsaritsynoParser
from app.models import TennisCourt
from app import db
from datetime import datetime
import logging

class ParserService:
    def __init__(self, app=None):
        self.logger = logging.getLogger('ParserService')
        self.setup_logger()
        self.app = app
        
        # Список парсеров
        self.parsers = [
            YClientsAdvParser(),
            FindSportParser(),
            TsaritsynoParser()
        ]
    
    def setup_logger(self):
        """Настройка логгера"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    async def parse_all_clubs(self):
        """Асинхронный парсинг данных со всех клубов"""
        self.logger.info("=== Начало парсинга всех клубов ===")
        all_data = []
        
        for parser in self.parsers:
            try:
                self.logger.info(f"Парсинг клуба: {parser.club_name}")
                club_data = await parser.get_courts_data()
                
                if club_data:
                    all_data.extend(club_data)
                    self.logger.info(f"Получено данных от {parser.club_name}: {len(club_data)} записей")
                else:
                    self.logger.warning(f"Нет данных от {parser.club_name}")
            
            except Exception as e:
                self.logger.error(f"Ошибка при парсинге {parser.club_name}: {str(e)}")
                continue
        
        self.logger.info(f"=== Парсинг завершен. Всего получено: {len(all_data)} записей ===")
        return all_data
    
    def save_to_database(self, data, app=None):
        """Сохранение данных в базу данных"""
        self.logger.info("=== Начало сохранения данных в БД ===")
        
        try:
            # Создаем контекст приложения, если его нет
            if app is None:
                from app import create_app
                app = create_app()
            
            with app.app_context():
                saved_count = 0
                for record in data:
                    try:
                        # Создаем или обновляем запись
                        court = TennisCourt(
                            club_name=record['club_name'],
                            court_number=record['court_number'],
                            date=record['date'],
                            time_slot=record['time_slot'],
                            status=record['status']
                        )
                        
                        # Проверяем, существует ли уже такая запись
                        existing = TennisCourt.query.filter_by(
                            club_name=record['club_name'],
                            court_number=record['court_number'],
                            date=record['date'],
                            time_slot=record['time_slot']
                        ).first()
                        
                        if existing:
                            # Обновляем существующую запись
                            existing.status = record['status']
                            existing.updated_at = datetime.utcnow()
                            saved_count += 1
                        else:
                            # Добавляем новую запись
                            db.session.add(court)
                            saved_count += 1
                    
                    except Exception as e:
                        self.logger.error(f"Ошибка при сохранении записи {record}: {str(e)}")
                        continue
                
                db.session.commit()
                self.logger.info(f"=== Успешно сохранено в БД: {saved_count} записей ===")
                return saved_count
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Ошибка при сохранении в БД: {str(e)}")
            raise
    
    async def update_all_data(self, app=None):
        """Полный цикл: парсинг + сохранение"""
        self.logger.info("=== Запуск полного обновления данных ===")
        
        try:
            # Получаем данные
            data = await self.parse_all_clubs()
            
            if data:
                # Сохраняем в БД
                saved_count = self.save_to_database(data, app)
                self.logger.info(f"=== Обновление завершено успешно. Сохранено: {saved_count} записей ===")
                return saved_count
            else:
                self.logger.warning("=== Нет данных для сохранения ===")
                return 0
        
        except Exception as e:
            self.logger.error(f"=== Критическая ошибка при обновлении: {str(e)} ===")
            raise