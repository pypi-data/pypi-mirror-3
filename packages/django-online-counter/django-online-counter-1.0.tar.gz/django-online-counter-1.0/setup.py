#-*- coding:utf-8 -*-

#Copyright (C) 2011, Metehan Özbek
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

setup(
    name = "django-online-counter",
    packages = find_packages(),
    package_data = {"onlinecounter.demo" : ["templates/*"]},
    version = "1.0",
    license = "GPL v3",
    description = "Django online visitor counter",
    author = u"Metehan Özbek",
    author_email = "metehan[at]metehan.us",
    url = "http://www.metehan.us/",
    download_url = "",
    keywords = ["django","online counter"],
    classifiers = [
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Environment :: Web Environment",
        "Framework :: Django"
    ],
)