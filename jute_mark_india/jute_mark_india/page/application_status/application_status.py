import frappe
import json
from frappe.utils import flt

@frappe.whitelist()
def get_application_data(filters):
    filters = json.loads(filters)
    filter_query = ""
    if filters.get("reginal_office"):
        filter_query += " and reg.regional_office = '{}'".format(filters.get("reginal_office"))
    if filters.get("from_date"):
        filter_query += " and cast(reg.creation as date) >= '{}'".format(filters.get("from_date"))
    if filters.get("to_date"):
        filter_query += " and cast(reg.creation as date) <= '{}'".format(filters.get("to_date"))
    if filters.get("category"):
        filter_query += " and reg.category_b = '{}'".format(filters.get("category"))
    if filters.get("district"):
        filter_query += " and reg.district = '{}'".format(filters.get("district"))
    result = []
    wf_state_query = f"""
        select
            sum(case when reg.workflow_state != 'Draft' then 1 else 0 end) as applications,
            sum(case when is_paid = 1 then 1 else 0 end) as payment_made,
            sum(case when reg.workflow_state = 'Application Submitted' then 1 else 0 end) as application_submitted,
            sum(case when reg.workflow_state = 'Assigned VO' then 1 else 0 end) as allotment_to_vo,
            sum(case when reg.name like 'R-%' then 1 else 0 end) as registration,
            sum(case when rep.upload_test_report is not null then 1 else 0 end) as report_submitted,
            sum(case when os.sign is not null and (os.photograph_1 is not null or os.photograph_2 is not null)
                then 1 else 0 end) as site_verified
        from `tabJute Mark India Registration form` reg
        left join(
            select parent, upload_test_report from (select parent, upload_test_report,
            row_number() over(partition by parent order by upload_test_report) as rn
            from `tabJMI Documents`) a where rn=1
        ) rep on reg.name = rep.parent
        left join (
            select regi_no, site_verification, photograph_1, photograph_2, sign from (
                select
                    os.textile_registration_no as regi_no, os.name as site_verification,
                    ph.photograph_1, ph.photograph_2, signature_with_name as sign,
                    row_number() over(partition by os.textile_registration_no order by os.name) as rn
                from `tabOn-Site Verification Form` os
                left join `tabSite Visit Photos` ph on os.name = ph.parent
            ) a where rn=1
        ) os on reg.name = os.regi_no
        where 1=1 {filter_query}
    """
    applications_data = frappe.db.sql(wf_state_query, as_dict=True)[0]

    for status, rec_cnt in applications_data.items():
       progress_per = 0
       remaining_per = 0
       status_lower = status
       status = status.title().replace("_", " ")
       if rec_cnt:
            progress_per = flt(int(rec_cnt)/int(applications_data.get("applications")) * 100, 2)
            remaining = 100 - progress_per
            remaining_per = flt(remaining/2, 2)
       result.append({
            "application_status": status,
            "application_status_lower": status_lower,
            "record_count": int(rec_cnt or 0),
            "progress_per": progress_per,
            "remaining_per": remaining_per
        })
    return result