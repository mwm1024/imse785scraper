# IMSE785
# KANSAS STATE UNIVERSITY

import argparse
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as BS
from datetime import datetime as dt, timedelta
import csv
from os import path


def get_weather_data(zipcode, date):
    url = 'https://www.almanac.com/weather/history/zipcode/%s/%s' % (zipcode, date)
    print(url + '\n-------')
    weather_data = {'Date': date}
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(req).read()
    except HTTPError as err:
        if err.code == 429:
            print('⚠️ HTTP Error 429, ',
                  f'please retry after {err.hdrs["Retry-After"]} seconds.')
        else:
            raise(err)
    else:
        soup = BS(page, 'html.parser')
        title = soup.find(id='page-title').string.strip() + ', %s:' % date
        print(title)
        data_blocks = soup.find_all(attrs={'class':'weatherhistory_results_datavalue'})
        if len(data_blocks):
            for block in data_blocks:
                print(block.h3.string, block.contents[1].p.get_text())
                weather_data[block.h3.string] = block.contents[1].p.contents[0].string
        else:
            print('* Failed to load data.')
    finally:
        print('\n')
    return weather_data


def collect_weather_data(zipcode, date, days):
    start = dt.strptime(date, '%Y-%m-%d')
    end = start + timedelta(days=days)
    if start >= end:
        start, end = end, start
        days = abs(days - 1)
    print('Collecting weather data for zip code: %s, between dates: %s and %s...'
        % (zipcode, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))

    dates = [dt.strftime(start + timedelta(days=x), "%Y-%m-%d") for x in range(0, days)]
    weather_data_list = []
    for date in dates:
        weather_data = get_weather_data(zipcode, date)
        if len(weather_data) > 1:
            weather_data_list.append(weather_data if weather_data else {'Date': date})
        else:
            break
    return weather_data_list


def write_to_csv(output, contents_list):
    try:
        file_action = 'w'
        if path.isfile(output):
            choice = input('File exists! Overwrite(W) or Append(A): ')
            if choice.lower() in ('w', 'a'):
                file_action = choice.lower()
            else:
                exit('Cancelled.')
        with open(output, file_action, newline='') as fp:
            csv_writer = csv.DictWriter(fp, fieldnames=contents_list[0].keys())
            if file_action == 'w':
                csv_writer.writeheader()
            for row in contents_list:
                csv_writer.writerow(row)
        print("%d rows written to %s." % (len(contents_list), output))
    except:
        raise(IOError)
    finally:
        print('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('zipcode', help='Specify 5-digit zip code, e.g. 66506')
    parser.add_argument('date', help='Specify date in ISO 8601 format YYYY-MM-DD, e.g. 2015-01-01')
    parser.add_argument('-d', '--days', type=int, help='Specify number of days to check after the DATE, e.g. 30')
    parser.add_argument('-o', '--output', help='Specify file path to save output csv file, e.g. output.csv')
    args = parser.parse_args()
    if args.zipcode and args.date:
        try:
            dt.strptime(args.date, '%Y-%m-%d')
        except ValueError as e:
            print('Invalid date: ', args.date)
        else:
            if args.days is not None:
                weather_data_list = collect_weather_data(args.zipcode, args.date, args.days)
            else:
                weather_data_list = [get_weather_data(args.zipcode, args.date)]
            if args.output:
                write_to_csv(args.output, weather_data_list)
    else:
        print(parse.print_help())


if __name__ == '__main__':
    main()
