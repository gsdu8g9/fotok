"""
This file initialized a simple test DB with two users and one photo.
"""

from fotok import db, models

db.create_all()

root = models.User(username='root')
root.set_password('root')

test = models.User(username='test')
test.set_password('test')

test.subscriptions.append(root)

photo = models.Photo(width=640, height=480)
photo.user = root

db.session.add(root)
db.session.add(test)
db.session.add(photo)

db.session.commit()
