#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import os
import gzip
import re
import statistics
import logging
import sys
from collections import namedtuple
import json
import argparse

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "DEBUG": False,
    "LOG_FILE": None
}
pattern_for_log_filename = r'nginx-access-ui.log-(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})(?P<extension>\.gz)*$'
logging.basicConfig(format='[%(asctime)s] %(levelname).1s %(message)s',
                    datefmt='%Y.%m.%d%H:%M:%S',
                    level=logging.DEBUG,
                    filename=config['LOG_FILE'])


def find_latest_log(path, pattern=pattern_for_log_filename):
    # if we have plane and .gz we would prefer plane
    for file in sorted(os.listdir(path), key=lambda item: item + '_', reverse=True):
        lst = ['path', 'date', 'extension']
        Result = namedtuple('Result', lst)

        z = re.match(pattern, file)
        if z:
            date, extension = f"{z.group('year')}.{z.group('month')}.{z.group('day')}", z.group('extension')
            return Result(os.path.join(path, file), date, extension)
    return Result(None, None, None)


def gen_parsed_log(pattern: str, lines):
    patc = re.compile(pattern)
    for line in lines:
        line = line.decode('utf-8').strip()
        if patc.match(line):
            yield {'url': patc.match(line).group('url'),
                   'request_time': float(patc.match(line).group('request_time')),
                   'parsed': True}
        else:
            yield {'log': line,
                   'parsed': False}


def make_report(logs, rep_name, config, threshold=50):
    parsed = 0
    unparsed = 0
    total_time = 0
    rep = dict()

    header = ['url',
              'count',
              'count_perc',
              'time_sum',
              'time_perc',
              'time_avg',
              'time_max',
              'time_med']

    for log in logs:
        if log['parsed']:
            parsed += 1

            total_time += log['request_time']
            if log['url'] in rep.keys():
                rep[log['url']].append(log['request_time'])
            else:
                rep[log['url']] = [log['request_time']]
        else:
            unparsed += 1
            if config['DEBUG']:
                logging.debug(f"Cannot parse the log entry: {log['log']}")

    unparsed_perc = unparsed / (parsed + unparsed) * 100
    logging.info(f'{unparsed_perc}% unparsed logs')

    if unparsed_perc > threshold:
        # parsing error
        raise SystemExit("Too many unparsed logs.")

    # count metrics
    data = [dict(zip(header, [i,
                              len(rep[i]),
                              len(rep[i]) / parsed * 100,
                              sum(rep[i]),
                              sum(rep[i]) / total_time * 100,
                              statistics.mean(rep[i]),
                              max(rep[i]),
                              statistics.median(rep[i])])) for i in rep]

    # get urls with the highest summary request time
    data = sorted(data, reverse=True, key=lambda item: item['time_sum'])[:config['REPORT_SIZE']]

    # read template
    with open('report.html', 'r') as f:
        page = f.read()
        page = page.replace('$table_json', str(data))

    # write report
    with open(rep_name, 'w') as f:
        f.write(page)
        logging.info('Done')


def merge_config(external_config, internal_config=config):
    def get_external_config(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.info(f"The config file '{path}' not found")
            sys.exit()
        except json.decoder.JSONDecodeError:
            logging.info(f"Cannot parse the config file '{path}'")
            sys.exit()

    res = internal_config.copy()
    if external_config is not None:
        res.update(external_config)
    return res


def main():
    parser = argparse.ArgumentParser(description='Generate report')
    parser.add_argument('--config', dest='config', type=str, nargs='?', required=False)
    args = parser.parse_args()

    full_config = merge_config(args.config)

    # from now, we have config, so let's update logging
    logging.basicConfig(format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d%H:%M:%S',
                        level=logging.DEBUG,
                        filename=full_config['LOG_FILE'],
                        force=True)

    data = find_latest_log(full_config['LOG_DIR'])

    if not data.path:
        logging.info('No logs to parse.')
        sys.exit()

    rep_full_path = os.path.join(full_config['REPORT_DIR'], f'report-{data.date}.html')
    if not os.path.exists(rep_full_path):
        with gzip.open(data.path, 'rb') if data.extension else \
                open(data.path, 'rb') as f:
            pattern = r'(\d+\.\d+\.\d+\.\d+)\s+(\w+|\-)\s+(\w+|\-)\s+\[(.*)\]\s+\"(\w+)\s+' \
                      r'(?P<url>.*?)\s+(.*?)\"\s+(.*)\s+(?P<request_time>[0-9]+\.?[0-9]+)$'
            logs = gen_parsed_log(pattern, f)
            make_report(logs, rep_full_path, config=full_config)
    else:
        logging.info('The report has already been created. Skipping...')


if __name__ == '__main__':
    try:
        main()
    except SystemExit as e:
        logging.exception(e)
    except:
        logging.exception('Something wrong...')
