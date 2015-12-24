import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
from gluon.scheduler import Scheduler
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('mailing')

scheduler = Scheduler(db)


def send_mailing(mailing):
    mailing_record = db(db.mailings.id == mailing).select().first()
    logger.debug('scheduler called with: mailing={}'.format(mailing_record))
    months_dutch = (
        'januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
        'augustus', 'september', 'oktober', 'november', 'december')
    date = datetime(mailing_record.f_year, mailing_record.f_month, 1)
    newsletter = '{}{}'.format(date.year, date.month)
    subject = {
        'english': 'DKARS Magazine #{issue}, {month} {year}'.format(
                issue=mailing_record.f_issue_number,
                month=date.strftime("%B"),
                year=date.year
        ),
        'dutch': 'DKARS Magazine #{issue}, {month} {year}'.format(
                issue=mailing_record.f_issue_number,
                month=months_dutch[date.month - 1],
                year=date.year
        ),
    }

    from_address = 'DKARS-news-{newsletter}@dkars.nl'.format(
            newsletter=newsletter)
    link = 'http://downloads.dkars.nl/DKARS%20Magazine%20{}.pdf'.format(
            newsletter)

    send_mail(
        mailing_record=mailing_record,
        subject=subject,
        from_address=from_address,
        link=link,
        newsletter=newsletter)


def send_custom_mailing(mailing):
    mailing_record = db(db.custom_mailings.id == mailing).select().first()
    logger.debug('scheduler called with: mailing={}'.format(mailing_record))
    subject = {'english': mailing_record.f_subject_english,
               'dutch': mailing_record.f_subject_dutch,
               }

    from_address = 'DKARS-mailing@dkars.nl'

    send_mail(
        mailing_record=mailing_record,
        subject=subject,
        from_address=from_address)


def send_mail(mailing_record, subject,
              from_address, link='', newsletter=''):
    logs = []
    languages = ['english', 'dutch']
    s = smtplib.SMTP('localhost')
    for language in languages:
        text = getattr(mailing_record, 'f_text_{}'.format(language))
        index = 1
        if mailing_record.f_test_mode:
            addresses = [mailing_record.f_test_address]
        else:
            addresses = [row.f_email for row in
                         db(db.addresses.f_taal == language).select()]
        for address in addresses:
            html = '<html><head></head><body><p>' + \
                   text.replace('\n', '<br>\n') + '</p></body></html>'
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject[language]
            msg['From'] = from_address
            msg['To'] = address
            if link:
                part1 = MIMEText(
                        Template(text).substitute(link=link + str(index)),
                        'plain')
                part2 = MIMEText(Template(html).substitute(
                        link='<a href="{link}">Link</a>'.format(link=link, )),
                        'html')
            else:
                part1 = MIMEText(text, 'plain')
                part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            try:
                s.sendmail(from_address, address, msg.as_string())
                log = 'to: {to} {index} subject:{subject}'.format(
                        index=index,
                        subject=subject[language],
                        to=address)
                logger.info(log)
                logs.append(log)
            except Exception as e:
                log = 'failed: from: {From}, to: {to} err:{e}'.format(
                        e=str(e),
                        From=from_address,
                        to=address)
                logger.error(log)
                logs.append(log)
            index += 1
    s.quit()
    if not link:
        newsletter = str(datetime.now())
    db.logs.insert(f_issue_number=newsletter, f_log='\n'.join(logs))
    db.commit()
