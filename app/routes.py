from flask import Blueprint, render_template, jsonify
from app.services.parser_service import ParserService
from app.models import TennisCourt
from app import db
from datetime import datetime, timedelta
import threading

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

@main_bp.route('/update', methods=['POST'])
def update_data():
    """Маршрут для обновления данных"""
    global update_status
    
    if update_status['is_updating']:
        return jsonify({
            'status': 'error',
            'message': 'Обновление уже выполняется'
        }), 400
    
    def update_task():
        global update_status
        update_status['is_updating'] = True
        update_status['error'] = None
        
        try:
            # Создаем новое приложение для потока
            from app import create_app
            app = create_app()
            
            with app.app_context():
                service = ParserService(app)
                saved_count = service.update_all_data(app)
                
                update_status['last_update'] = datetime.now()
                update_status['is_updating'] = False
                
                return saved_count
        except Exception as e:
            update_status['error'] = str(e)
            update_status['is_updating'] = False
            raise
    
    # Запускаем обновление в отдельном потоке
    thread = threading.Thread(target=update_task)
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
    
    # Форматируем данные для JSON с правильными полями
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