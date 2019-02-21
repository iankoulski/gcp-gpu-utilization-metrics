# How To Use It

This repository provides simple way to monitor GPU utilization on GCP

It is very simple to use, just run agent on each of your instance:

```bash
git clone https://github.com/b0noI/gcp-gpu-utilization-metrics.git
cd gcp-gpu-utilization-metrics
pip install -r ./requirenments.txt
python ./report_gpu_metrics.py &
```

This will auto create the metrics. But if you need to create metrics first run the following commands:

```bash
git clone https://github.com/b0noI/gcp-gpu-utilization-metrics.git
cd gcp-gpu-utilization-metrics
pip install -r ./requirenments.txt
GOOGLE_CLOUD_PROJECT=<ID> python ./create_gpu_metrics.py
```

# Environment settings

GOOGLE_CLOUD_PROJECT - used with create_gpu_metrics.py script. The report_gpu_metrics.py script gets project info from the instance metadata.

GPU_PRINT_LOGS - When True or Yes (case insensitive) the monitor will print metrics to stdout in addition to sending them to GCP, When False or No (case insensitive, default) the monitor will only send metrics to GCP

GPU_REPORTING_FREQUENCY - Seconds delay between subsequence metrics reports.

GPU_METRIC_SUFFIX - String (e.g. cluster name) to be appended to the reported metrics. This is useful when two clusters in the same project are doing reporting. Default is '', meaning use project wide metric names.

