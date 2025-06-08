from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from app.models.post import Post, Comment
from app.models.user import User
import sys
import os

# Agregar sirope al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../sirope-master'))
import sirope

bp = Blueprint('posts', __name__)

@bp.route('/')
def posts():
    """Página principal de posts ordenados por fecha"""
    try:
        posts_list = list(current_app.sirope.load_all(Post))
        posts_list.sort(key=lambda p: p.created_at, reverse=True)
        
        # Obtener información de autores para cada post
        posts_with_authors = []
        for post in posts_list:
            try:
                author = current_app.sirope.load(post.author_oid)
                posts_with_authors.append((post, author))
            except:
                posts_with_authors.append((post, None))
        
        return render_template('posts/posts.html', posts_with_authors=posts_with_authors)
        
    except Exception as e:
        print(f"Error cargando posts: {e}")
        return render_template('posts/posts.html', posts_with_authors=[])

@bp.route('/<post_id>')
def post_detail(post_id):
    """Página de detalle de un post con comentarios"""
    try:
        post_oid = sirope.OID.from_text(post_id)
        post = current_app.sirope.load(post_oid)
        
        if not post:
            flash('Post no encontrado', 'error')
            return redirect(url_for('posts.posts'))
        
        # Obtener autor del post
        author = None
        try:
            author = current_app.sirope.load(post.author_oid)
        except:
            pass
        
        # Obtener comentarios del post
        comments_with_authors = []
        for comment_oid in post.comments:
            try:
                comment = current_app.sirope.load(comment_oid)
                if comment:
                    comment_author = None
                    try:
                        comment_author = current_app.sirope.load(comment.author_oid)
                    except:
                        pass
                    comments_with_authors.append((comment, comment_author))
            except:
                continue
        
        # Ordenar comentarios por fecha
        comments_with_authors.sort(key=lambda c: c[0].created_at)
        
        return render_template('posts/post_detail.html', 
                             post=post, 
                             author=author,
                             comments_with_authors=comments_with_authors)
                             
    except Exception as e:
        print(f"Error cargando detalle del post: {e}")
        flash('Error cargando el post', 'error')
        return redirect(url_for('posts.posts'))

@bp.route('/<post_id>/like', methods=['POST'])
@login_required
def toggle_like_post(post_id):
    """Dar o quitar like a un post"""
    try:
        post_oid = sirope.OID.from_text(post_id)
        post = current_app.sirope.load(post_oid)
        
        if not post:
            return jsonify({'success': False, 'message': 'Post no encontrado'})
        
        user_oid = current_user.__oid__
        
        # Toggle like
        if post.has_liked(user_oid):
            post.remove_like(user_oid)
            liked = False
            message = 'Like removido'
        else:
            post.add_like(user_oid)
            liked = True
            message = 'Like agregado'
        
        current_app.sirope.save(post)
        
        return jsonify({
            'success': True,
            'message': message,
            'liked': liked,
            'like_count': post.like_count
        })
        
    except Exception as e:
        print(f"Error con like del post: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/<post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Agregar comentario a un post"""
    try:
        content = request.form.get('content')
        
        if not content:
            return jsonify({'success': False, 'message': 'El contenido del comentario es requerido'})
        
        post_oid = sirope.OID.from_text(post_id)
        post = current_app.sirope.load(post_oid)
        
        if not post:
            return jsonify({'success': False, 'message': 'Post no encontrado'})
        
        # Crear comentario
        comment = Comment(content, current_user.__oid__, post_oid)
        comment_oid = current_app.sirope.save(comment)
        
        # Agregar comentario al post
        post.add_comment(comment_oid)
        current_app.sirope.save(post)
        
        return jsonify({
            'success': True,
            'message': 'Comentario agregado exitosamente',
            'comment_count': post.get_comments_count()
        })
        
    except Exception as e:
        print(f"Error agregando comentario: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/comment/<comment_id>/like', methods=['POST'])
@login_required
def toggle_like_comment(comment_id):
    """Dar o quitar like a un comentario"""
    try:
        comment_oid = sirope.OID.from_text(comment_id)
        comment = current_app.sirope.load(comment_oid)
        
        if not comment:
            return jsonify({'success': False, 'message': 'Comentario no encontrado'})
        
        user_oid = current_user.__oid__
        
        # Toggle like
        if comment.has_liked(user_oid):
            comment.remove_like(user_oid)
            liked = False
            message = 'Like removido'
        else:
            comment.add_like(user_oid)
            liked = True
            message = 'Like agregado'
        
        current_app.sirope.save(comment)
        
        return jsonify({
            'success': True,
            'message': message,
            'liked': liked,
            'like_count': comment.like_count
        })
        
    except Exception as e:
        print(f"Error con like del comentario: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})