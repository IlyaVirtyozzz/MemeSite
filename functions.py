def user_check(id_user, db, Memeuser):
    user = db.session.query(Memeuser).filter_by(id=id_user).first()
    return user
