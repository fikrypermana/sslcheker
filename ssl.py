

from odoo import models, api, fields # Mandatory
import ssl
import datetime
import socket
import requests
import time


class Ssl(models.Model):
    _name = 'domain.ssl' # name_of_module.name_of_class 
    _description = 'Domain ssl' # Some note of table
    _rec_name = 'domain'
    _check_company_auto = True

    company_id = fields.Many2one(comodel_name='res.company', required=True, default=lambda self : self.env.company.id)

    

    # Header
   
    vendor=fields.Selection([
         ('diperpanjang', 'LetsEncrypt'),
        ('akan', 'Pusat SSL'),
       ])
   
    # Isi dengan API key bot Telegram Anda
    #bot_token = "6050046731:AAHayiYdspL9o3lKPZOL5kd57dry1prSVV0"


    # Isi dengan chat ID Anda
    #chat_id = "1358728485"

    # Isi dengan domain yang ingin diperiksa
    domain = fields.Char()

    # Fungsi untuk memeriksa SSL
    @api.model
    def check_ssl_expiry(self,domain):
        context = ssl.create_default_context()
        conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)
        conn.settimeout(3.0)
        try:
            conn.connect((domain,443))
            cert = conn.getpeercert()
            not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_left = (not_after - datetime.datetime.utcnow()).days
            time.sleep(60)
            return days_left, not_after
        except Exception as e:
            return None, None
        
        

    # Fungsi untuk mengirim notifikasi ke Telegram
    def send_telegram_notification(self):
        domain = self.env[self._name].search([])
                
        for record in domain :
            domain = record.domain
            bot_info = self.env['domain.bot'].search([('aktif', '=', True)], limit=1)  
            r = requests.get(f'https://{record.domain}')
            try:
                
                days_left, not_after = self.check_ssl_expiry(domain)
                if days_left is not None and days_left <= 30:
                    r = requests.get(f'https://{record.domain}')
                    print(r, 'r')
                    print(record.domain, 'domain')
                    message = f" !! 𝑷𝑬𝑹𝑰𝑵𝑮𝑨𝑻𝑨𝑵 !! SSL untuk domain {record.domain} akan kadaluarsa dalam 30 hari"\
                        f"\ncc @krisna"\
                        f"\ncc @ariefalrasyid" 
                    url = "https://api.telegram.org/bot" + str(bot_info.botID) +"/sendMessage?text=" + str(message) + "&chat_id=" + str(bot_info.chatID)
                    respone =requests.get(url)
            

                   
                        
                    print(respone)
                    
                    # Cetak informasi SSL
                    if not_after is not None:
                        print(f"Informasi SSL untuk domain {domain}:")
                        print(f"Sisa Hari: {days_left} hari")
                        print(f"Kadaluarsa Pada: {not_after}")
                    else:
                        print(f"Domain {domain} tidak dapat dihubungi atau tidak memiliki SSL yang valid.")

                else:
                    print(f"{record.id}SSL untuk domain {domain} akan kadaluarsa dalam {days_left} hari"\
                        f"\n\nInformasi SSL untuk domain {domain}:"\
                        f"\nSisa Hari: {days_left} hari"\
                        f"\nKadaluarsa Pada: {not_after}"
                        )
                    setData= {
                        'ssl' :record.id,
                        'days_left' : days_left,
                        'not_after' : not_after
                    }

                    self.env['domain.info'].create(setData)
            except Exception as e:
                print (f"eror : {e}")