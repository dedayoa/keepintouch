'''
Created on Aug 30, 2016

@author: Dayo
'''


class TemplateForIssueFeedbackMessages(object):
    
    
    def template_to_user(self):
        t = '''
        Dear {{fullname}},
        <p>Thank you for the feedback. <strong>We really appreciate it</strong>.</p>
        <p>We will look into the issue immediately and revert</p>
        
        <p>Need Immediate Support, contact us via<br />
        Phone: +2348028443225<br />
        Email: support@intouchng.com<br /></p>
        
        Regards<br />
        In.Touch Support<br />
        
        '''
        return t        
        
    def template_to_dev_chan(self):
        t = '''
        Dear Support
        <p>You have received a new submission from {{fullname}}<{{email}}>.</p>
        See Detail Below:
        <p><strong>Title</strong>: {{title}}</p>
        <strong>Detail</strong>:
        <p>{{detail}}</p>
        
        Attachment can be found here <a href="{{screenshot_link}}">{{screenshot_link}}</a>
        <p>Over & Out...</p>
        '''
        
        return t
    
class TemplateForPhoneEmailVerification(object):
    
    def template_email(self):
        t = '''
        Dear {{fullname}}
        <p>Your Email Verification code is</p>
        <p><strong>{{email_verification_code}}</strong></p>
        Copy and paste in the "Verification Code" field on In.Touch.
        <p>Need Immediate Support, contact us via<br />
        Phone: +2348028443225<br />
        Email: support@intouchng.com<br /></p>
        
        Regards<br />
        In.Touch Support<br />'''
        
        return t
        
    def template_sms(self):
        t = '''
        Dear {{fullname}}
        Your Phone Verification code is {{phone_verification_code}}.
        
        In.Touch        
        '''
        
        return t