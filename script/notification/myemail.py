import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logs import *

class Myemail(object):
    """
    """

    def __init__(self, config, packpub_info, upload_info):
        self.__config = config
        self.__packpub_info = packpub_info
        self.__upload_info = upload_info

    def __prepare_message(self):
        """
        """
        #log_json(self.__packpub_info)
        #log_json(self.__upload_info)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "[packtpub-crawler]"
        msg['From'] = self.__config.get('email', 'email.from')
        msg['To'] = self.__config.get('email', 'email.to')

        text = "Enjoy your daily FREE eBook!"
        html = """\
        <html>
          <head></head>
          <body>
            <div>{title}</div>
            <div><img src="{image}" alt="cover" /></div>
            <div>{description}</div>
            """.format(title=self.__packpub_info['title'].encode('utf-8'),
                        image=self.__packpub_info['url_image'].encode('utf-8'),
                        description=self.__packpub_info['description'].encode('utf-8'))

        if self.__upload_info is not None:
            html += "<ul>"
            for detail in self.__upload_info['details']:
                html += """<li>{mime_type} - <a href="{download_url}">{name}</a></li>"""\
                    .format(mime_type=detail['mime_type'], download_url=detail['download_url'], name=detail['name'])
            html += "</ul>"

        html += """\
            <div>Powered by <a href="https://github.com/niqdev/packtpub-crawler">packtpub-crawler</a></div>
            <div>FREE eBook every day from <a href="https://www.packtpub.com/packt/offers/free-learning">www.packtpub.com</a></div>
          </body>
        </html>
        """

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        return msg

    def __prepare_error_message(self, exception, source):
        """
        """
        #log_json(self.__packpub_info)
        #log_json(self.__upload_info)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "[packtpub-crawler]"
        msg['From'] = self.__config.get('email', 'email.from')
        msg['To'] = self.__config.get('email', 'email.to')

        text = "Error downloading today's ebook [{source}]".format(source=source)
        html = """\
        <html>
          <head></head>
          <body>
            <div>{title}</div>
            <div>Download manually: <a href="{url}">{url}</a></div>
            <div>{description}</div>
            """.format(title=text,
                       description=repr(exception),
                       url=self.__packpub_info['landingPageUrl'])

        html += """\
            <div>Powered by <a href="https://github.com/niqdev/packtpub-crawler">packtpub-crawler</a></div>
          </body>
        </html>
        """

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        return msg

    def send(self):
        print self.__config.get('email', 'email.host')
        print self.__config.get('email', 'email.port')
        server = smtplib.SMTP(self.__config.get('email', 'email.host'), self.__config.get('email', 'email.port'))
        server.starttls()
        server.login(self.__config.get('email', 'email.username'), self.__config.get('email', 'email.password'))

        message = self.__prepare_message()
        receivers = message['To'].split(",")
        server.sendmail(message['From'], receivers, message.as_string())
        server.quit()

        log_success('[+] notified to: {0}'.format(receivers))

    def sendError(self, exception, source):
        server = smtplib.SMTP(self.__config.get('email', 'email.host'), self.__config.get('email', 'email.port'))
        server.starttls()
        server.login(self.__config.get('email', 'email.username'), self.__config.get('email', 'email.password'))

        message = self.__prepare_error_message(exception, source)
        receivers = message['To'].split(",")
        server.sendmail(message['From'], receivers, message.as_string())
        server.quit()

        log_success('[+] error notifikation sent to: {0}'.format(receivers))
