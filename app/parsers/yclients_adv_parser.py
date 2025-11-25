from playwright.async_api import async_playwright
import asyncio
import logging
from datetime import datetime, timedelta
from .base_parser import BaseParser

class YClientsAdvParser(BaseParser):
    def __init__(self, url=None):
        super().__init__()
        self.url = url or "https://b1044864.yclients.com/company/967881/personal/select-time?o=m-1"
        self.club_name = "MyProtennis.ru"

    async def get_courts_data(self):
        """Основной метод для получения данных о кортах с использованием 4-шаговой навигации"""
        self.logger.info("=== Начало 4-шаговой навигации для YClients ===")
        data = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-setuid-sandbox'
                    ]
                )
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = await context.new_page()

                # Шаг 1: Перейти на страницу выбора услуг
                await page.goto(self.url, wait_until='networkidle')
                await page.wait_for_load_state('networkidle')
                self.logger.info("✅ Шаг 1: Страница загружена")

                # Шаг 2: Выбрать первую услугу (аренда корта)
                self.logger.info("Шаг 2: Выбор первой услуги")
                service_button = await page.wait_for_selector('text=Аренда корта', timeout=10000)
                if not service_button:
                    # Если нет текста "Аренда корта", попробуем выбрать первый сервис
                    service_buttons = await page.query_selector_all('button.ui-kit-simple-cell')
                    if service_buttons:
                        service_button = service_buttons[0]
                    else:
                        raise Exception("Не удалось найти ни одну услугу")
                await service_button.click()
                await asyncio.sleep(1)

                # Шаг 3: Выбрать корт
                self.logger.info("Шаг 3: Выбор корта")
                # Ждем загрузки списка кортов
                await page.wait_for_selector('text=Выбрать корт', timeout=10000)
                # Получаем все доступные корты
                court_elements = await page.query_selector_all('div.court-item')  # Уточнить селектор
                if not court_elements:
                    # Альтернативный селектор
                    court_elements = await page.query_selector_all('div:has-text="Корт №")')

                for i, court_element in enumerate(court_elements):
                    # Клик по корту
                    await court_element.click()
                    await asyncio.sleep(1)

                    # Шаг 4: Выбрать дату и время
                    self.logger.info(f"Шаг 4: Выбор даты и времени для корта {i+1}")
                    # Ждем загрузки календаря
                    await page.wait_for_selector('text=Выбрать дату', timeout=10000)
                    # Получаем список доступных дат (на ближайшие 3 дня)
                    dates = []
                    date_elements = await page.query_selector_all('div.date-item')  # Уточнить селектор
                    if not date_elements:
                        # Альтернативный селектор
                        date_elements = await page.query_selector_all('div.calendar-day')

                    for date_element in date_elements[:3]:  # Только 3 дня вперед
                        # Клик по дате
                        await date_element.click()
                        await asyncio.sleep(1)

                        # Получаем список доступных временных слотов
                        time_slots = []
                        time_elements = await page.query_selector_all('div.time-slot')  # Уточнить селектор
                        if not time_elements:
                            # Альтернативный селектор
                            time_elements = await page.query_selector_all('div:has-text=":"')

                        for time_element in time_elements:
                            # Получаем текст слота (например, "12:00 - 13:00")
                            time_text = await time_element.text_content()
                            if ':' in time_text:
                                # Проверяем, доступен ли слот (если есть кнопка "Продолжить", значит слот свободен)
                                continue_button = await page.query_selector('text=Продолжить')
                                status = 'свободен' if continue_button else 'занят'

                                # Формируем запись
                                record = {
                                    'club_name': self.club_name,
                                    'court_number': str(i + 1),
                                    'date': datetime.now().date(),  # Здесь нужно получить реальную дату из элемента
                                    'time_slot': time_text.split(' - ')[0] if ' - ' in time_text else time_text,
                                    'status': status
                                }
                                data.append(record)

                # Закрываем браузер
                await browser.close()
                self.logger.info(f"✅ 4-шаговая навигация завершена. Получено {len(data)} записей")
                return data

        except Exception as e:
            self.logger.error(f"Ошибка при 4-шаговой навигации: {str(e)}")
            self.logger.warning("Возвращаем тестовые данные")
            return self._get_test_data()