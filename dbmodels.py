import logging

from flask.ext.sqlalchemy import SQLAlchemy
# no app object passed! Instead we use use db.init_app in the factory.

db = SQLAlchemy()

fh = logging.FileHandler('dbmodels.log')
fh.setLevel(logging.DEBUG)
logger = logging.getLogger('db.engine')
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)


class Manifest(db.Model):
    __tablename__ = 'manifests'
    id = db.Column('id', db.Text, nullable=False, primary_key=True)
    source_type = db.Column('source_type', db.Text, nullable=False,
                            primary_key=True)
    source_url = db.Column('source_url', db.Text, nullable=False,
                           primary_key=True)
    label = db.Column('label', db.Text, nullable=False)
    # db.Column('manifest', postgresql.JSON(), nullable=False)
    manifest = db.Column('manifest', db.Text, nullable=False)
    manifest_category = db.Column('manifest_category', db.Text, nullable=True)
    images = db.relationship("Image", backref="manifest")

    def __repr__(self):
        return "<Manifest(id='%s', source_type='%s', " \
               "source_url='%s', label='%s)>" % (
               self.id, self.source_type, self.source_url, self.label)


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column('id', db.Integer, primary_key=True)
    identifier = db.Column('identifier', db.Text, nullable=False, index=True)
    manifest_id = db.Column('manifest_id', db.Text)
    source_type = db.Column('source_type', db.Text)
    source_url = db.Column('source_url', db.Text)
    annotations = db.Column('annotations', db.Text)
    status = db.Column('status', db.String(12))
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['manifest_id', 'source_type', 'source_url'],
            ['manifests.id', 'manifests.source_type', 'manifests.source_url'],
            onupdate="CASCADE", ondelete="CASCADE"
        ),
    )
    # permissions = db.relationship("UserPermission")

    def __repr__(self):
        return "<Image(id='%s', identifier='%s', " \
               "manifest_id='%s', status='%s)>" % (self.id, self.identifier,
                                                   self.manifest_id,
                                                   self.status)


# class UserPermission(db.Model):
#     __tablename__ = 'user_permissions'
#     permission_id = db.Column('permission_id', db.Integer, primary_key=True)
#     user_id = db.Column('user_id', db.Integer, nullable=False, index=True)
#     asset_id = db.Column('asset_id',
#                          db.Integer,
#                          db.ForeignKey('images.id',
#                                        onupdate="CASCADE",
#                                        ondelete="CASCADE"),
#                          nullable=False)
