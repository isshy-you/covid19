import os
import requests

class url_read:
    
    def url_read_csv(url):
        os.makedirs('database', exist_ok=True)
        urlData = requests.get(url).content
        filename = url.split('/')[-1]
        with open('database/'+filename ,mode='wb') as f:
            f.write(urlData)

    url_read_csv('https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv')
    url_read_csv('https://covid19.mhlw.go.jp/public/opendata/requiring_inpatient_care_etc_daily.csv')
    url_read_csv('https://covid19.mhlw.go.jp/public/opendata/deaths_cumulative_daily.csv')
    url_read_csv('https://covid19.mhlw.go.jp/public/opendata/severe_cases_daily.csv')
    url_read_csv('https://www.mhlw.go.jp/content/pcr_tested_daily.csv')
    url_read_csv('https://www.mhlw.go.jp/content/pcr_case_daily.csv')
    url_read_csv('https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_per_100_thousand_population_daily.csv')
    url_read_csv('https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_detail_weekly.csv')
    url_read_csv('https://www3.nhk.or.jp/n-data/opendata/coronavirus/nhk_news_covid19_prefectures_daily_data.csv')

if __name__ == "__main__":
    url_read()