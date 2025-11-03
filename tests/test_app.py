import os
import tempfile
import pytest
from app import app, db, Category, Expense

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # create sample category
            c = Category(name='Test', budget=100)
            db.session.add(c)
            db.session.commit()
        yield client

    os.close(db_fd)
    try:
        os.remove(db_path)
    except OSError:
        pass


def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'SpendSmart' in rv.data


def test_add_and_view(client):
    # add expense
    with app.app_context():
        c = Category.query.filter_by(name='Test').first()
        assert c is not None
        cid = c.id
    rv = client.post('/add', data={'description':'unit test','amount':'12.50','category':str(cid)}, follow_redirects=True)
    assert rv.status_code == 200
    assert b'Expense added' in rv.data
    rv = client.get('/view')
    assert b'unit test' in rv.data
