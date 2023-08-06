import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from ..models import tables
from ..models import setup_database

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def main(argv=sys.argv):
    import getpass
    import transaction
    from ..models.user import UserModel
    
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    
    # create all tables
    settings = setup_database({}, **settings)
    engine = settings['write_engine']
    tables.DeclarativeBase.metadata.create_all(engine)
    
    session = settings['write_session_maker']()
    model = UserModel(session)
    
    with transaction.manager:
        admin = model.get_user_by_name('admin')
        if admin is None:
            print 'Create admin account'
            
            email = raw_input('Email:')
            
            password = getpass.getpass('Password:')
            confirm = getpass.getpass('Confirm:')
            if password != confirm:
                print 'Password not match'
                return
        
            user_id = model.create_user(
                user_name='admin',
                display_name='Administrator',
                email=email,
                password=password
            )
            admin = model.get_user_by_id(user_id)
            session.flush()
            print 'Created admin, user_id=%s' % admin.user_id
            
        permission = session.query(tables.Permission) \
            .filter_by(permission_name='admin') \
            .first()
        if permission is None:
            print 'Create admin permission ...'
            permission = tables.Permission(
                permission_name='admin',
                description='Administrate',
            )
            session.add(permission)
            
        group = session.query(tables.Group) \
            .filter_by(group_name='admin') \
            .first()
        if group is None:
            print 'Create admin group ...'
            session.flush()
            group = tables.Group(
                group_name='admin',
                display_name='Administrators',
                created=tables.now_func()
            )
            session.add(group)
            
        group_permission = session.query(tables.group_permission_table) \
            .filter_by(group_id=group.group_id) \
            .filter_by(permission_id=permission.permission_id) \
            .first()
        if group_permission is None:
            print 'Add admin permission to admin group'
            session.flush()
            session.execute(tables.group_permission_table.insert(), dict(
                group_id=group.group_id,
                permission_id=permission.permission_id,
            ))
            
        session.flush()
        user_group = session.query(tables.user_group_table) \
            .filter_by(user_id=admin.user_id) \
            .filter_by(group_id=group.group_id) \
            .first()
        if user_group is None:
            print 'Add admin to admin group'
            session.execute(tables.user_group_table.insert(), dict(
                user_id=admin.user_id,
                group_id=group.group_id,
            ))