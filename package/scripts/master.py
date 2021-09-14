# -*- coding: utf-8 -*--

from resource_management import *
from resource_management.core.logger import Logger


class Master(Script):

    def install(self, env):
        import params
        env.set_params(params)

        Logger.info("Install begin")

        # Download elasticsearch.tar.gz
        Execute('wget {0} -O elasticsearch.tar.gz'.format(params.elastic_download_path))

        # Install Elasticsearch
        Execute('tar -zxvf elasticsearch.tar.gz -C /usr/hdp/2.5.3.0-37/')

        # Remove Elasticsearch installation file
        Execute('rm -rf elasticsearch.tar.gz')

        # sh config file in targethost
        cmd = format("cd {elastic_scripts_dir}; chmod +x ./changeOsConfToES.sh && sh ./changeOsConfToES.sh")
        Execute(cmd)

        Logger.info("Install complete")

    def configure(self, env):
        # Import properties defined in -config.xml file from the params class
        import params

        Logger.info("Configuration begin")

        # This allows us to access the params.elastic_pid_file property as
        # format('{elastic_pid_file}')
        env.set_params(params)

        # Update the port in the web UI that displays the connection to the Elasticsearch
        # cmd = format("cd {elastic_head_site}; sh ./changeHostName.sh {elasticsearch_port} {elasticsearch_head_port}")
        # Execute(cmd)

        # 删除pid目录
        Directory([params.elastic_pid_dir],
                  action="delete")

        # 创建pid目录
        Directory([params.elastic_log_dir, params.elastic_pid_dir],
                  mode=0755,
                  cd_access='a',
                  owner=params.elastic_user,
                  group=params.user_group,
                  create_parents=True
                  )

        # Ensure all files owned by elasticsearch user
        cmd = format("chown -R {elastic_user}:{user_group} {elastic_base_dir} {elastic_log_dir} {elastic_pid_dir}")
        Execute(cmd)

        elasticsearch_yml = InlineTemplate(params.elasticsearch_yml)
        File(format("{elastic_conf_base_dir}/elasticsearch.yml"),
             owner=params.elastic_user,
             group=params.user_group,
             content=elasticsearch_yml)

        # mkdir elasticsearch path_data
        path_data_es = params.path_data.split(',')
        for i in range(len(path_data_es)):
            Directory([path_data_es[i]],
                      mode=0755,
                      cd_access='a',
                      owner=params.elastic_user,
                      group=params.user_group,
                      create_parents=True
                      )
            cmd = "chown -R {0}:{1} {2}".format(params.elastic_user, params.user_group, path_data_es[i])
            Execute(cmd)

        Logger.info("Configuration complete")

    def start(self, env):
        import params

        Logger.info("Configuration start")

        env.set_params(params)
        # Configure Elasticsearch
        self.configure(env)

        # Start Elasticsearch
        cmd = format("{elastic_base_dir}/bin/elasticsearch -d -p {elastic_pid_file}")
        Execute(cmd, user=params.elastic_user)

        # get Elasticsearch pid and write filex
        Execute(
            'ps -ef | grep elasticsearch-6.4.0/config | grep -v grep | awk \'{print $2}\' > ' + params.elastic_pid_file,
            user=params.elastic_user)

        Logger.info("Start complete")

    def stop(self, env):
        import params

        Logger.info("Stop begin")
        env.set_params(params)

        # Stop Elasticsearch
        Execute('ps -ef | grep elasticsearch-6.4.0/config | grep -v grep | awk \'{print $2}\' | xargs kill -9',
                user=params.elastic_user,
                ignore_failures=True)
        # 删除pid文件
        File([params.elastic_pid_file],
             action="delete")

        Logger.info("Stop complete")

    def status(self, env):
        # Import properties defined in -env.xml file from the status_params class
        import status_params

        # This allows us to access the params.elastic_pid_file property as
        #  format('{elastic_pid_file}')
        env.set_params(status_params)

        # Use built-in method to check status using pidfile
        check_process_status(status_params.elastic_pid_file)

    def restart(self, env):
        self.stop(env)
        self.start(env)


if __name__ == "__main__":
    Master().execute()
