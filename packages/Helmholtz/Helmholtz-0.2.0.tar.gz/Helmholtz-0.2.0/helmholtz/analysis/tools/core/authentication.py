class Authentication(object) :
    """Store user authentication and database manager."""
    
    def __init__(self) :
        self.authenticated = False
        self.username = None
        self.firstname = None
        self.lastname = None
        self.manager = None
    
    def authenticate(self, username, password, manager) :
        self.authenticated, self.username, self.firstname, self.lastname = manager.authenticate(username, password)
        self.manager = manager

#create a global variable accessible from the DBManager 
#in order to test if the user is known by the database system
authentication = Authentication()

def authenticate(username, password, manager) :
    authentication.authenticate(username, password, manager)
