from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required

bp = Blueprint('actions', __name__)

@bp.route('/like/<int:user_id>', methods=['POST'])
@login_required
def like_user(user_id):
    # 1) 자기 자신 좋아요 방지
    if user_id == current_user.id:
        return jsonify(error="불가능한 요청"), 400

    # 2) 이미 좋아요 눌렀는지 확인
    exists = Like.query.filter_by(liker_id=current_user.id, liked_id=user_id).first()
    if exists:
        return jsonify(message="이미 좋아요 함"), 200

    # 3) 좋아요 추가
    new_like = Like(liker_id=current_user.id, liked_id=user_id)
    db.session.add(new_like)

    # 4) 상대가 나를 이미 좋아요 했는지 확인 → Match 생성
    reciprocal = Like.query.filter_by(liker_id=user_id, liked_id=current_user.id).first()
    if reciprocal:
        # 양방향 매칭 생성 (user_a < user_b 정렬해주면 중복 방지)
        a, b = sorted([current_user.id, user_id])
        match = Match(user_a=a, user_b=b)
        db.session.add(match)

    # 5) (선택) 프로필 like_count 동기화
    User.query.filter_by(id=user_id).update({'like_count': User.like_count + 1})

    db.session.commit()
    return jsonify(success=True), 201
