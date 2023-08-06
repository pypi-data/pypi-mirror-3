class DBManager(object) :
    """Manage database connection to store components and analyses into database. Subclasses must implement all functions"""
    
    def authenticate(self, username, password) :
        """Authenticate the user in order to know if registration of component or analysis is possible."""
        raise Exception("Your custom manager must inherits from DBManager and overload authenticate function.")
    
    def list_users(self) :
        """Display list of users stored into database."""
        raise Exception("Your custom manager must inherits from DBManager and overload list_users function.")
    
    def list_components(self, author=None) :
        """Display list of components stored into database."""
        raise Exception("Your custom manager must inherits from DBManager and overload list_components function.")
    
    def list_analyses(self, author=None, project=None) :
        """Display list of analyses stored into database."""
        raise Exception("Your custom manager must inherits from DBManager and overload list_analyses function.")
    
    def list_projects(self, author=None, project=None) :
        """Display list of projects stored into database."""
        raise Exception("Your custom manager must inherits from DBManager and overload list_projects function.")

    def component_description(self, component) :
        """Display description of component stored into database."""
        raise Exception("Your custom manager must inherits from DBManager and overload component_description function.")
    
    def analysis_description(self, analysis) :
        """Display description of analysis stored into database."""
        raise Exception("Your custom manager must inherits from DBManager and overload analysis_description function.")
    
    def get_analysis(self, analysis) :
        """Add to the analysis instance fields that are coming from an existing analysis."""
        raise Exception("Your custom manager must inherits from DBManager and overload get_analysis function.")
    
    def create_project(self, project, path, author, description, shared_with=None) :
        """Create a new project into database."""
        raise Exception("Your custom manager must inherits from DBManager and overload create_project function.")
    
    def share_project(self, project):
        """Create a new project into database."""
        raise Exception("Your custom manager must inherits from DBManager and overload create_project function.")

    def avoid_replication(self, destination_analysis, destination_pin, source_analysis, source_pin) :
        """Avoid replication of existing analysis outputs. Must be overloaded in subclasses."""
        raise Exception("Your custom manager must inherits from DBManager and overload avoid_replication function.")
    
    def register(self, component, auto=False) :
        """Register a Component into a database. Must be overloaded in subclasses."""
        raise Exception("Your custom manager must inherits from DBManager and overload register function.")
    
    def store(self, component, analysis, author=None, intermediates=[], comments=None) :
        """Register an Analysis into a database. Must be overloaded in subclasses."""
        raise Exception("Your custom manager must inherits from DBManager and overload store function.")
