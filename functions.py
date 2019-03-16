


def user_check(id_user, db, Memeuser):
    return db.session.query(Memeuser).filter_by(id=id_user).first()


