'''
Created on Jul 13, 2016

@author: Dayo
'''

from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax
from django.template import Context, Template
from django.utils.crypto import get_random_string

from .models import Contact, SMTPSetting
from messaging.sms_counter import SMSCounter

def _compose(template, convars):
    
    t = Template(template)
    return t.render(Context({
                            'firstname':getattr(convars,'first_name',''),
                            'lastname':getattr(convars,'last_name',''),
                            'salutation':getattr(convars,'salutation',''),
                            'email':getattr(convars,'email',''),
                            'phone':getattr(convars,'phone',''),                            
                            })
                    )


idondit = ''

@ajax
@login_required
def prepare_to_send_message(request):
    #c = "foo " + request.POST['recipients']
    #return {'result': c}
    global idondit
    
    if request.method == 'POST':
        #return {'result':request.POST.getlist('recipients',[])}
        #get contacts
        recipients = request.POST.getlist('recipients',[])
        cts = Contact.objects.filter(pk__in=recipients)
        result_dict = {}
        '''
        Return: "Email will be sent to (38) recipients"
        '''
        if request.POST.get('send_email', False):
            if request.POST.get('email_message') == '':
                return #"Email template should NOT be empty if you intend to send emails"
            #email_template = request.POST.get('email_message','')
            #I need the number of recipients who have emails accounts registered on the system
            num_of_contacts_with_emails = cts.exclude(email__exact='').count()
            
            smtp_to_use = SMTPSetting.objects.get(pk=request.POST.get('smtp_setting',''))
            
            result_dict['nocwe'] = num_of_contacts_with_emails
            result_dict['mail_server'] = '<a href="{}" target="_blank">{}</a>'.\
                                        format(smtp_to_use.get_absolute_url(),smtp_to_use.smtp_server)            
            result_dict['sample_email'] = _compose(request.POST.get('email_message'),cts.first()) #convert to img
            
            code_seg_1 = get_random_string(length=10) or None
        
        else:
            result_dict['nocwe'] = 0 #if this is 0, then it all dont matter
        '''
        Return: Total SMSs to be sent (200), Send Units Available (550)
        ''' 
        if request.POST.get('send_sms', False):
            if request.POST.get('sms_message') == '':
                return #SMS template should NOT be empty if you intend to send SMSs"
            m_count = 0
            for contact in cts:
                mc_var = SMSCounter().get_messages_count_only(_compose(request.POST.get('sms_message'), contact))
                m_count+=mc_var
            result_dict['total_sms_count'] = m_count
            code_seg_2 = get_random_string(length=10) or None
            
        else:
            result_dict['total_sms_count'] = 0
        
        result_dict['idtdt'] = idondit = "{}{}".format(code_seg_1, code_seg_2)       
        return {'result':result_dict}
    

@ajax
@login_required
def send_message(request):
    
    global idondit
    
    if request.method == 'POST':
        if request.POST.get('idtdt') == idondit:
            return {'result':'good'}
        '''
        recipients = request.POST.getlist('recipients',[])
        cts = Contact.objects.filter(pk__in=recipients)

        if request.POST.get('send_email', False):
            if request.POST.get('email_message') == '':
                return
        
        else:
            pass

        if request.POST.get('send_sms', False):
            if request.POST.get('sms_message') == '':
                return #SMS template should NOT be empty if you intend to send SMSs"
            
        else:
            pass
                
        return'''