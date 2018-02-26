from app.project import db
from app.project.models import User
from datetime import datetime


db.drop_all()
db.create_all()

admin = User('user@gmail.com', 'testpassword')
admin.registration_date = datetime.now()
admin.email_confirmed = True
admin.role = 'admin'
db.session.add(admin)
db.session.commit()

