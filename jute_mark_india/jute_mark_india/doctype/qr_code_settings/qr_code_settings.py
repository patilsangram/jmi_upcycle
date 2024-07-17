# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from Crypto.Cipher import AES

class QRCodeSettings(Document):
	def validate(self):
		if self.password_for_encryption:
			if len(self.password_for_encryption) != 16:
				frappe.throw("Password should have <b>16 digits</b> for <b>128 Bit encryption</b>")
		if not self.qr_code_generation_constant:
			frappe.throw("QR Code Generation Constant is required in between 1-10.")
		else:
			if ((self.qr_code_generation_constant>10) or (self.qr_code_generation_constant<1)):
				frappe.throw("QR Code Generation Constant is required in between 1-10.")

def get_encryption_key():
	return frappe.utils.password.get_decrypted_password(
		"QR Code Settings", "QR Code Settings", "password_for_encryption"
	)

# def encrypt_msg(plaintext):
# 	key = get_encryption_key().encode("utf-8")
# 	plaintext = plaintext.encode("utf-8")

# 	# # Pad the plaintext if necessary (AES requires plaintext to be a multiple of 16 bytes)
# 	# while len(plaintext) % 16 != 0:
# 	# 	plaintext += b'\x00'

# 	cipher = AES.new(key, AES.MODE_ECB)
# 	decipher = AES.new(key, AES.MODE_ECB)

# 	msg = cipher.encrypt(plaintext)
# 	msg_in_hex = msg.hex()
# 	decrypted_msg = decipher.decrypt(msg)
# 	return msg_in_hex.upper()

def encrypt_msg(plaintext):
	key = get_encryption_key().encode("utf-8")
	plaintext = plaintext.encode("utf-8")
	cipher = AES.new(key, AES.MODE_ECB)

	while len(plaintext) % 16 != 0:
		plaintext += b'\0'
		
	ciphertext = cipher.encrypt(plaintext)
	msg_in_hex = ciphertext.hex()
	return msg_in_hex.upper()
