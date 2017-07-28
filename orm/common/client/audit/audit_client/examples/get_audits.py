"""get_audits module."""

from audit_client.api import audit

audit_server_url = "http://127.0.0.1:8776/v1/audit/transaction"
num_of_send_retries = 3
time_wait_between_retries = 1
audit.init(audit_server_url, num_of_send_retries, time_wait_between_retries)
response = audit.get_audits(timestamp_from=1, timestamp_to=5,
                            application_id="application_id_1",
                            tracking_id="tracking_id_1",
                            transaction_id="transaction_id_1",
                            transaction_type="transaction_type_1",
                            resource_id="resource_id_1",
                            service_name="service_name_1", user_id="user_id_1",
                            external_id="external_id_1",
                            event_details="event_details_1", status="status_1",
                            limit=10)
print(response)

response = audit.get_audits(timestamp_from=1, timestamp_to=5, limit=10)
print(response)
