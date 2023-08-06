from continuous_services.service import Service

from apps.messaging.tasks import send_email

class EmailService(Service):
    
    def build_complete(self):
        previous_result = self.previous_build["result"] if self.previous_build else None
        
        is_broken_fixed = (self.build["result"] != previous_result)
        is_failure = (self.build["result"] in ("F", "D"))
        is_success = (self.build["result"] == "S")
        
            
        if is_broken_fixed and self.data["email_broken_fixed"]:
            send = True
        elif is_failure and self.data["email_every_failure"]:
            send = True
        elif is_success and self.data["email_every_success"]:
            send = True
        else:
            send = False
        
        if send:
            send_email.delay(
                template_name="build_happy" if is_success else "build_sad",
                from_email=None,
                recipient_list=[self.data["email_address"]],
                context={
                    "project_name": self.project["name"], # needed in the subject
                    "project": self.project,
                    "build": self,
                    "branch": self.branch,
                    "unsubscribe": self.get_service_url(),
                },
            )
            
