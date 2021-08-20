# import requests
import os
from urllib.parse import urlparse

def find_osskey(domain):
    key_name = ['accessKeyId', 'accessKeySecret', 'accesskeyid', 'accesskeysecret','TmpSecretId','TmpSecretKey','secretAccessKey',
                'AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY']
    file_name = f'./js/{urlparse(domain).netloc}'
    for root, ds, fs in os.walk(file_name):
        for f in fs:
            if f.endswith('.js'):
                fullname = os.path.join(root, f)
                # yield fullname
                with open(fullname, 'r', encoding='utf-8')  as f:
                    lines = f.readlines()
                    for lines in lines:
                        for key in key_name:

                            if key in lines:
                                print(lines)


if __name__ == '__main__':
    find_osskey('admin.x.com')
