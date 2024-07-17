import frappe
from frappe.email.doctype.notification.notification import get_context

notifications = {
    'Application Submitted Notification' : {
        'email_content': 'Your JMI application number {{ doc.name }} is submitted successfully.',
        'subject': 'Your application is submitted successfully.'
    },
    'Incomplete Application Notification': {
        'email_content': 'Your JMI application number {{ doc.name }} is incomplete. Please complete the application before today.',
        'subject': 'Your application is incomplete.'
    },
    'Sample Submission Notification': {
        'email_content': 'Please submit the samples for JMI application at nearest TC laboratary.(Sample dimention with requirement)',
        'subject': 'Please submit the samples at nearest TC laboratary.'
    },
    'VO Allotment Notification': {
        'email_content': 'JMI application number {{ doc.application_no }}, is alloted to Shri. {{ doc.assigned_username }} for onsite verification.',
        'subject': 'Your application is alloted to Shri. {{ doc.assigned_username }} for onsite verification.'
    },
    'Site Schedule Confirmation Notification': {
        'email_content': 'JMI application number {{ doc.application_no }} is scheduled for onsite verification on {{ doc.visit_planed_on }}. Kindly make it convenient to be available with relevant documents/records.',
        'subject': 'Your application number {{ doc.application_no }} is scheduled for onsite verification on {{ doc.visit_planed_on }}.'
    },
    'Site Re-Schedule Confirmation Notification': {
        'email_content': 'Your application number {{ doc.application_no }}, is reschduled on {{ doc.visit_planed_on }} for onsite verification.',
        'subject': 'Your application number {{ doc.application_no }}, is reschduled on {{ doc.visit_planed_on }} for onsite verification.'
    },
    'Verification Completed Notification': {
        'email_content': 'On-site-verification for JMI registration is successfully completed on {{ doc.visit_planed_on }}, you will soon receive the registration and label issuance letters.',
        'subject': 'On-site-verification conducted on {{ doc.visit_planed_on }} is completed.'
    },
    'Registration Completed Notification': {
        'email_content': 'Reference to your JMI application number {{ doc.name }}, Registration is successfully completed. Your registration number is {{ doc.registration_number }}.',
        'subject': 'Registration is successfully completed. Your registration number is {{ doc.registration_number }}.'
    },
    'Renewal Reminder Notification': {
        'email_content': 'Your JMI registration is due for renewal on {{ doc.next_renewal_date }}. Plase do the renewal before {{ doc.next_renewal_date }}.',
        'subject': 'Your JMI registration is due for renewal on {{ doc.next_renewal_date }}. Plase do the renewal before {{ doc.next_renewal_date }}.'
    },
    'Renewal Complete Notification': {
        'email_content': 'Your JMI registration number {{ doc.registration_number }} is renewed successfully on {{ doc.renewed_on }}. Valid upto {{ doc.next_renewal_date }}.',
        'subject': 'Your registration is renewed successfully.'
    },
    'Label Enhancement Notification': {
        'email_content': 'Reference to your JMI registration number {{ doc.app__reg_number }}. Your request for label exceeds the entitlement, kindly make request for label enhancement.',
        'subject': 'Your request for label exceeds the entitlement.'
    }
}

def send_notification(doctype, docname, template_name, user_id):
    if not notifications.get(template_name):
        return 0
    if not frappe.db.exists(doctype, docname):
        return 0
    if not frappe.db.exists('User', user_id):
        return 0
    doc = frappe.get_doc(doctype, docname)
    context = get_context(doc)
    message_template = notifications.get(template_name)
    email_content = frappe.render_template(message_template.get('email_content'), context)
    subject = frappe.render_template(message_template.get('subject'), context)
    notification_send = False
    if frappe.db.exists('Notification Log', { 'document_type':doctype, 'document_name':docname, 'for_user':user_id }):
        last_notification_log = frappe.get_last_doc('Notification Log', filters = { 'document_type':doctype, 'document_name':docname, 'for_user':user_id })
        if last_notification_log.subject == subject:
            notification_send = True
    if not notification_send:
        notification_log = frappe.new_doc('Notification Log')
        notification_log.type = 'Assignment'
        notification_log.document_type = doctype
        notification_log.document_name = docname
        notification_log.email_content = email_content
        notification_log.subject = subject
        notification_log.for_user = user_id
        notification_log.save(ignore_permissions=True)
        frappe.db.commit()
