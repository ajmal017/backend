
from profiles import helpers as profile_helpers
from django.conf import settings
import csv


def read_csv_and_send_marketing_email():
    csv_file_name = 'webapp/fixtures/emailer-batch-fin1k.csv'

    data_reader = csv.reader(open(csv_file_name), delimiter=',', quotechar='"')

    for row in data_reader:
        try: 
            if row[0] != 'email_id' and row[0] != '':
                
                email_id = row[0]
                name = ''
                send_marketing_email(email_id,name)
        except Exception as e:
            print("error: " + str(e))
            
            
def send_marketing_email(email_id,name,domain_override=None, subject_template_name='marketing_email/marketing_email_subject.txt',
                                     email_template_name=None, use_https=False,from_email=None,
                                     request=None,html_email_template_name='marketing_email/MarketingEmailer.html', extra_email_context=None):
    
    context = {     
             'domain': settings.SITE_API_BASE_URL,
             'site_name': "Finaskus",
             'name': name,
             'protocol': 'https' if use_https else 'http',
               }
    profile_helpers.send_mail(subject_template_name, email_template_name, context, from_email, email_id,
                          html_email_template_name=html_email_template_name)
    
    return True

