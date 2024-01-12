# from flask_migrate import Migrate, upgrade
# from flask_sqlalchemy import SQLAlchemy
# from flask import Flask



# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///user.db"
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

# def perform_migration():
#     with app.app_context():
#         migrate.init_app(app, db)
#         # migrate.migrate()
#         # migrate.create_all()
#         # upgrade()

# perform_migration()

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)
#     profile = db.relationship('Profile', back_populates='user')

# class Profile(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     address = db.Column(db.String)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     user = db.relationship('User', back_populates='profile')
    
# with app.app_context():
#     db.create_all()


# new_user = User(
#     name = "Terna"
# )
# new_profile = Profile(
#     address = "234 Sunny Ville",

# )
# with app.app_context():
#     db.session.add(new_user)
#     db.session.add(new_profile)
#     db.session.commit()

# with app.app_context():
#     users = User.query.all()
#     for user in users:
#         profile = user.profile
#         for add in profile:
#             print(add.address)
#         print(profile)

