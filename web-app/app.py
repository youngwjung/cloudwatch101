from flask import Flask
import psutil
import boto3
import datetime
import json
import time
import logging

logging.basicConfig(filename='app.log', format='%(levelname)s - %(message)s')

app = Flask(__name__)

@app.route('/')
def index():
    cpu_util = psutil.cpu_percent()
    mem_util = psutil.virtual_memory().percent

    read_io_before = psutil.disk_io_counters().read_count
    write_io_before = psutil.disk_io_counters().write_count

    time.sleep(1)

    read_io_after = psutil.disk_io_counters().read_count
    write_io_after = psutil.disk_io_counters().write_count

    read_io = read_io_after - read_io_before
    write_io = write_io_after - write_io_before

    rds_cpu_util = 0
    alert = False
    error_message = {}

    cw = boto3.resource('cloudwatch', region_name='ap-northeast-2')
    metric = cw.Metric('AWS/RDS', 'CPUUtilization').get_statistics(
        Dimensions=[
            {
                'Name' : 'DBInstanceIdentifier',
                'Value' : 'cw-postgres'
            }
        ],
        StartTime=datetime.datetime.utcnow() - datetime.timedelta(minutes=5),
        EndTime=datetime.datetime.utcnow(),
        Period=300,
        Statistics=['Average']
    )
    if metric['Datapoints']:
        rds_cpu_util = metric['Datapoints'][0]['Average']

    if cpu_util > 50:
        alert = True
        error_message['cpu_util'] = 'not ok'

    if mem_util > 50:
        alert = True
        error_message['mem_util'] = 'not ok'

    if read_io > 10:
        alert = True
        error_message['read_io'] = 'not ok'
        print (f'Read IO is {read_io}')

    if write_io > 10:
        alert = True
        error_message['write_io'] = 'not ok'
        print (f'Write IO is {write_io}')


    if rds_cpu_util > 50:
        alert = True
        error_message['rds_cpu_util'] = 'not ok'

    if alert:
        raise SystemError(json.dumps(error_message))
    else:
        return "OK"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)