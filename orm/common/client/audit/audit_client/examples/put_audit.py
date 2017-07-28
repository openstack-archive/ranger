"""put_audit module."""

from audit_client.api import audit

audit_server_url = "http://127.0.0.1:8776/v1/audit/transaction"
num_of_send_retries = 3
time_wait_between_retries = 1
audit.init(audit_server_url, num_of_send_retries, time_wait_between_retries)
audit.audit(1, "application_id_1", "tracking_id_1", "transaction_id_1",
            "transaction_type_1", "resource_id_1", "service_name_1",
            "user_id_1", "external_id_1", "event_details_1", "status_1")
print("audit1")
audit.audit(2, "application_id_2", "tracking_id_2", "transaction_id_2",
            "transaction_type_2", "resource_id_2", "service_name_2",
            "user_id_2", "external_id_2", "event_details_2", "status_2")
print("audit2")
audit.audit(3, "application_id_3", "tracking_id_3", "transaction_id_3",
            "transaction_type_3", "resource_id_3", "service_name_3",
            "user_id_3", "external_id_3", "event_details_3", "status_3")
print("audit3")
audit.audit(4, "application_id_4", "tracking_id_4", "transaction_id_4",
            "transaction_type_4", "resource_id_4", "service_name_4",
            "user_id_4", "external_id_4", "event_details_4", "status_4")
print("audit4")
audit.audit(5, "application_id_5", "tracking_id_5", "transaction_id_5",
            "transaction_type_5", "resource_id_5", "service_name_5",
            "user_id_5", "external_id_5", "event_details_5", "status_5")
print("audit5")
audit.audit(6, "application_id_6", "tracking_id_6", "transaction_id_6",
            "transaction_type_6", "resource_id_6", "service_name_6",
            "user_id_6", "external_id_6", "event_details_6", "status_6")
print("audit6")
audit.audit(7, "application_id_7", "tracking_id_7", "transaction_id_7",
            "transaction_type_7", "resource_id_7", "service_name_7",
            "user_id_7", "external_id_7", "event_details_7", "status_7")
print("audit7")
audit.audit(8, "application_id_8", "tracking_id_8", "transaction_id_8",
            "transaction_type_8", "resource_id_8", "service_name_8",
            "user_id_8", "external_id_8", "event_details_8", "status_8")
print("audit8")
audit.audit(9, "application_id_9", "tracking_id_9", "transaction_id_9",
            "transaction_type_9", "resource_id_9", "service_name_9",
            "user_id_9", "external_id_9", "event_details_9", "status_9")
print("audit9")
audit.audit(10, "application_id_10", "tracking_id_10", "transaction_id_10",
            "transaction_type_10", "resource_id_10", "service_name_10",
            "user_id_10", "external_id_10", "event_details_10", "status_10")
print("audit10")
audit.audit(11, "application_id_11", "tracking_id_11", "transaction_id_11",
            "transaction_type_11", "resource_id_11", "service_name_11",
            "user_id_11", "external_id_11", "event_details_11", "status_11")
print("audit11")
