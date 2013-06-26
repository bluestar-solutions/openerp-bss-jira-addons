# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Bluestar Solutions Sàrl (<http://www.blues2.ch>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

def enum(**enums):
    return type('Enum', (), enums)

Direction = enum(FLOOR=-1, NEAR=0, CEIL=1)

def round_to(n, precision, direction=Direction.NEAR):
    correction = 0.0
    if direction == Direction.NEAR:
        correction = 0.5 if n >= 0 else -0.5
    elif direction == Direction.CEIL:
        if int(n/precision)*precision == n :
            return n
        correction = 1.0 if n >= 0 else -1.0
    return int(n/precision+correction)*precision

def round_to_05(n, direction=Direction.NEAR):
    return round_to(n, 0.05, direction)