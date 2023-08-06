#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Gregory Sitnin <sitnin@gmail.com>"
__copyright__ = "WWPass Corporation, 2011"


def all():
    return {
        "ru_month": month,
        "ru_month_human": month_human,
    }


def month(month):
    months = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]
    return months[int(month) - 1]


def month_human(dt, year=False, day=False):
    months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    result = "%s" % months[dt.month - 1]
    result += "%d " % dt.day if day else ""
    result += " %d года" % dt.year if year else ""
    return result
