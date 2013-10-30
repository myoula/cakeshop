系统要求：
nginx
centos 6.x
mysql 5.1x
memcached

一 安装基本环境
1 安装系统环境
rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-6

yum -y install gcc nginx mysql-libs mysql-server mysql-devel memcached python-setuptools

2 安装 virtualenv
easy_install virtualenv

3 安装pypy
yum -y install pypy-libs pypy pypy-devel

4 创建基本环境
cd /home/www
virtualenv --no-site-packages -p pypy czcake

cd czcake
source bin/activate

#把源文件放进来

pip install -r requirement.txt

mkdir etc
echo_supervisord_conf > etc/supervisord.conf

vi etc/supervisord.conf
#添加配置
[program:czcake8080]
command=python /home/www/czcake/src/manager.py
autostart=true
stderr_logfile = /var/log/nginx/app.log
stdout_logfile = /var/log/nginx/app.log

supervisord -c /home/www/czcake/etc/supervisord.conf

vi /etc/nginx.conf
#添加配置
upstream czcake {
    server 127.0.0.1:8080;
}

server {
    listen       80;
    server_name czcake.heycz.com;
    client_max_body_size  4M;

    location /
    {
        proxy_pass_header Server;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_pass http://czcake;
    }
}

二 项目配置
cd src
vi setting.py
#设置数据库和缓存服务器信息

#初始化数据库
python manager.py --cmd=syncdb

三 开始运行
supervisorctl restart all
service nginx restart