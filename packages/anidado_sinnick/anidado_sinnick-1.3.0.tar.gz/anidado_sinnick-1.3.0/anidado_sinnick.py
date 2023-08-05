#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Esto es el modulo "nested.py", y posee una funcion llamada print_lol() que
permite imprimir listas que tienen listas anidadas"""

def print_lol(the_list, indent=False, level=0):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end='')
            print(each_item)
