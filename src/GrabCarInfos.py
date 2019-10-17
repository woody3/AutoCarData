# -*- coding: utf-8 -*-
import os
import re
import json
import requests
from requests import ConnectionError, Timeout, ConnectTimeout
from lxml import etree
import time
from fake_useragent import UserAgent
from ExceptionHandler import AutoCarException


# 对爬取到数据重新编码，防止写入文件后出现乱码
def re_encode(param, coding_format="utf-8"):
    if isinstance(param, int):
        return str(param)
    elif param is None:
        return ""
    else:
        return param.encode(coding_format, "ignore")


# 断点续爬读取文件，运行异常时记录断点处数据
def channel_file_op(file_name, operator, data=""):
    path = os.path.abspath('..')
    file_path = os.path.join(path, 'infos', file_name)
    if "r" in operator:
        with open(file_path, mode=operator) as f:
            chnl_list = f.read().split(",")
            return [i for i in chnl_list if i != '']
    else:
        with open(file_path, mode=operator) as f:
            f.write(data)
            f.flush()


# 爬取的数据写入文件
def wrire_to_file(info_list, name, pattern_name, brand_name):
    path = os.path.abspath('../datas')
    file_name = "%s-%s.csv" % (brand_name.decode("utf-8"), pattern_name.decode("utf-8"))
    # file_path = os.path.join(path, "cars.csv")
    file_path = os.path.join(path, file_name)

    if os.path.exists(file_path):
        os.remove(file_path)
    if info_list:
        data = ""
        for i in xrange(len(info_list)):
            province = re_encode(info_list[i].get("dealerInfoBaseOut").get("provinceName"))
            city = re_encode(info_list[i].get("dealerInfoBaseOut").get("cityName"))
            county = re_encode(info_list[i].get("dealerInfoBaseOut").get("countyName"))
            # print info_list[i].get("dealerInfoBaseOut").get("address")
            address = re_encode(info_list[i].get("dealerInfoBaseOut").get("address"))
            dealer = re_encode(info_list[i].get("dealerInfoBaseOut").get("dealerName"))
            min_price = re_encode(info_list[i].get("minNewsPrice"))
            max_price = re_encode(info_list[i].get("maxOriginalPrice"))
            sell_phone = re_encode(info_list[i].get("dealerInfoBaseOut").get("sellPhone"))
            cellphone = re_encode(info_list[i].get("yphone"))

            # print brand_name, pattern_name, name, province, city, \
            #     county, address, dealer, min_price, max_price, sell_phone, cellphone
            if data == "":
                data = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                    brand_name, pattern_name, name, province, city, county, address, dealer, min_price, max_price,
                    sell_phone, cellphone)
            else:
                data = "%s%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                    data, brand_name, pattern_name, name, province, city, county, address, dealer, min_price, max_price,
                    sell_phone, cellphone)

        # print data
        with open(file_path, mode='a+') as f:
            f.write(data)


if __name__ == '__main__':

    headers = {"User-Agent": UserAgent().random}
    domain = "https://car.autohome.com.cn"
    start_url = "https://car.autohome.com.cn/AsLeftMenu/As_LeftListNew.ashx?typeId=1%20&brandId=0%20&fctId=0%20&seriesId=0"

    brand_list = (channel_file_op("brand_list.txt", "r"))
    pattern_list = (channel_file_op("pattern_list.txt", "r"))
    sub_list = (channel_file_op("sub_list.txt", "r"))
    sub_name_list = (channel_file_op("sub_name_list.txt", "r"))
    retry_times = 0
    if len(brand_list) == 0:
        brand_res_text = requests.get(start_url, headers=headers).text
        brand_text = brand_res_text.encode('unicode-escape').decode('string_escape')
        brand_list = re.findall(r"/price/brand-\d+.html", brand_text)
        brand_list.reverse()

    while len(brand_list) > 0:
        headers = {"User-Agent": UserAgent().random}
        brand = brand_list.pop()
        pattern_url = "%s%s" % (domain, brand)
        print "开始爬取:", pattern_url
        if retry_times > 5:
            raise AutoCarException("ConnectException : connect error or time out")
        try:
            response_data = requests.get(pattern_url, headers=headers)
            pattern_res_text = response_data.text
            if response_data.status_code >= 500:
                raise AutoCarException("ServerException : server is not available")
            elif response_data.status_code >= 400:
                raise AutoCarException("ClientRequestException : request error")
            pattern_text = pattern_res_text.encode('unicode-escape').decode('string_escape')
            if len(pattern_list) == 0:
                pattern_list = re.findall(r"/price/series-[0-9\-]*.html#pvareaid=2042205", pattern_text)
                pattern_list.reverse()

            while len(pattern_list) > 0:
                headers = {"User-Agent": UserAgent().random}
                pattern = pattern_list.pop()
                sub_url = "%s%s" % (domain, pattern)
                print "开始爬取:", sub_url
                if retry_times > 5:
                    raise AutoCarException("ConnectException : connect error or time out")
                try:
                    sub_response = requests.get(sub_url, headers=headers)
                    sub_res_text = sub_response.text
                    if response_data.status_code >= 500:
                        raise AutoCarException("ServerException : server is not available")
                    elif response_data.status_code >= 400:
                        raise AutoCarException("ClientRequestException : request error")
                    sub_text = sub_res_text.encode('unicode-escape').decode('string_escape')
                    tree = etree.HTML(sub_text)

                    pattern_name_init = tree.xpath("//div[@class='main-title']/a/text()")[0]
                    try:
                        pattern_name = pattern_name_init.decode('unicode_escape').encode("utf-8")
                    except ValueError as e:
                        pattern_name = pattern_name_init.encode("utf-8")
                    print "开始爬取车型：", pattern_name
                    # sub_list = re.findall(r"//www.autohome.com.cn/spec/\d+/#pvareaid=\d+", sub_text)
                    # sub_list = tree.xpath("//div[@id='divSeries']//div[@class='interval01-list-cars']//a/@href")
                    if len(sub_list) == 0:
                        sub_name_list = tree.xpath(
                            "//div[@id='divSeries']//div[@class='interval01-list-cars']//a/text()")
                        sub_list = tree.xpath(
                            "//div[@id='divSeries']//div[@class='interval01-list-cars']/../@data-value")
                        sub_name_list.reverse()
                        sub_list.reverse()
                    brand_name_init = tree.xpath("//div[@class='cartab-title']/h2/a/text()")[0]
                    brand_name = brand_name_init.decode('unicode_escape').encode("utf-8")

                    while len(sub_list) > 0:
                        car_no = sub_list.pop()
                        car_name_init = sub_name_list.pop()
                        if retry_times > 5:
                            raise AutoCarException("ConnectException : connect error or time out")

                        # 这里主要是处理不常见特殊的字符，比如德文字母，俄文字母，意大利文字母等等，unicode_escape出现转码错误后，
                        # 强制用utf-8转换成str类型，保证程序继续爬取运行
                        try:
                            car_name = car_name_init.decode('unicode_escape').encode("utf-8")
                        except ValueError as e:
                            car_name = car_name_init.encode("utf-8")
                        print "开始爬取款式：", car_name
                        # pageSize参数最大只能是30，经测试，设置的值超过30都默认是10
                        init_url = "https://dealer.autohome.com.cn/handler/other/getdata?__action=dealerlq.getdealerlistspec&provinceId=0&cityId=0&countyId=0&pageSize=30&specId=%s" % car_no
                        headers = {"User-Agent": UserAgent().random}
                        data = {}
                        try:
                            data_response = requests.get(init_url, headers=headers)
                            data_res = data_response.text
                            if response_data.status_code >= 500:
                                raise AutoCarException("ServerException : server is not available")
                            elif response_data.status_code >= 400:
                                raise AutoCarException("ClientRequestException : request error")
                            init_data = json.loads(data_res)
                            pages = 0
                            info_list = []

                            if init_data.get("result"):
                                pages = init_data.get("result").get("pagecount")
                                info_list = init_data.get("result").get("list")
                                if pages == 0:
                                    print "正在爬取的 %s => %s => %s 暂无经销商报价" % (brand_name, pattern_name, car_name)
                                    continue
                            else:
                                continue

                            print "正在爬取: %s => %s => %s, 共%d页，当前爬取第%d页" % \
                                  (brand_name, pattern_name, car_name, pages, 1)

                            if pages > 1:
                                for page in xrange(pages - 1):
                                    print "正在爬取: %s => %s => %s , 共%d页，当前爬取第%d页" % \
                                          (brand_name, pattern_name, car_name, pages, page + 2)
                                    request_url = "%s&pageIndex=%s" % (init_url, str(page + 2))
                                    headers = {"User-Agent": UserAgent().random}
                                    data_re_son = requests.get(request_url, headers=headers)
                                    time.sleep(0.5)  # 反防爬，每次请求后休眠500ms
                                    data_re = data_re_son.text
                                    if data_re_son.status_code >= 400:
                                        raise RuntimeError
                                    data = json.loads(data_re)
                                    info_list.extend(data.get("result").get("list"))

                            wrire_to_file(info_list, car_name, pattern_name, brand_name)

                        except(ConnectionError, Timeout, ConnectTimeout) as expt:
                            sub_list.append(car_no)
                            sub_name_list.append(car_name_init)
                            retry_times += 1
                            sleep(3) #休眠3秒后再尝试连接
                            print "连接错误，开始重试"
                        except SyntaxError as expt:
                            print "出现编码转换错误:", expt
                            miss_sub = "丢失爬取的款式详情：%s => %s => %s-%s" % (brand_name, pattern_name, car_name_init, car_no)
                            channel_file_op("missing_info.txt", "a", miss_sub)
                        except Exception as expt:
                            sub_list.append(car_no)
                            sub_name_list.append(car_name_init)
                            channel_file_op("sub_list.txt", "w", ",".join(sub_list))
                            channel_file_op("sub_name_list.txt", "w", ",".join(sub_name_list))
                            print "汽车款式爬取过程中出错，错误详情：", expt
                            raise expt
                except (ConnectionError, Timeout, ConnectTimeout) as ex:
                    pattern_list.append(pattern)
                    retry_times += 1
                    sleep(3) #休眠3秒后再尝试连接
                    print "连接错误，开始重试"
                except (SyntaxError, ValueError) as ex:
                    print "出现编码转换错误:", ex
                    miss_pattern = "丢失爬取的车型链接：%s" % pattern
                    channel_file_op("missing_info.txt", "a", miss_pattern)
                except Exception as ex:
                    pattern_list.append(pattern)
                    channel_file_op("pattern_list.txt", "w", ",".join(pattern_list))
                    print "汽车车型爬取过程中出错,错误详情：", ex
                    raise ex
        except (ConnectionError, Timeout, ConnectTimeout) as e:
            brand_list.append(brand)
            retry_times += 1
            sleep(3) #休眠3秒后再尝试连接
            print "连接错误，开始重试"
        except (SyntaxError, ValueError) as e:
            print "出现编码转换错误:", e
            miss_brand = "丢失爬取的品牌链接：%s" % brand
            channel_file_op("missing_info.txt", "a", miss_brand)
        except Exception as e:
            brand_list.append(brand)
            channel_file_op("brand_list.txt", "a", ",".join(brand_list))
            print "汽车品牌爬取过程中出错,错误详情：", e
            raise e

    # 程序正常退出时，需要清空断点相关的文件
    channel_file_op("brand_list.txt", "w")
    channel_file_op("pattern_list.txt", "w")
    channel_file_op("sub_name_list.txt", "w")
    channel_file_op("sub_list.txt", "w")
