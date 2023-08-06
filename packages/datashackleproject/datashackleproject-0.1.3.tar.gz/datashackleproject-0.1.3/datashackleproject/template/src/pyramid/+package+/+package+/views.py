from p2.datashackle.core import Session
from pyramid.view import view_config
from .models import Person

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    
    session = Session()
    persons = session.query(Person).all()
    
    return {'persons': persons}
