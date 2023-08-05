from django.db import models

#===============================================================================
class VisitorManager(models.Manager):
    
    #---------------------------------------------------------------------------
    def find_visitor(self, visitor_key):
        try:
            return self.get(visitor_key=visitor_key)
        except self.model.DoesNotExist:
            print("model doesn't exist")
            return None
            
    #---------------------------------------------------------------------------
    def create_from_ip(self, ip):
        from visitor.visitor_utils import create_uuid
        return self.get_or_create(visitor_key=create_uuid(ip))[0]
        
