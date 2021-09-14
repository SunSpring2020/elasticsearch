# -*- coding: utf-8 -*--

from resource_management import *
import os


# 安装：
# 1、安装nodejs、pm2
# 2、下载elasticsearch-head源码

# 配置：
# 1、更改 elasticsearch-head 相关文件的 ip:port
# 2、创建pid目录
# 3、更改所有者（源码目录、pid目录、日志目录）

# 启动
# 1、使用pm2的方式启动

class Head(Script):
    def install(self, env):
        import params
        env.set_params(params)

        Logger.info('elasticsearch-head install begin.')

        # install nodejs and pm2
        cmd = format("cd {elastic_scripts_dir}; sh ./cfgNodejs.sh {nodejs_download_path}")
        Execute(cmd)

        # Download Elasticsearch and head
        Execute('wget {0} -O elasticsearch-head.tar.gz'.format(params.elastic_head_download_path))

        # Install Elasticsearch
        Execute('tar -zxvf elasticsearch-head.tar.gz -C {0}/{1}'.format(params.stack_root, params.version))

        # Remove Elasticsearch installation file
        Execute('rm -rf elasticsearch-head.tar.gz')

        Logger.info('elasticsearch-head install complete.')

    def configure(self, env):
        # Import properties defined in -config.xml file from the params class
        import params
        env.set_params(params)

        Logger.info("Configuration begin")

        # 删除pid目录
        Directory([params.elastic_head_pid_dir], action="delete")

        # 创建pid目录
        Directory([params.elastic_head_pid_dir],
                  mode=0755,
                  cd_access='a',
                  owner=params.elastic_user,
                  group=params.user_group,
                  create_parents=True
                  )

        # Ensure all files owned by elasticsearch user
        cmd = format("chown -R {elastic_user}:{user_group} {elastic_head_base_dir} {elastic_head_pid_dir}")
        Execute(cmd)

        # Update the port in the web UI that displays the connection to the Elasticsearch
        File(os.path.join(params.tmp_dir, 'changeHostName.sh'),
             owner=params.elastic_user,
             group=params.user_group,
             mode=0644,
             content=Template("changeHostName.sh.j2")
             )
        cmd = format("cd {tmp_dir}; sh ./changeHostName.sh")
        Execute(cmd, user=params.elastic_user)

        Logger.info("Configuration complete")

    def start(self, env):
        import params
        env.set_params(params)

        Logger.info("Start command begin")

        # Configure elasticsearch-head
        self.configure(env)

        # Start elasticsearch-head
        cmd = format("cd {elastic_head_base_dir}; pm2 start npm --name elasticsearch-head -- run start")
        Execute(cmd, user=params.elastic_user)

        # get elasticsearch-head pid and write file
        Execute(
            'pm2 pid elasticsearch-head > ' + params.elastic_head_pid_file,
            user=params.elastic_user)

        Logger.info(params.elastic_base_dir)
        Logger.info("Start command complete")

    def stop(self, env):
        import params
        env.set_params(params)

        # kill elasticsearch-head
        cmd = format("pm2 delete elasticsearch-head")
        Execute(cmd, user=params.elastic_user, ignore_failures=True)

        # delete elasticsearch-head pid file
        # 删除pid文件
        File([params.elastic_head_pid_file],
             action="delete")

    def status(self, env):
        # Import properties defined in -env.xml file from the status_params class
        import status_params
        env.set_params(status_params)

        # Use built-in method to check status using pidfile
        check_process_status(status_params.elastic_head_pid_file)

    def test_head_check(self, env):
        Logger.info("******** custom process ********")
        Logger.info("custom elasticsearch head successfully!")


if __name__ == "__main__":
    Head().execute()
