# Copyright 2015
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_config import cfg


service_available_group = cfg.OptGroup(
    name="service_available",
    title="Available OpenStack Services"
)

ServiceAvailableGroup = [
    cfg.BoolOpt("ranger", default=False,
                help="Whether or not ranger is expected to be available")
]

orm_group = cfg.OptGroup(
    name="ranger",
    title="Ranger Service option"
)

OrmGroup = [
    cfg.StrOpt("uri",
               default="orm",
               help="Uri of the orm service."),
    cfg.StrOpt("cms_port",
               default='7080',
               help="cms port of the orm url."),
    cfg.StrOpt("fms_port",
               default='8082',
               help="fms port of the orm url."),
    cfg.StrOpt("region_port",
               default='7003',
               help="region port of the orm url."),
    cfg.BoolOpt("alt_region_available",
                default=None,
                help="alt_region_available of the orm alternate region."),
    cfg.StrOpt("ims_port",
               default='8084',
               help="ims port of the orm url."),
    cfg.StrOpt("image_url",
               help="swift container url where image is located")
]
