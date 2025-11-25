from flask import Blueprint, render_template, jsonify
from app.services.parser_service import ParserService
from app.models import TennisCourt
from app import db
from datetime import datetime, timedelta
import threading
import asyncio

main_bp = Blueprint('main', __name__)

# Глобальная переменная для отслеживания статуса обновления
update_status = {
    'is_updating': False,
    'last_update': None,
    'error': None
}

@main_bp.route('/')
def index():
    # Получаем данные для отображения (только актуальные)
    today = datetime.now().date()
    courts = TennisCourt.query.filter(
        TennisCourt.date >= today
    ).order_by(
        TennisCourt.date,
        TennisCourt.time_slot,
        TennisCourt.club_name,
        TennisCourt.court_number
    ).all()
    
    return render_template('index.html', courts=courts, update_status=update_status)

def update_task(app):
    """Функция для выполнения в отдельном потоке с передачей приложения"""
    global update_status
    update_status['is_updating'] = True
    update_status['error'] = None
    
    try:
        with app.app_context():
            service = ParserService(app)
            
            # Создаем новый event loop для асинхронного вызова
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Запускаем асинхронную задачу
            saved_count = loop.run_until_complete(service.update_all_data(app))
            
            update_status['last_update'] = datetime.now()
            update_status['is_updating'] = False
            
            return saved_count
    except Exception as e:
        update_status['error'] = str(e)
        update_status['is_updating'] = False
        raise

@main_bp.route('/update', methods=['POST'])
def update_data():
    """Маршрут для обновления данных"""
    global update_status
    
    if update_status['is_updating']:
        return jsonify({
            'status': 'error',
            'message': 'Обновление уже выполняется'
        }), 400
    
    # Создаем новое приложение для потока
    from app import create_app
    app = create_app()
    
    # Запускаем обновление в отдельном потоке с передачей приложения
    thread = threading.Thread(target=update_task, args=(app,))
    thread.start()
    
    return jsonify({
        'status': 'success',
        'message': 'Обновление запущено в фоновом режиме'
    })

@main_bp.route('/status')
def update_status_route():
    """Получение статуса обновления"""
    global update_status
    
    status_response = {
        'is_updating': update_status['is_updating'],
        'last_update': update_status['last_update'].isoformat() if update_status['last_update'] else None,
        'error': update_status['error']
    }
    
    return jsonify(status_response)

@main_bp.route('/data')
def get_data():
    """Получение данных для AJAX обновления таблицы"""
    today = datetime.now().date()
    courts = TennisCourt.query.filter(
        TennisCourt.date >= today
    ).order_by(
        TennisCourt.date,
        TennisCourt.time_slot,
        TennisCourt.club_name,
        TennisCourt.court_number
    ).all()
    
    # Форматируем данные для JSON
    data = []
    for court in courts:
        data.append({
            'day_of_week': court.date.strftime('%A'),
            'date': court.date.strftime('%Y-%m-%d'),  # Для фильтрации
            'time': court.time_slot,
            'club': court.club_name,
            'court_number': court.court_number,
            'status': court.status,
            'status_class': 'success' if court.status == 'свободен' else 'danger'
        })
    
    return jsonify(data)