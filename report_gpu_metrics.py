import time
import socket
import subprocess
import requests
import csv
import os
from time import gmtime, strftime
import sys

from google.cloud import monitoring_v3


metadata_server = "http://metadata/computeMetadata/v1/instance/"
metadata_flavor = {'Metadata-Flavor' : 'Google'}
data = requests.get(metadata_server + 'zone', headers = metadata_flavor).text
zone = data.split("/")[3]
project_id = data.split("/")[1]

client = monitoring_v3.MetricServiceClient()
project_name = client.project_path(project_id)
instance_id = requests.get(metadata_server + 'id', headers = metadata_flavor).text

printLogs=False
envPrintLogs = str(os.environ.get('GPU_PRINT_LOGS', 'False')).lower()
if envPrintLogs == 'true' or envPrintLogs == 'yes':
    printLogs=True

def report_metric(value, type, instance_id, zone, project_id):
    series = monitoring_v3.types.TimeSeries()
    series.metric.type = 'custom.googleapis.com/{type}'.format(type=type)
    series.resource.type = 'gce_instance'
    series.resource.labels['instance_id'] = instance_id
    series.resource.labels['zone'] = zone
    series.resource.labels['project_id'] = project_id
    point = series.points.add()
    point.value.int64_value = value
    now = time.time()
    point.interval.end_time.seconds = int(now)
    point.interval.end_time.nanos = int(
        (now - point.interval.end_time.seconds) * 10**9)
    client.create_time_series(project_name, [series])


def get_nvidia_smi_utilization(gpu_query_name):
    csv_file_path = "/tmp/gpu_utilization.csv"
    usage = 0
    length = 0
    subprocess.check_call(["/bin/bash", "-c",
                           "nvidia-smi --query-gpu={query_name} -u --format=csv"
                           " > {csv_file_path}".format(
                               query_name=gpu_query_name,
                               csv_file_path=csv_file_path)])
    with open(csv_file_path) as csvfile:
        utilizations = csv.reader(csvfile, delimiter=' ')
        for row in utilizations:
            length += 1
            if printLogs:
                print(str(row))
            if length > 1:
                usage += int(row[0])
        averageUtilization = int(usage / (length - 1))
        if printLogs:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' GMT, Average: ' + str(averageUtilization))
            sys.stdout.flush()
    return averageUtilization


def get_gpu_utilization():
    return get_nvidia_smi_utilization("utilization.gpu")


def get_gpu_memory_utilization():
    return get_nvidia_smi_utilization("utilization.memory")


gpu_metric_suffix = str(os.environ.get('GPU_METRIC_SUFFIX', ''))
GPU_UTILIZATION_METRIC_NAME = "gpu_utilization" + gpu_metric_suffix
GPU_MEMORY_UTILIZATION_METRIC_NAME = "gpu_memory_utilization" + gpu_metric_suffix

GPU_REPORTING_FREQUENCY = 60
freq = str(os.environ.get('GPU_REPORTING_FREQUENCY', ''))
# Note: Use isdigit() with Python2.x and isnumeric() with Python3.x
if freq.isdigit():
  GPU_REPORTING_FREQUENCY = int(freq)

while True:
  report_metric(get_gpu_utilization(),
                GPU_UTILIZATION_METRIC_NAME,
                instance_id,
                zone,
                project_id)
  report_metric(get_gpu_memory_utilization(),
                GPU_MEMORY_UTILIZATION_METRIC_NAME,
                instance_id,
                zone,
                project_id)
  time.sleep(GPU_REPORTING_FREQUENCY)
