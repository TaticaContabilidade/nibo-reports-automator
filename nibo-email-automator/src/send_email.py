import smtplib
import os
from logs.logger.logging_sendemail import Logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class SendEmail(Logging):
  def __init__(self): 
    super().__init__()

  def send_email(self, file_path: list, enterprise: str) -> None:
    try:
      j: int = 0 
      email: str = os.environ["EMAIL_GMAIL"]
      password: str = os.environ["GMAIL_APP_PASS"]
      server_email = smtplib.SMTP('smtp.gmail.com', 587)
    
      server_email.starttls()
      server_email.login(email, password)

      subject: str = f"Relatórios Semanais - {enterprise}"
      body: str = "TESTANDO..."
      from_addr:str = os.environ["SENDER_EMAIL"]
      to_addrs:str = os.environ["RECEIVER_EMAIL"]

      msg: MIMEMultipart = MIMEMultipart()
      msg["Subject"] = subject
      msg["From"] = from_addr
      msg["To"] = to_addrs 
      msg.attach(MIMEText(body, 'plain'))
      
      while j < len(file_path):
        
        with open(file_path[j], 'rb') as attachment_file:
          part = MIMEBase('application', 'octet-stream')
          part.set_payload(attachment_file.read())

        encoders.encode_base64(part)
        part.add_header(
          'Content-Disposition',
          f'attachment; filename="{os.path.basename(file_path[j])}"',
        )

        j += 1
        msg.attach(part)

      server_email.send_message(msg)
      self.logging_debug("Sucess: Email enviado com ")
      server_email.quit()

    except Exception as e:
      self.logging_error(f"Error: Error ao enviar email: {e}")

  def logging_debug(self, message) -> Logging:
    return self.logger.debug(message)

  def logging_error(self, message) -> Logging:
    return self.logger.error(message)

  def logging_info(self, message) -> Logging:
    return self.logger.info(message)

  def logging_warning(self, message) -> Logging:
    return self.logger.warning(message)