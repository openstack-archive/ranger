use orm;

insert into region (region_id,
                    name,
	                address_state,
	                address_country,
	                address_city,
	                address_street,
	                address_zip,
	                region_status,
	                ranger_agent_version,
	                open_stack_version,
	                design_type,
                    location_type,
	                vlcp_name,
	                clli ,
	                description)
        values
        ("lcp_0","lcp 0", "Cal", "US", "Los Angeles", "Blv st", "012345", "functional", "ranger_agent 1.0", "kilo", "design_type_0", "location_type_0", "vlcp_0", "clli_0", "lcp_0 in LA"),
        ("lcp_1","lcp 1", "NY", "US", "New York", "5th avn", "112345", "functional", "ranger_agent 1.9", "kilo", "design_type_1", "location_type_1", "vlcp_1", "clli_1", "lcp_1 in NY"),
        ("lcp_2","lcp 2", "", "IL", "Tel Aviv", "Bazel 4", "212345", "functional", "ranger_agent 1.0", "kilo", "design_type_2", "location_type_2", "vlcp_2", "clli_2", "lcp_2 in Tel Aviv");

insert into rms_groups (group_id,
	                 name,
	                 description)
	    values
	    ("group_0", "group 0", "test group 0"),
        ("group_1", "group 1", "test group 1");

insert into group_region (group_id,
                          region_id)
        values
        ("group_0","lcp_0"),
        ("group_0","lcp_1"),
        ("group_1","lcp_2");

insert into region_meta_data (region_id,
	                          meta_data_key,
	                          meta_data_value)
        values
        ("lcp_0", "key_0", "value_0"),
        ("lcp_0", "key_1", "value_1"),
        ("lcp_1", "key_0", "value_0"),
        ("lcp_1", "key_1", "value_1"),
        ("lcp_2", "key_0", "value_0");

insert into region_end_point (region_id,
	                          end_point_type,
	                          public_url)
        values
        ("lcp_0", "ord", "http://ord_0.com"),
        ("lcp_0", "identity", "http://identity_0.com"),
        ("lcp_0", "dashboard", "http://image_0.com"),
        ("lcp_1", "ord", "http://ord_1.com"),
        ("lcp_1", "identity", "http://identity_1.com"),
        ("lcp_1", "dashboard", "http://image_1.com"),
        ("lcp_2", "ord", "http://ord_2.com"),
        ("lcp_2", "identity", "http://identity_2.com"),
        ("lcp_2", "dashboard", "http://image_2.com");
