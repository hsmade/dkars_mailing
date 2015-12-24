import smtplib
import os
import logging
logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger('mailing')

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
from gluon.scheduler import Scheduler
from datetime import datetime
scheduler = Scheduler(db)

def send_mailing(mailing):
    mailing_record = db(db.mailings.id == mailing).select().first()
    logger.debug('scheduler called with: mailing={}'.format(mailing_record))
    months_dutch = ( 'januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december') 
    logs = []
    date = datetime(mailing_record.f_year, mailing_record.f_month, 1)
    newsletter = '{}{}'.format(date.year, date.month)
    languages = [ 'english', 'dutch' ]
    Subject = { 'english': 'DKARS Magazine #{issue}, {month} {year}'.format(
                  issue=mailing_record.f_issue_number,
                  month=date.strftime("%B"),
                  year=date.year
                  ),
                'dutch': 'DKARS Magazine #{issue}, {month} {year}'.format(
                  issue=mailing_record.f_issue_number,
                  month=months_dutch[date.month-1],
                  year=date.year
                  ),
               }
    
    From = 'DKARS-news-{newsletter}@dkars.nl'.format(newsletter=newsletter)
    s = smtplib.SMTP('localhost')
    link='http://downloads.dkars.nl/DKARS%20Magazine%20{}.pdf'.format(newsletter)
    
    for language in languages:
        text = getattr(mailing_record, 'f_text_{}'.format(language))
        index=1
        if mailing_record.f_test_mode:
            addresses = [mailing_record.f_test_address]
        else:
            addresses=[row.f_email for row in db(db.addresses.f_taal == language).select()]
        for address in addresses:
            html = '<html><head></head><body><p>'+text.replace('\n','<br>\n')+'</p></body></html>'
            msg = MIMEMultipart('alternative')
            msg['Subject'] = Subject[language]
            msg['From'] = From
            msg['To'] = address
            part1 = MIMEText(Template(text).substitute(link=link+str(index)), 'plain')
            part2 = MIMEText(Template(html).substitute(link='<a href="{link}">Link</a>'.format(link=link,)), 'html')
            msg.attach(part1)
            msg.attach(part2)
            try:
                s.sendmail(From, address, msg.as_string())
                log = 'to: {to} {index} subject:{subject}'.format(index=index,subject=Subject[language], to=address)
                logger.info(log)
                logs.append(log)
            except Exception as e:
                log = 'failed: from: {From}, to: {to} err:{e}'.format(e=str(e),From=From, to=address)
                logger.error(log)
                logs.append(log)
            index += 1
    s.quit()
    db.logs.insert(f_issue_number=newsletter, f_log='\n'.join(logs))
    db.commit()
