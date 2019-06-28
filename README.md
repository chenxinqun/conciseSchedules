conciseSchedules -- 这是一个简洁的兼容crontab语法的定时器工具
==========================
[![PyPI](https://img.shields.io/pypi/v/conciseSchedules.svg)](https://pypi.org/project/conciseSchedules/)

## conciseSchedules 有两种工作模式:
一种是"crontab_tasks", 兼容 crontab 语法, 只支持以shell启动脚本的方式启动定时器, 即subprocess.Popen所支持的方式启动. 最小时间颗粒度为分钟.
一种是"schedule_tasks",  既兼容 crontab 语法, 又支持 conciseSchedules 语法, 只支持通过 python callable 对象启动定时器, 即threading.Thread所支持的方式启动. 最小时间颗粒度为秒.
##### 首先, 介绍一下"schedule_tasks"工作模式, 要使用它很简单:
conciseSchedules {   
                    'second': int or None or tuple(strat, end),
                    'minute': int or None or tuple(strat, end),
                    'hour': int or None or tuple(strat, end),
                    'day': int or None or tuple(strat, end),
                    'month': int or None or tuple(strat, end),
                    'weekday': int or None or tuple(strat, end),
                }
1.不需要的时间颗粒度, 可以不传, 即为None. 至少要有一个颗粒度不为None. 
所有为None的颗粒度, 如果比有值的颗粒度小, 则设置为1, 如果比有值的颗粒度大, 则设置为all.
2.如果传int类型,  >= 0 的值则表示明确的时间, 即第几(秒, 分, 时, 日, 月) 或 周几, 其中颗粒度为天的时候, 传0无效. 如果传-1, 则相当于crontab "*/1"的语法, 即"每1(秒, 分, 时, 日, 月, 周)", 其中'weekday' 0表示星期日, 1-6表示星期一至星期六, 传-1的话, 会被解释为每周启动一次, 且时间设定为每周1的1点1分启动.
3.如果传二元素元祖, 则相当于crontab "int-int" 即从几至几.
``` 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test.py


def test():
    print('hello conciseSchedules!', test.__name__)


if __name__ == '__main__':
    import conciseSchedules as scheduler

    tasks_conf = {
        'schedule_tasks':[
        {'schedule':{'second': -1}, 'target': test,}    # 每秒钟启动一次
        {'schedule':{'minute': -1}, 'target': test,}    # 每分钟启动一次. 默认是每分钟的第1秒.
        {'schedule':{'second': 15, 'minute': (10-20))}, 'target': test,}    # 每小时的10-12分的第15秒启动
        {'schedule':{'hour': -1)}, 'target': test,}           # 每小时启动一次.默认是每小时的1分1秒.
        {'schedule':{'minute': 1, 'hour': 10, 'day': 1, 'month': 10)}, 'target': test,}     # 每年10月1日10点1分启动.
        ], 
    }
    scheduler.set_tasks(tasks_conf)
    scheduler.run_loop()

```
这样就创建了五个定时器.

#### 你还可以这样:
``` 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test.py


def test():
    print('hello conciseSchedules!', test.__name__)


if __name__ == '__main__':
    import conciseSchedules as scheduler
    
    task = {'schedule_tasks': {'schedule':{'second': -1}, 'target': test,}}    # 每秒钟启动一次
    scheduler.add_task(task)
    scheduler.run_loop()

``` 
这样动态添加单个任务.

#### 同时你还可以使用装饰器:
``` 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test.py

import conciseSchedules as scheduler


@scheduler.task(schedule={'second': -1})
def test():
    print('hello conciseSchedules!', test.__name__)


if __name__ == '__main__':
    scheduler.run_loop()

``` 
###需要注意的是, 装饰器, 只支持独立的 function, 不支持任何挂靠在类下面的 method. 如果有需要用到类的时候, 请用 function 封装一层.

如果你要在 "crontab_tasks" 模式使用 crontab 语法, 把以上例子中 'schedule': {} 关键字改成 'crontab': '*/1 * * * * *' 就行了. 要注意 'schedule_tasks' 工作模式下, crontab 支持秒级颗粒度, 第一位是 "秒", 第二位及以后是 "分 时 日 月 周". 
----------------------------
### 下面是"crontab_tasks"工作模式:
crontab "分 时 日 月 周" 共五种颗粒度, 用空格隔开. 支持语法: "*" 任何时间, "*/3" 每逢3(能整除3), "1-10" 在 1至10之间, "1" 精确到1. 例如: "*/1 1 * * *" 则表示每天1点的每1分钟启动. 如果 周 的参数是 "*/1", 则表示每周启动一次, 且启动时间在周1, 如果是"*/> 1", 则会被解释成"能 整除 大于1的数的星期几启动" 而不是每年的第几周启动. 至于其它, 请参考 crontab 文档.
``` 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test.py
def test():
    print('hello conciseSchedules!', test.__name__)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# start.py


if __name__ == '__main__':
    import conciseSchedules as scheduler
    tasks_conf = {
        'crontab_tasks':[
        {'crontab':'*/1 ', 'target': test,}    # 每分钟启动一次. 默认是每分钟的第1秒.
        {'crontab':"", 'target': test,}    # 每小时的10-12分启动
        {'crontab':{'hour': -1)}, 'target': test,}           # 每小时启动一次.默认是每小时的1分1秒.
        {'crontab':{'minute': 1, 'hour': 10, 'day': 1, 'month': 10)}, 'target': test,}     # 每年10月1日10点1分启动.
        ], 
    }
    scheduler.set_tasks(tasks_conf)
    scheduler.run_loop()
    """如果要配合系统 crontab 来使用, 请使用 scheduler.run() 方法"""
``` 
