# -*- coding: utf-8 -*--

from resource_management import *
import os, json

# config object that holds the configurations declared in the -config.xml file
config = Script.get_config()
stack_root = Script.get_stack_root()
tmp_dir = Script.get_tmp_dir()

hostname = config['hostname']
elastic_user = config['configurations']['elastic-env']['elastic_user']
user_group = config['configurations']['cluster-env']['user_group']

version = default("/commandParams/version", "2.5.3.0-37")

elastic_base_dir = os.path.join(stack_root, version, 'elasticsearch-6.4.0')
elastic_head_base_dir = os.path.join(stack_root, version, 'elasticsearch-head')
elastic_conf_base_dir = elastic_base_dir + '/config'
elastic_head_site = elastic_head_base_dir + '/_site'

elastic_log_dir = config['configurations']['elastic-env']['elastic_log_dir'].rstrip("/")
elastic_pid_dir = config['configurations']['elastic-env']['elastic_pid_dir'].rstrip("/")
elastic_head_pid_dir = config['configurations']['elastic-env']['elastic_head_pid_dir'].rstrip("/")
elastic_pid_file = format("{elastic_pid_dir}/elasticsearch.pid")
elastic_head_pid_file = format("{elastic_head_pid_dir}/elasticsearch-head.pid")

service_package_dir = os.path.realpath(__file__).split('/scripts')[0]
elastic_scripts_dir = os.path.join(service_package_dir, "scripts")

es_log_file = os.path.join(elastic_log_dir, 'elasticsearch-start.log')

elasticsearch_service_host = default("/clusterHostInfo/elasticsearch_service_hosts", ['localhost'])[0]

# es component download local-yum path
if bool(config.get('hostLevelParams')) & bool(config['hostLevelParams'].get("repo_info")):
    yum_host = json.loads(config['hostLevelParams']['repo_info'])[0]['baseUrl']
    elastic_download_path = yum_host + '/elasticsearch/elasticsearch-6.4.0.tar.gz'
    elastic_head_download_path = yum_host + '/elasticsearch/elasticsearch-head.tar.gz'
    nodejs_download_path = yum_host + '/elasticsearch/node-v10.13.0-linux-x64.tar.gz'

cluster_name = config['configurations']['elastic-config']['cluster_name']
node_attr_rack = config['configurations']['elastic-config']['node_attr_rack']
path_data = config['configurations']['elastic-config']['path_data'].strip(",")
elasticsearch_yml = config['configurations']['elastic-config']['content']

bootstrap_memory_lock = str(config['configurations']['elastic-config']['bootstrap_memory_lock'])

# Elasticsearch expetcs that boolean values to be true or false and will generate an error if you use True or False.
if bootstrap_memory_lock == 'True':
    bootstrap_memory_lock = 'true'
else:
    bootstrap_memory_lock = 'false'

network_host = config['configurations']['elastic-config']['network_host']
elasticsearch_port = config['configurations']['elastic-config']['elasticsearch_port']
elasticsearch_head_port = config['configurations']['elastic-config']['elasticsearch_head_port']
http_cors_enabled = config['configurations']['elastic-config']['http_cors_enabled']

# discovery_zen_ping_unicast_hosts = config['clusterHostInfo']['all_hosts']
elasticsearch_service_hosts = config['clusterHostInfo']['elasticsearch_service_hosts']

# Need to parse the comma separated hostnames to create the proper string format within the configuration file
# Elasticsearch expects the format ["host1","host2"]
discovery_zen_ping_unicast_hosts = '[' + ','.join('"' + x + '"' for x in elasticsearch_service_hosts) + ']'

discovery_zen_minimum_master_nodes = len(elasticsearch_service_hosts) / 2 + 1

gateway_recover_after_nodes = config['configurations']['elastic-config']['gateway_recover_after_nodes']
node_max_local_storage_nodes = config['configurations']['elastic-config']['node_max_local_storage_nodes']

action_destructive_requires_name = str(config['configurations']['elastic-config']['action_destructive_requires_name'])

# Elasticsearch expecgts boolean values to be true or false and will generate an error if you use True or False.
if action_destructive_requires_name == 'True':
    action_destructive_requires_name = 'true'
else:
    action_destructive_requires_name = 'false'

# head requires
# http_cors_enabled = config['configurations']['elastic-config']['http_cors_enabled']
http_cors_allow_origin = config['configurations']['elastic-config']['http_cors_allow_origin']

if http_cors_enabled:
    http_cors_enabled = 'true'
else:
    http_cors_enabled = 'false'

ping_timeout_default = config['configurations']['elastic-config']['ping_timeout_default']
discovery_zen_ping_timeout = config['configurations']['elastic-config']['discovery_zen_ping_timeout']
zookeeper_session_timeout = config['configurations']['elastic-config']['zookeeper.session.timeout']
