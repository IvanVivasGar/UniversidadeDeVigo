from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from app.models.discussion import Discussion, DiscussionReply
from app.models.user import User
from app.utils.helpers import save_uploaded_file
import sys
import os
import json
from datetime import datetime

# Agregar sirope al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../sirope-master'))
import sirope

bp = Blueprint('discussions', __name__)

@bp.route('/')
def discussions():
    """Página principal de discusiones"""
    try:
        # Obtener parámetros de filtro y búsqueda
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        sort_by = request.args.get('sort', 'recent')
        page = int(request.args.get('page', 1))
        per_page = 10
        
        # Obtener todas las discusiones usando current_app.sirope
        all_discussions = list(current_app.sirope.load_all(Discussion))
        
        # Filtrar por búsqueda
        if search:
            all_discussions = [d for d in all_discussions 
                             if search.lower() in d.title.lower() or 
                                search.lower() in d.content.lower()]
        
        # Filtrar por categoría
        if category:
            all_discussions = [d for d in all_discussions if d.category == category]
        
        # Ordenar discusiones
        if sort_by == 'recent':
            all_discussions.sort(key=lambda x: x.created_at, reverse=True)
        elif sort_by == 'popular':
            all_discussions.sort(key=lambda x: len(x.likes), reverse=True)
        elif sort_by == 'active':
            all_discussions.sort(key=lambda x: x.last_activity, reverse=True)
        elif sort_by == 'oldest':
            all_discussions.sort(key=lambda x: x.created_at)
        
        # Paginación
        total_discussions = len(all_discussions)
        total_pages = (total_discussions + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        discussions_page = all_discussions[start_idx:end_idx]
        
        # Preparar datos con información de autores
        discussions_list = []
        for discussion in discussions_page:
            try:
                # Obtener el nombre del autor usando el método del modelo
                author_name = discussion.get_author_name(current_app.sirope)
                print(f"DEBUG: Discusión '{discussion.title}' - Autor: {author_name} (OID: {discussion.author_oid})")
                
                discussions_list.append({
                    'discussion': discussion,
                    'author_name': author_name,
                    'oid': str(discussion.__oid__) if hasattr(discussion, '__oid__') else None
                })
            except Exception as e:
                print(f"Error procesando discusión '{discussion.title}': {e}")
                # Agregar discusión con autor desconocido en caso de error
                discussions_list.append({
                    'discussion': discussion,
                    'author_name': "Usuario desconocido",
                    'oid': str(discussion.__oid__) if hasattr(discussion, '__oid__') else None
                })
                continue
        
        # Debug: Verificar que tenemos datos de autores
        print(f"DEBUG: Total de discusiones procesadas: {len(discussions_list)}")
        for item in discussions_list[:3]:  # Solo los primeros 3 para debug
            print(f"DEBUG: {item['discussion'].title} -> {item['author_name']}")
        
        # Estadísticas adicionales
        total_participants = len(set(d.author_oid for d in all_discussions))
        today = datetime.now().date()
        active_today = len([d for d in all_discussions 
                           if d.last_activity.date() == today])
        
        return render_template('discussions/discussions.html',
                             discussions=discussions_list,
                             page=page,
                             total_pages=total_pages,
                             total_discussions=total_discussions,
                             total_participants=total_participants,
                             active_today=active_today)
    
    except Exception as e:
        flash(f'Error al cargar las discusiones: {str(e)}', 'error')
        return render_template('discussions/discussions.html',
                             discussions=[],
                             page=1,
                             total_pages=1,
                             total_discussions=0,
                             total_participants=0,
                             active_today=0)

@bp.route('/<discussion_id>')
def discussion_detail(discussion_id):
    """Página de detalle de una discusión con respuestas"""
    try:
        discussion_oid = sirope.OID.from_text(discussion_id)
        discussion = current_app.sirope.load(discussion_oid)
        
        if not discussion:
            flash('Discusión no encontrada', 'error')
            return redirect(url_for('discussions.discussions'))
        
        # Incrementar contador de visualizaciones
        discussion.increment_views()
        current_app.sirope.save(discussion)
        
        # Obtener autor de la discusión usando el nuevo método
        author_name = discussion.get_author_name(current_app.sirope)
        
        # Obtener respuestas de la discusión con sus autores
        replies_with_authors = []
        for reply_oid in discussion.replies:
            try:
                reply = current_app.sirope.load(reply_oid)
                if reply:
                    reply_author_name = reply.get_author_name(current_app.sirope)
                    replies_with_authors.append({
                        'reply': reply,
                        'author_name': reply_author_name,
                        'oid': str(reply.__oid__) if hasattr(reply, '__oid__') else None
                    })
            except Exception as e:
                print(f"Error cargando respuesta {reply_oid}: {e}")
                continue
        
        # Ordenar respuestas por fecha
        replies_with_authors.sort(key=lambda r: r['reply'].created_at)
        
        # Verificar si el usuario actual ya dio like
        user_liked = False
        if current_user.is_authenticated:
            user_liked = discussion.has_liked(current_user.__oid__)
        
        # Obtener discusiones relacionadas por categoría
        related_discussions = []
        try:
            all_discussions = list(current_app.sirope.load_all(Discussion))
            related_discussions = [d for d in all_discussions 
                                 if d.category == discussion.category 
                                 and d.__oid__ != discussion.__oid__][:5]
        except:
            pass
        
        return render_template('discussions/discussion_detail.html', 
                             discussion=discussion, 
                             author_name=author_name,
                             replies_with_authors=replies_with_authors,
                             user_liked=user_liked,
                             related_discussions=related_discussions)
                             
    except Exception as e:
        print(f"Error cargando detalle de la discusión: {e}")
        flash('Error cargando la discusión', 'error')
        return redirect(url_for('discussions.discussions'))

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_discussion():
    """Crear nueva discusión"""
    if request.method == 'POST':
        # Detectar si es una petición AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            category = request.form.get('category', 'general')
            tags_json = request.form.get('tags', '[]')
            
            # Validaciones básicas
            if not title or not content:
                error_msg = 'Título y contenido son requeridos'
                if is_ajax:
                    return jsonify({'success': False, 'message': error_msg})
                flash(error_msg, 'error')
                return redirect(url_for('discussions.create_discussion'))
            
            if len(title) < 5:
                error_msg = 'El título debe tener al menos 5 caracteres'
                if is_ajax:
                    return jsonify({'success': False, 'message': error_msg})
                flash(error_msg, 'error')
                return redirect(url_for('discussions.create_discussion'))
            
            if len(content) < 20:
                error_msg = 'El contenido debe tener al menos 20 caracteres'
                if is_ajax:
                    return jsonify({'success': False, 'message': error_msg})
                flash(error_msg, 'error')
                return redirect(url_for('discussions.create_discussion'))
            
            # Parsear tags
            try:
                tags = json.loads(tags_json) if tags_json else []
            except:
                tags = []
            
            # Crear discusión
            discussion = Discussion(title, content, current_user.__oid__, category)
            
            # Agregar tags
            for tag in tags[:10]:  # Máximo 10 tags
                discussion.add_tag(tag.strip())
            
            # Procesar imagen opcional
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    try:
                        image_url = save_uploaded_file(file, 'discussions')
                        if image_url:
                            discussion.image_url = image_url
                    except Exception as e:
                        print(f"Error subiendo imagen: {e}")
            
            # Guardar discusión
            oid = current_app.sirope.save(discussion)
            
            success_msg = 'Discusión creada exitosamente'
            if is_ajax:
                return jsonify({
                    'success': True, 
                    'message': success_msg,
                    'discussion_id': str(oid),
                    'redirect_url': url_for('discussions.discussion_detail', discussion_id=str(oid))
                })
            
            flash(success_msg, 'success')
            return redirect(url_for('discussions.discussion_detail', discussion_id=str(oid)))
            
        except Exception as e:
            print(f"Error creando discusión: {e}")
            error_msg = 'Error creando la discusión'
            if is_ajax:
                return jsonify({'success': False, 'message': error_msg})
            flash(error_msg, 'error')
            return redirect(url_for('discussions.create_discussion'))
    
    # GET request - mostrar formulario
    return render_template('discussions/create_discussion.html')

@bp.route('/<discussion_id>/like', methods=['POST'])
@login_required
def toggle_like_discussion(discussion_id):
    """Dar o quitar like a una discusión"""
    try:
        discussion_oid = sirope.OID.from_text(discussion_id)
        discussion = current_app.sirope.load(discussion_oid)
        
        if not discussion:
            return jsonify({'success': False, 'message': 'Discusión no encontrada'})
        
        user_oid = current_user.__oid__
        
        # Toggle like
        if discussion.has_liked(user_oid):
            discussion.remove_like(user_oid)
            liked = False
            message = 'Like removido'
        else:
            discussion.add_like(user_oid)
            liked = True
            message = 'Like agregado'
        
        current_app.sirope.save(discussion)
        
        return jsonify({
            'success': True,
            'message': message,
            'liked': liked,
            'like_count': discussion.like_count
        })
        
    except Exception as e:
        print(f"Error con like de la discusión: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/<discussion_id>/reply', methods=['POST'])
@login_required
def add_reply(discussion_id):
    """Agregar respuesta a una discusión"""
    try:
        content = request.form.get('content', '').strip()
        parent_reply_id = request.form.get('parent_reply_id')
        
        if not content:
            return jsonify({'success': False, 'message': 'El contenido de la respuesta es requerido'})
        
        if len(content) < 5:
            return jsonify({'success': False, 'message': 'La respuesta debe tener al menos 5 caracteres'})
        
        discussion_oid = sirope.OID.from_text(discussion_id)
        discussion = current_app.sirope.load(discussion_oid)
        
        if not discussion:
            return jsonify({'success': False, 'message': 'Discusión no encontrada'})
        
        if discussion.is_closed:
            return jsonify({'success': False, 'message': 'Esta discusión está cerrada'})
        
        # Procesar respuesta padre si existe
        parent_reply_oid = None
        if parent_reply_id:
            try:
                parent_reply_oid = sirope.OID.from_text(parent_reply_id)
                # Verificar que la respuesta padre existe
                parent_reply = current_app.sirope.load(parent_reply_oid)
                if not parent_reply:
                    parent_reply_oid = None
            except:
                parent_reply_oid = None
        
        # Crear respuesta
        reply = DiscussionReply(content, current_user.__oid__, discussion_oid, parent_reply_oid)
        reply_oid = current_app.sirope.save(reply)
        
        # Agregar respuesta a la discusión
        discussion.add_reply(reply_oid)
        current_app.sirope.save(discussion)
        
        return jsonify({
            'success': True,
            'message': 'Respuesta agregada exitosamente',
            'reply_count': discussion.get_replies_count(),
            'reply_id': str(reply_oid)
        })
        
    except Exception as e:
        print(f"Error agregando respuesta: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/reply/<reply_id>/like', methods=['POST'])
@login_required
def toggle_like_reply(reply_id):
    """Dar o quitar like a una respuesta"""
    try:
        reply_oid = sirope.OID.from_text(reply_id)
        reply = current_app.sirope.load(reply_oid)
        
        if not reply:
            return jsonify({'success': False, 'message': 'Respuesta no encontrada'})
        
        user_oid = current_user.__oid__
        
        # Toggle like
        if reply.has_liked(user_oid):
            reply.remove_like(user_oid)
            liked = False
            message = 'Like removido'
        else:
            reply.add_like(user_oid)
            liked = True
            message = 'Like agregado'
        
        current_app.sirope.save(reply)
        
        return jsonify({
            'success': True,
            'message': message,
            'liked': liked,
            'like_count': reply.like_count
        })
        
    except Exception as e:
        print(f"Error con like de la respuesta: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/<discussion_id>/close', methods=['POST'])
@login_required
def close_discussion(discussion_id):
    """Cerrar una discusión (solo el autor o admin)"""
    try:
        discussion_oid = sirope.OID.from_text(discussion_id)
        discussion = current_app.sirope.load(discussion_oid)
        
        if not discussion:
            return jsonify({'success': False, 'message': 'Discusión no encontrada'})
        
        # Verificar permisos (autor o admin)
        if discussion.author_oid != current_user.__oid__ and not getattr(current_user, 'is_admin', False):
            return jsonify({'success': False, 'message': 'Sin permisos para cerrar esta discusión'})
        
        discussion.close()
        current_app.sirope.save(discussion)
        
        return jsonify({
            'success': True,
            'message': 'Discusión cerrada exitosamente'
        })
        
    except Exception as e:
        print(f"Error cerrando discusión: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/<discussion_id>/pin', methods=['POST'])
@login_required
def pin_discussion(discussion_id):
    """Fijar una discusión (solo admin)"""
    try:
        if not getattr(current_user, 'is_admin', False):
            return jsonify({'success': False, 'message': 'Sin permisos para fijar discusiones'})
        
        discussion_oid = sirope.OID.from_text(discussion_id)
        discussion = current_app.sirope.load(discussion_oid)
        
        if not discussion:
            return jsonify({'success': False, 'message': 'Discusión no encontrada'})
        
        if discussion.is_pinned:
            discussion.unpin()
            message = 'Discusión desfijada'
        else:
            discussion.pin()
            message = 'Discusión fijada'
        
        current_app.sirope.save(discussion)
        
        return jsonify({
            'success': True,
            'message': message,
            'is_pinned': discussion.is_pinned
        })
        
    except Exception as e:
        print(f"Error fijando discusión: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/reply/<reply_id>/solution', methods=['POST'])
@login_required
def toggle_solution(reply_id):
    """Marcar o desmarcar una respuesta como solución (solo el autor de la discusión)"""
    try:
        reply_oid = sirope.OID.from_text(reply_id)
        reply = current_app.sirope.load(reply_oid)
        
        if not reply:
            return jsonify({'success': False, 'message': 'Respuesta no encontrada'})
        
        # Obtener la discusión para verificar permisos
        discussion = current_app.sirope.load(reply.discussion_oid)
        if not discussion:
            return jsonify({'success': False, 'message': 'Discusión no encontrada'})
        
        # Verificar que solo el autor de la discusión puede marcar soluciones
        if discussion.author_oid != current_user.__oid__:
            return jsonify({'success': False, 'message': 'Solo el autor de la discusión puede marcar soluciones'})
        
        # Toggle solución
        if reply.is_solution:
            reply.unmark_as_solution()
            message = 'Respuesta desmarcada como solución'
        else:
            # Desmarcar otras soluciones existentes en la misma discusión
            for other_reply_oid in discussion.replies:
                try:
                    other_reply = current_app.sirope.load(other_reply_oid)
                    if other_reply and other_reply.is_solution and other_reply.__oid__ != reply.__oid__:
                        other_reply.unmark_as_solution()
                        current_app.sirope.save(other_reply)
                except:
                    continue
            
            reply.mark_as_solution()
            message = 'Respuesta marcada como solución'
        
        current_app.sirope.save(reply)
        
        return jsonify({
            'success': True,
            'message': message,
            'is_solution': reply.is_solution
        })
        
    except Exception as e:
        print(f"Error marcando solución: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})