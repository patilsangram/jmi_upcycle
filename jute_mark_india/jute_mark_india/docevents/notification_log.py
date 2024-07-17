import frappe
import requests
import json
import re
from frappe import enqueue

@frappe.whitelist()
def send_push_notification(doc, method=None):
    '''
        method sends push notifications to user devices
        args:
            doc: document object of notification log
    '''
    push_notifications_enabled = frappe.db.get_single_value('Android App Settings', 'enable_push_notifications')
    if push_notifications_enabled:
        if doc.for_user:
            device_ids = get_devive_id(doc.for_user)
            for device_id in device_ids:
                process_notification(device_id=device_id, notification=doc)

@frappe.whitelist()
def get_devive_id(user_id):
    '''
        method gets the device tokens of user
        args:
            doc: document object of notification log
    '''
    user_device_ids = frappe.get_all("User Device", filters= {"user": user_id}, fields=["device_id"])
    return user_device_ids

@frappe.whitelist()
def process_notification(device_id, notification):
    '''
        method sends the api call to fcm server to send a notification to a user device
        args:
            device_id: device token of user
            notification: document object of notification log
    '''
    message = notification.email_content
    title = notification.subject
    if message:
        message = convert_message(message)
    if title:
        title = convert_message(title)

    url = "https://fcm.googleapis.com/fcm/send"
    body = {
        "to": device_id.device_id,
        "notification": {
            "body": message,
            "title": title
        },
        "data": {
            "doctype": notification.document_type,
            "docname": notification.document_name
        }
    }

    server_key = 'key = ' + frappe.db.get_single_value('Android App Settings', 'fcm_server_key')
    req = requests.post(url=url, data=json.dumps(body), headers={"Authorization": server_key, "Content-Type": "application/json", "Accept": "application/json"})

@frappe.whitelist()
def convert_message(message):
    '''
        method removes html elements from string
        args:
            message: string to be converted
    '''
    CLEANR = re.compile('<.*?>')
    cleanmessage = re.sub(CLEANR, "",message)
    return cleanmessage
