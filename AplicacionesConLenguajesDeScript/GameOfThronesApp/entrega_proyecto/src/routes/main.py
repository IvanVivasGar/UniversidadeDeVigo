from flask import Blueprint, render_template, current_app
from app.models.character import Character
from app.models.house import House
from app.models.event import Event
from app.models.post import Post
from app.models.discussion import Discussion
from app.utils.helpers import get_latest_entities

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Página principal con últimos elementos de cada sección"""
    try:
        sirope = current_app.sirope
        
        # Obtener últimos elementos de cada sección
        latest_characters = get_latest_entities(sirope, Character, 2)
        latest_houses = get_latest_entities(sirope, House, 2)
        latest_events = get_latest_entities(sirope, Event, 2)
        
        # Calcular totales para los contadores
        total_characters = len(list(sirope.load_all(Character)))
        total_houses = len(list(sirope.load_all(House)))
        total_events = len(list(sirope.load_all(Event)))
        total_posts = len(list(sirope.load_all(Post)))
        total_discussions = len(list(sirope.load_all(Discussion)))
        
        # Obtener último post
        latest_post = None
        try:
            posts = list(sirope.load_all(Post))
            if posts:
                posts.sort(key=lambda p: p.created_at, reverse=True)
                latest_post = posts[0]
        except:
            pass
        
        # Calcular estadísticas adicionales
        avg_character_rating = 0
        avg_house_rating = 0
        avg_event_importance = 0
        total_likes = 0
        
        try:
            # Promedio de calificaciones de personajes
            characters = list(sirope.load_all(Character))
            if characters:
                ratings = [c.get_average_rating() for c in characters if c.get_average_rating() > 0]
                if ratings:
                    avg_character_rating = round(sum(ratings) / len(ratings), 1)
            
            # Promedio de calificaciones de casas
            houses = list(sirope.load_all(House))
            if houses:
                ratings = [h.get_average_rating() for h in houses if h.get_average_rating() > 0]
                if ratings:
                    avg_house_rating = round(sum(ratings) / len(ratings), 1)
            
            # Promedio de importancia de eventos
            events = list(sirope.load_all(Event))
            if events:
                importances = [e.importance_rating for e in events if e.importance_rating]
                if importances:
                    avg_event_importance = round(sum(importances) / len(importances), 1)
            
            # Total de likes
            posts = list(sirope.load_all(Post))
            total_likes = sum(p.like_count for p in posts)
            
        except Exception as e:
            print(f"Error calculando estadísticas: {e}")
        
        return render_template('index.html',
                             latest_characters=latest_characters,
                             latest_houses=latest_houses,
                             latest_events=latest_events,
                             latest_post=latest_post,
                             total_characters=total_characters,
                             total_houses=total_houses,
                             total_events=total_events,
                             total_posts=total_posts,
                             total_discussions=total_discussions,
                             avg_character_rating=avg_character_rating,
                             avg_house_rating=avg_house_rating,
                             avg_event_importance=avg_event_importance,
                             total_likes=total_likes)
    except Exception as e:
        print(f"Error en página principal: {e}")
        return render_template('index.html',
                             latest_characters=[],
                             latest_houses=[],
                             latest_events=[],
                             latest_post=None,
                             total_characters=0,
                             total_houses=0,
                             total_events=0,
                             total_posts=0,
                             total_discussions=0,
                             avg_character_rating=0,
                             avg_house_rating=0,
                             avg_event_importance=0,
                             total_likes=0)

@bp.route('/about')
def about():
    """Página de información sobre WesterosTracker"""
    return render_template('about.html')