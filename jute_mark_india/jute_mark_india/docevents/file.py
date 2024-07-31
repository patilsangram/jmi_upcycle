import frappe
import os


@frappe.whitelist()
def save_file_on_filesystem(doc):
    """Custom file save method to save file with new file name generated using hashvalue.
    Copied from frappe.core.doctype.file"""
    try:
        file_name = doc.file_name
        file_ext = file_name.split(".")[-1]
        new_file_name = frappe.generate_hash(length=10) + "." + file_ext
        doc.file_name = new_file_name
        if doc.is_private:
            doc.file_url = f"/private/files/{doc.file_name}"
        else:
            doc.file_url = f"/files/{doc.file_name}"
        fpath = doc.write_file()

        return {"file_name": os.path.basename(fpath), "file_url": doc.file_url}
    except Exception as e:
        message = frappe.get_traceback()
        frappe.log_error(message=message, title="JMI: save_file_on_filesystem")

def write_file(doc):
    """write file to disk with a random name (to compare)"""
    if doc.is_remote_file:
        return

    file_path = doc.get_full_path()

    if isinstance(doc._content, str):
        doc._content = doc._content.encode()

    with open(file_path, "wb+") as f:
        f.write(doc._content)
        os.fsync(f.fileno())

    frappe.local.rollback_observers.append(doc)

    return file_path