SET sql_notes=0;

use orm;

create table if not exists transactions(
  id integer not null auto_increment,
  timestamp bigint not null,
  user_id varchar(64) binary null,
  application_id varchar(64) binary not null,
  tracking_id varchar(64) binary not null,
  external_id varchar(64) binary null,
  transaction_id varchar(64) binary not null,
  transaction_type varchar(64) binary not null,
  event_details varchar(255) binary null,
  status varchar(64) binary null,
  resource_id varchar(64) binary not null,
  service_name varchar(64) binary not null,
  primary key (id),
  key tracking_id_index (tracking_id),
  key transaction_id_index (transaction_id),
  key resource_id_index (resource_id),
  unique(timestamp, user_id, application_id, tracking_id, external_id, transaction_id,
  transaction_type, event_details, status, resource_id, service_name));
