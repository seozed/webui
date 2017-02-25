from flask import request, Flask
import redis
from flask import render_template
import time
from database import get_mongodb
import settings


app = Flask(__name__)
r = redis.StrictRedis()
db = get_mongodb(settings)

@app.route('/push', methods=['GET'])
def record():
    ip = request.remote_addr
    index = request.args.get('index')
    if index:
        r.hset('proxy', index, ip)
        update()
        return "push success"
    else:
        return "push faild"

def update():
    """更新squid反代节点"""

    ip_list = r.hgetall('proxy')
    with open('/etc/squid/squid.conf.example') as file:
        text = file.read()
        for i,ip in ip_list.items():
            text += "cache_peer {} parent 64444 0 no-query no-digest\n".format(ip.decode())

        text += "never_direct allow all"
        with open('/etc/squid/squid.conf', 'w') as outfile:
            outfile.write(text)

    # 使用sudo权限重载squid配置
    password = 2
    command = 'service squid reload'
    import os
    os.system('echo %s |sudo -S %s' % (password, command))

@app.route('/survive/')
def survive():
    """外部链接监控台"""

    # 添加链接
    links = request.args.get('add', '')
    name = request.args.get('name')
    for link in links.split('\r\n'):
        if '//' in link:
            item = {
                'link': link,
                'create_time': time.time(),
                'name': name
            }
            try:
                db['url'].insert(item)
            except:
                pass

    # 转换时间戳
    item = []
    for data in db['url'].find():
        time_local = time.localtime(data['create_time'])
        data['create_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        item.append(data)

    return render_template('survive.html', items=item)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
