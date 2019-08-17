#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@File  : conciseSchedules.py
@Author: ChenXinqun
@Date  : 2019/5/25 17:21
'''
__title__ = 'conciseSchedules'
__url__ = 'https://github.com/chenxinqun/conciseSchedules'
__version__ = '1.0.3'
__author__ = 'ChenXinqun'
__author_email__ = 'chenxinqun163@163.com'
__maintainer__ = '{} <{}>'.format(__author__, __author_email__)
__maintainer_email__ = '{}'.format(__author_email__)
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2019 {}'.format(__author__)
__description__ = 'A Concise Schedules module -- {} for Python.'.format(__title__)
###===###


import re
import sys
import pytz
import time
from copy import deepcopy
from threading import Thread
from subprocess import Popen
from typing import List, Dict, Any, Callable, Tuple
from datetime import datetime
from traceback import print_exc
from tzlocal import get_localzone
from multiprocessing.pool import ThreadPool as Pool


class Schedules:
    '''
 使用实例:
 from conciseSchedules import scheduler
 # import conciseSchedules as scheduler
 tasks_conf = {'crontab_tasks': [
     {'crontab': '*/1 * * * *', 'shell': 'python tests.py'}
     ],
     'schedule_tasks':[
         {
             'schedule': {
                             'second': int or None or tuple(strat, end),
                             'minute': int or None or tuple(strat, end),
                             'hour': int or None or tuple(strat, end),
                             'day': int or None or tuple(strat, end),
                             'month': int or None or tuple(strat, end),
                             'weekday': int or None or tuple(strat, end),
                         }
             'crontab': '*/1(sechond) * * * * *'
             'target': func,
             'args': func args,
             'kwargs': func kwargs,
         }
     ]
 }
 scheduler.set_tasks(tasks_conf)
 scheduler.run_loop()
 如果配合Linux的crontab使用, 请使用 scheduler.run() 方法
 如果要在程序中动态的添加 task, 请使用 scheduler.add_task({'crontab_tasks': {'crontab': '*/1 * * * *', 'shell': 'python tests.py'}})
 或者  scheduler.add_task({'schedule_tasks': {'crontab': '*/1 * * * * *', 'target': tests_run, args=(arg1,)}})

 类参数说明:
 Schedules.pool_size: 线程池大小
 Schedules.__point:  默认时间点, 没有设置某时间是, 用此值
 Schedules.__time_field_crontab:  crontab的默认字段
 Schedules.__all_time_crontab:  所有的crontab时间范围
 Schedules.__default_crontab:   crontab默认时间配置
 Schedules.__time_field_schedule:  schedule的默认字段
 Schedules.__all_time_schedule:  schedule的所有时间范围
 Schedules.__default_schedule:  schedule的默认时间配置
 Schedules.__any_pattern:  crontab语法校验正则
 Schedules.__every_pattern:  crontab语法校验正则
 Schedules.__between_pattern:  crontab语法校验正则
 Schedules.__at_pattern:  crontab语法校验正则
 Schedules.__at_more_pattern:  crontab语法校验正则
 Schedules.__key_crontab_tasks: 配置字典中必要的参数名
 Schedules.__key_schedule_tasks:  配置字典中必要的参数名
 Schedules.__tasks_key_args:  配置字典中必要的参数名
 Schedules.__tasks_key_shell: 配置字典中必要的参数名
 Schedules.__tasks_key_crontab: 配置字典中必要的参数名
 Schedules.__tasks_key_schedule: 配置字典中必要的参数名
 Schedules.__tasks_key_target: 配置字典中必要的参数名
 Schedules.__tasks_key_kwargs: 配置字典中必要的参数名
 Schedules.__max_7:   最大值为7的时间
 Schedules.__max_12:  最大值为12的时间
 Schedules.__max_24:  最大值为24的时间
 Schedules.__max_31:  最大值为31的时间
 Schedules.__max_60:  最大值为60的时间


    '''
    pool_size = 10
    __point = [1]
    __time_field_crontab = 'minute hour day month weekday'.split(' ')
    __all_time_crontab = [
        [x for x in range(0, 60)],
        [x for x in range(0, 24)],
        [x for x in range(1, 32)],
        [x for x in range(1, 13)],
        [x for x in range(0, 7)]
    ]
    __default_crontab = dict(zip(__time_field_crontab, __all_time_crontab))
    __time_field_schedule = deepcopy(__time_field_crontab)
    __time_field_schedule.insert(0, 'second')
    __all_time_schedule = deepcopy(__all_time_crontab)
    __all_time_schedule.insert(0, [x for x in range(0, 60)])
    __default_schedule = dict(zip(__time_field_schedule, __all_time_schedule))
    __any_pattern = re.compile('^\*$')
    __every_pattern = re.compile('^\*/\d{1,2}$')
    __between_pattern = re.compile('^\d{1,2}-\d{1,2}$')
    __at_pattern = re.compile('^\d{1,2}$')
    __at_more_pattern = re.compile('^\d[\d,]+\d{1,2}$')
    __key_crontab_tasks = 'crontab_tasks'
    __key_schedule_tasks = 'schedule_tasks'
    __tasks_key_args = 'args'
    __tasks_key_shell = 'shell'
    __tasks_key_crontab = 'crontab'
    __tasks_key_schedule = 'schedule'
    __tasks_key_target = 'target'
    __tasks_key_kwargs = 'kwargs'
    __max_7 = ['weekday']
    __max_12 = ['month']
    __max_24 = ['hour']
    __max_31 = ['day']
    __max_60 = ['second', 'minute']

    def __init__(self, tasks_conf: Dict[str, List[Dict[str, Any]]] = None):
        if tasks_conf is None:
            self.conf = {}
        else:
            self.set_tasks(tasks_conf)
        self.set_timezone()
        self.pool = None
        self.__stop = 0

    @classmethod
    def _crontab_syntax_analyze(cls, field: list, args: str, default: dict) -> dict:
        '''

        :param field:
        :param args:
        :param default:
        :return:
        '''
        try:
            point = cls.__point
            c = {}
            a = dict(zip(field, args.split(' ')))
            for item in a:
                val = a[item]
                if cls.__any_pattern.match(val):
                    c[item] = default[item]
                elif cls.__every_pattern.match(val):
                    step = int(val.split('/')[1])
                    cls.item_out_of_range(item, step)
                    c[item] = [x for x in default[item] if x % step == 0]
                elif cls.__between_pattern.match(val):
                    between = [int(x) for x in val.split('-')]
                    for i in between:
                        cls.item_out_of_range(item, int(i))
                    c[item] = [x for x in default[item] if x in between]
                elif cls.__at_pattern.match(val):
                    at = int(val)
                    cls.item_out_of_range(item, at)
                    c[item] = [x for x in default[item] if x == at]
                elif cls.__at_more_pattern.match(val):
                    at_more = [int(x) for x in val.split(',')]
                    for i in at_more:
                        cls.item_out_of_range(item, i)
                    c[item] = [x for x in default[item] if x in at_more]
                else:
                    raise TypeError('%s must be "*" or "*/int" or "int" or "int-int", got "%s"' % (item, val))

            if not cls.__any_pattern.match(a.get('hour', '')):
                if cls.__any_pattern.match(a.get('minute', '')):
                    c['minute'] = point
                if cls.__any_pattern.match(a.get('second', '')):
                    c['second'] = point

            if not cls.__any_pattern.match(a.get('day', '')):
                if cls.__any_pattern.match(a.get('hour', '')):
                    c['hour'] = point
                if cls.__any_pattern.match(a.get('minute', '')):
                    c['minute'] = point
                if cls.__any_pattern.match(a.get('second', '')):
                    c['second'] = point

            if not cls.__any_pattern.match(a.get('weekday', '')):
                if cls.__any_pattern.match(a.get('hour')):
                    c['hour'] = point
                if cls.__any_pattern.match(a.get('minute', '')):
                    c['minute'] = point
                if cls.__any_pattern.match(a.get('second', '')):
                    c['second'] = point

            if not cls.__any_pattern.match(a.get('month', '')):
                if cls.__any_pattern.match(a.get('day', '')):
                    c['day'] = point
                if cls.__any_pattern.match(a.get('hour', '')):
                    c['hour'] = point
                if cls.__any_pattern.match(a.get('minute', '')):
                    c['minute'] = point
                if cls.__any_pattern.match(a.get('second', '')):
                    c['second'] = point
            return c
        except IndexError as e:
            print_exc()
            raise e
        except Exception as e:
            print_exc()
            raise Exception('crontab syntax error')

    @staticmethod
    def item_out_of_range(k, v) -> None:
        '''

        :param k:
        :param v:
        :return:
        '''
        cls = Schedules
        if k in cls.__max_7 and v >= 7:
            return cls.out_of_range(k, v)
        elif k in cls.__max_12 and v > 12:
            return cls.out_of_range(k, v)
        elif k in cls.__max_24 and v >= 24:
            return cls.out_of_range(k, v)
        elif k in cls.__max_31 and v > 31:
            return cls.out_of_range(k, v)
        elif k in cls.__max_60 and v >= 60:
            return cls.out_of_range(k, v)

    @staticmethod
    def out_of_range(k, v) -> None:
        '''

        :param k:
        :param v:
        :return:
        '''
        raise IndexError('%s: %s out of range' % (k, v))

    @classmethod
    def _schedule_syntax_analyze(cls, field: list, kwargs: dict, default: dict) -> dict:
        '''

        :param field:
        :param kwargs:
        :param default:
        :return:
        '''
        try:
            point = cls.__point
            c = {}
            for kw in kwargs:
                if kw not in field:
                    raise KeyError('field must in %s' % field)
            for k, v in default.items():
                arg = kwargs.get(k)
                if arg in v:
                    c[k] = [arg]
                else:
                    if arg is None:
                        if k == 'second':
                            c[k] = point
                        else:
                            c[k] = v
                    elif isinstance(arg, int):
                        if arg < 0:
                            step = abs(arg)
                            cls.item_out_of_range(k, step)
                            c[k] = [x for x in v if x % step == 0]
                        else:
                            cls.out_of_range(k, arg)
                    elif isinstance(arg, tuple):
                        assert len(arg) == 2
                        start, end = arg
                        assert isinstance(start, int) and isinstance(end, int)
                        ilst = []
                        for i in v:
                            if start <= i <= end:
                                ilst.append(i)
                        c[k] = ilst
                    else:
                        raise TypeError('%s: %s type must be int, got %s' % (k, arg, type(arg).__name__))

            if isinstance(kwargs.get('hour'), int):
                if kwargs.get('minute') is None:
                    c['minute'] = point
                if kwargs.get('second') is None:
                    c['second'] = point

            if isinstance(kwargs.get('day'), int):
                if kwargs.get('hour') is None:
                    c['hour'] = point
                if kwargs.get('minute') is None:
                    c['minute'] = point
                if kwargs.get('second') is None:
                    c['second'] = point

            if isinstance(kwargs.get('month'), int):
                if kwargs.get('day') is None:
                    c['day'] = point
                if kwargs.get('hour') is None:
                    c['hour'] = point
                if kwargs.get('minute') is None:
                    c['minute'] = point
                if kwargs.get('second') is None:
                    c['second'] = point

            if isinstance(kwargs.get('weekday'), int):
                if kwargs.get('hour') is None:
                    c['hour'] = point
                if kwargs.get('minute') is None:
                    c['minute'] = point
                if kwargs.get('second') is None:
                    c['second'] = point

            return c
        except Exception as e:
            print(e)
            print_exc()
            raise Exception('crontab syntax error')

    @classmethod
    def get_date_time(cls, tz: str = None):
        if not tz:
            tz = 'Asia/Shanghai'
        timezone = pytz.timezone(tz)
        date_time = datetime.now(timezone)
        return date_time

    @classmethod
    def __start_analyze(cls, collec: dict, tz: str = None) -> Tuple[List[bool], datetime]:
        '''

        :param collec:
        :param tz:
        :return:
        '''
        date_time = cls.get_date_time(tz)
        condition = []
        for item in collec:
            tm = getattr(date_time, item)
            if callable(tm):
                tm = tm()
            if tm in collec[item]:
                condition.append(True)
            else:
                condition.append(False)
        return condition, date_time

    @classmethod
    def __crontab_start(cls, crontab: str, shell: str, tz: str = None) -> None:
        '''

        :param crontab:
        :param shell:
        :param tz:
        :return:
        '''
        c = cls._crontab_syntax_analyze(cls.__time_field_crontab, crontab, cls.__default_crontab)
        condition, date_time = cls.__start_analyze(c, tz)
        tzinfo = date_time.tzinfo
        if all(condition):
            p = Popen(shell, shell=True)
            print(
                "[%s %s]" % (tzinfo, date_time.strftime('%Y-%m-%d %H:%M:%S')),
                'exec', "[%s]" % p.args, 'start', p.pid
            )

    @classmethod
    def __schedules_start(
            cls, target: Callable,
            schedule: dict = None,
            crontab: str = None,
            args: tuple = None,
            kwargs: dict = None,
            tz: str = None
    ) -> None:
        '''
        :param target: a callable obj
        :param schedule: a dict like {
                            'second': int or None or tuple(strat, end),
                            'minute': int or None or tuple(strat, end),
                            'hour': int or None or tuple(strat, end),
                            'day': int or None or tuple(strat, end),
                            'month': int or None or tuple(strat, end),
                            'weekday': int or None or tuple(strat, end),
                        }
        :param crontab: a str like '*/1(sechond) * * * * *'
        :param args: func args
        :param kwargs: func kwargs
        :return:
        '''
        if isinstance(crontab, str):
            c = cls._crontab_syntax_analyze(cls.__time_field_schedule, crontab, cls.__default_schedule)
        else:
            c = cls._schedule_syntax_analyze(cls.__time_field_schedule, schedule, cls.__default_schedule)
        condition, date_time = cls.__start_analyze(c, tz)
        tzinfo = date_time.tzinfo
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = dict()
        if all(condition):
            t = Thread(target=target, args=args, kwargs=kwargs)
            t.start()
            if hasattr(target, '__name__'):
                name = target.__name__
            else:
                name = target
            print(
                "[%s %s]" % (tzinfo, date_time.strftime('%Y-%m-%d %H:%M:%S')),
                'exec', '[%s(*%s, **%s)]' % (name, args, kwargs), 'start'
            )
            t.join()

    def set_timezone(self, tz: str = None) -> None:
        '''

        :param tz:
        :return:
        '''
        if isinstance(tz, str):
            tz_list = self.timezone_listing()
            if tz not in tz_list:
                raise TypeError('tz: %s invalid, you need use self.timezone_listing(country) got timezone info' % tz)
            tzinfo = tz
        else:
            tzinfo = get_localzone()
        if not tzinfo:
            tzinfo = 'Asia/Shanghai'
        self.tzinfo = str(tzinfo)

    def timezone_listing(self, country: str = None) -> list:
        '''
        :param country: a country code for example 'cn', 'us'
         or use self.timezon_countrys() got!
         if country is None return ALL
        :return: the country timezone city list, default cn
        '''
        if country is None:
            return pytz.common_timezones
        return pytz.country_timezones(country)

    def timezon_countrys(self) -> dict:
        ''':return countrys name dict'''
        return dict(pytz.country_names)

    def __task_assert(self, item, stp=0) -> None:
        '''
        :param item:
        :param stp:
        :return:
        '''
        if stp == 0:
            assert isinstance(*item)
        elif stp == 1:
            assert isinstance(*item) or item[0] is None
        elif stp == 2:
            assert isinstance(item, dict)
            assert isinstance(item.get(self.__tasks_key_crontab), str)
            assert isinstance(item.get(self.__tasks_key_shell), str)
        elif stp == 3:
            assert isinstance(item, dict)
            assert isinstance(item.get(self.__tasks_key_schedule), dict) or item.get(self.__tasks_key_schedule) is None
            assert isinstance(item.get(self.__tasks_key_crontab), str) or item.get(self.__tasks_key_crontab) is None
            assert item.get(self.__tasks_key_schedule) or item.get(self.__tasks_key_crontab)
            assert callable(item.get(self.__tasks_key_target))
            assert isinstance(item.get(self.__tasks_key_args), tuple) or item.get(self.__tasks_key_args) is None
            assert isinstance(item.get(self.__tasks_key_kwargs), dict) or item.get(self.__tasks_key_kwargs) is None
        elif stp == 4:
            assert item[0] in item[2] or item[1] in item[2]
        elif stp == 5:
            assert item[0] or item[1]

    def set_pool_size(self, size: int) -> None:
        '''这个方法用来重设 pool_size(默认值为10)'''
        self.__task_assert((size, int), 0)
        Schedules.pool_size = size

    def set_tasks(self, tasks_conf: Dict[str, List[Dict[str, Any]]]) -> None:
        '''
         这是一个用来批量添加任务的方法
        :param tasks_conf: {
             'crontab_tasks': [{'crontab_tasks': '', 'shell': ''}],
             'schedule_tasks':
                 [
                     {
                         'schedule': {
                             'second': int or None or tuple(strat, end),
                             'minute': int or None or tuple(strat, end),
                             'hour': int or None or tuple(strat, end),
                             'day': int or None or tuple(strat, end),
                             'month': int or None or tuple(strat, end),
                             'weekday': int or None or tuple(strat, end),
                         }
                         'crontab': '*/1(sechond) * * * * *'   # str , the model add sechond.
                         'target': func,
                         'args': func args,
                         'kwargs': func kwargs,
                 }
             ]
         }
        :return:

        '''
        self.__task_assert((tasks_conf, dict), 0)
        self.__task_assert((self.__key_crontab_tasks, self.__key_schedule_tasks, tasks_conf), 4)
        crontab_tasks = tasks_conf.get(self.__key_crontab_tasks)
        if crontab_tasks:
            self.__task_assert((crontab_tasks, list), 0)
            for item in crontab_tasks:
                self.__task_assert(item, 2)
        schedule_tasks = tasks_conf.get(self.__key_schedule_tasks)
        if schedule_tasks:
            self.__task_assert((schedule_tasks, list), 0)
            for item in schedule_tasks:
                self.__task_assert(item, 3)
        self.conf = tasks_conf

    def add_task(self, t: Dict[str, dict]) -> None:
        '''

        :param t:
             {
         'crontab_tasks': {'crontab': '*/1 * * * *', 'shell': 'python tests.py'}
         }

         or  {
         'schedule_tasks': {'crontab': '*/1 * * * * *', 'target': tests_run, args=(1,)}
         }

         这是一个用来添加单个任务的方法

        :return: None

        '''
        self.__task_assert((t, dict), 0)
        crontab = t.get(self.__key_crontab_tasks)
        self.__task_assert((crontab, dict), 1)
        if crontab:
            self.__task_assert(crontab, 3)
            if not isinstance(self.conf.get(self.__key_crontab_tasks), list):
                self.conf[self.__key_crontab_tasks] = []
            self.conf[self.__key_crontab_tasks].append(crontab)

        schedule = t.get(self.__key_schedule_tasks)
        self.__task_assert((schedule, dict), 1)
        if schedule:
            self.__task_assert(schedule, 3)
            if not isinstance(self.conf.get(self.__key_schedule_tasks), list):
                self.conf[self.__key_schedule_tasks] = []
            self.conf[self.__key_schedule_tasks].append(schedule)

    def task(self, schedule: dict = None, crontab: str = None, args: tuple = None, kwargs: dict = None) -> Callable:
        '''

        :param schedule:
        :param crontab:
        :param args:
        :param kwargs:
        :return:
        '''
        add_task = self.add_task
        key_schedule_tasks = self.__key_schedule_tasks
        tasks_key_schedule = self.__tasks_key_schedule
        tasks_key_crontab = self.__tasks_key_crontab
        tasks_key_target = self.__tasks_key_target
        tasks_key_args = self.__tasks_key_args
        tasks_key_kwargs = self.__tasks_key_kwargs

        def add(func) -> Callable:
            def wrap(*params, __task__=True, **kwparams):
                if not __task__:
                    t = {key_schedule_tasks:
                        {
                            tasks_key_schedule: schedule,
                            tasks_key_crontab: crontab,
                            tasks_key_target: func,
                            tasks_key_args: args,
                            tasks_key_kwargs: kwargs,
                        }
                    }
                    add_task(t)
                    return func
                else:
                    return func

            return wrap(__task__=False)

        return add

    def _get_pool(self) -> Pool:
        '''

        :return:
        '''
        crontab_tasks = self.conf.get(self.__key_crontab_tasks) or []
        schedule_tasks = self.conf.get(self.__key_schedule_tasks) or []
        task_len = len(crontab_tasks) + len(schedule_tasks)
        if 0 < task_len < 10:
            size = task_len
        else:
            size = self.pool_size
        return Pool(size)

    def __start_crontab_task(self, kwargs: dict) -> None:
        '''

        :param kwargs:
        :return:
        '''
        kwargs.setdefault('tz', self.tzinfo)
        try:
            self.__crontab_start(**kwargs)
        except Exception as e:
            print_exc()
            raise e

    def __start__schedules_task(self, kwargs: dict) -> None:
        '''

        :param kwargs:
        :return:
        '''
        kwargs.setdefault('tz', self.tzinfo)
        try:
            self.__schedules_start(**kwargs)
        except Exception as e:
            print_exc()
            raise e

    def __run_tasks(self, task_fun, task_list, pool=None, is_async=False) -> None:
        '''

        :param task_fun:
        :param task_list:
        :param pool:
        :param is_async:
        :return:
        '''
        if self.pool is None:
            self.pool = self._get_pool()
        pool = self.pool
        if is_async:
            pool.map_async(task_fun, task_list).get()
        else:
            pool.map(task_fun, task_list)

    def __run_crontab(self) -> None:
        '''

        :return:
        '''
        while 1:
            if self.__stop == 1:
                break
            interval = 60 - datetime.now().second
            time.sleep(interval)
            crontab_tasks = self.conf.get(self.__key_crontab_tasks)
            if crontab_tasks:
                self.__task_assert((crontab_tasks, list), 0)
                Thread(
                    target=self.__run_tasks,
                    args=(self.__start_crontab_task, crontab_tasks),
                    kwargs={'is_async': True}, daemon=True
                ).start()

    def __run_schedule(self) -> None:
        '''
        :return:
        '''
        while 1:
            if self.__stop == 1:
                break
            interval = 1
            time.sleep(interval)
            schedule_tasks = self.conf.get(self.__key_schedule_tasks)
            if schedule_tasks:
                self.__task_assert((schedule_tasks, list), 0)
                Thread(
                    target=self.__run_tasks,
                    args=(self.__start__schedules_task, schedule_tasks),
                    kwargs={'is_async': True}, daemon=True
                ).start()

    def stop(self) -> None:
        '''
        :return:
        '''
        self.__stop = 1

    def start(self) -> None:
        '''
        :return:
        '''
        self.__stop = 0

    def run_loop(self) -> None:
        '''
        :return:
        '''
        date_time = self.get_date_time(self.tzinfo)
        msg = '[%s %s] %s start' % (self.tzinfo, date_time.strftime('%Y-%m-%d %H:%M:%S'), self.run_loop.__name__)
        print(msg)
        t_list = []
        t_list.append(Thread(target=self.__run_crontab))
        t_list.append(Thread(target=self.__run_schedule))
        for t in t_list:
            t.start()
        for t in t_list:
            t.join()
        date_time = self.get_date_time(self.tzinfo)
        msg = '[%s %s] %s exit' % (self.tzinfo, date_time.strftime('%Y-%m-%d %H:%M:%S'), self.run_loop.__name__)
        print(msg)

    def run(self) -> None:
        '''
        :return:
        '''
        date_time = self.get_date_time(self.tzinfo)
        msg = '[%s %s] %s start' % (self.tzinfo, date_time.strftime('%Y-%m-%d %H:%M:%S'), self.run.__name__)
        print(msg)
        t_list = []
        crontab_tasks = self.conf.get(self.__key_crontab_tasks)
        if crontab_tasks:
            t_list.append(
                Thread(
                    target=self.__run_tasks,
                    args=(self.__start_crontab_task, crontab_tasks)
                )
            )
        schedule_tasks = self.conf.get(self.__key_schedule_tasks)
        if schedule_tasks:
            t_list.append(
                Thread(
                    target=self.__run_tasks,
                    args=(self.__start__schedules_task, schedule_tasks)
                )
            )
        for t in t_list:
            t.start()
        for t in t_list:
            t.join()
        date_time = self.get_date_time(self.tzinfo)
        msg = '[%s %s] %s exit' % (self.tzinfo, date_time.strftime('%Y-%m-%d %H:%M:%S'), self.run.__name__)
        print(msg)


scheduler = Schedules()


def set_timezone(tz: str) -> None:
    '''

    :param tz:
    :return:
    '''
    return scheduler.set_timezone(tz)


def timezone_listing(country: str = None) -> list:
    '''
    :param country: a country code for example 'cn', 'us' or use self.timezon_countrys() got!
    if country is None return ALL
    :return: the country timezone city list, default cn
    '''
    return scheduler.timezone_listing(country)


def timezon_countrys() -> dict:
    ''':return countrys name dict'''
    return scheduler.timezon_countrys()


def set_tasks(tasks_conf: Dict[str, List[Dict[str, Any]]]) -> None:
    '''

    :param tasks_conf:
    :return:
    '''
    return scheduler.set_tasks(tasks_conf)


def add_task(t: Dict[str, dict]) -> None:
    '''
    :param t: {'crontab_tasks': {'crontab': '*/1 * * * *', 'shell': 'python tests.py'}}
            or {'schedule_tasks': {'crontab': '*/1 * * * * *', 'target': tests_run, args=(1,)}}
    :return:
    '''
    return scheduler.add_task(t)


def task(schedule: dict = None, crontab: str = None, args: tuple = None, kwargs: dict = None) -> Callable:
    '''

    :param schedule:
    :param crontab:
    :param args:
    :param kwargs:
    :return:
    '''
    return scheduler.task(schedule, crontab, args, kwargs)


def stop() -> None:
    '''

    :return:
    '''
    return scheduler.stop()


def start() -> None:
    '''

    :return:
    '''
    return scheduler.start()


def run_loop() -> None:
    '''

    :return:
    '''
    return scheduler.run_loop()


def run() -> None:
    '''

    :return:
    '''
    return scheduler.run()
