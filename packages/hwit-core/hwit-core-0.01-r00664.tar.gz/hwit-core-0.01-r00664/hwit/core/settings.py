#!/usr/bin/env python
#    -*-    encoding: UTF-8    -*-

#   copyright 2009 D Haynes
#
#   This file is part of the HWIT distribution.
#
#   HWIT is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   HWIT is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with HWIT.  If not, see <http://www.gnu.org/licenses/>.

tones = {
"aluminium": [
(int("ee",16),int("ee",16),int("ec",16)),   #eeeeec
(int("d3",16),int("d7",16),int("cf",16)), 	#d3d7cf
(int("ba",16),int("bd",16),int("b6",16))], 	#babdb6

"butter": [
(int("fc",16),int("e9",16),int("4f",16)),   #fce94f
(int("ed",16),int("d4",16),int("00",16)), 	#edd400
(int("c4",16),int("a0",16),int("00",16))], 	#c4a000

"chameleon": [
(int("8a",16),int("e2",16),int("34",16)),   #8ae234
(int("73",16),int("d2",16),int("16",16)), 	#73d216
(int("4e",16),int("9a",16),int("06",16))], 	#4e9a06

"orange": [
(int("fc",16),int("af",16),int("3e",16)),   #fcaf3e
(int("f5",16),int("79",16),int("00",16)), 	#f57900
(int("ce",16),int("5c",16),int("00",16))], 	#ce5c00

"chocolate": [
(int("e9",16),int("b9",16),int("6e",16)),   #e9b96e
(int("c1",16),int("7d",16),int("11",16)), 	#c17d11
(int("8f",16),int("59",16),int("02",16))], 	#8f5902

"sky_blue": [
(int("72",16),int("9f",16),int("cf",16)),   #729fcf
(int("34",16),int("65",16),int("a4",16)), 	#3465a4
(int("20",16),int("4a",16),int("87",16))], 	#204a87

"plum": [
(int("ad",16),int("7f",16),int("a8",16)),   #ad7fa8
(int("75",16),int("50",16),int("7b",16)), 	#75507b
(int("5c",16),int("35",16),int("66",16))], 	#5c3566

"slate": [
(int("88",16),int("8a",16),int("85",16)),   #888a85
(int("55",16),int("57",16),int("53",16)), 	#555753
(int("2e",16),int("34",16),int("36",16))], 	#2e3436

"scarlet_red": [
(int("ef",16),int("29",16),int("29",16)),   #ef2929
(int("cc",16),int("00",16),int("00",16)), 	#cc0000
(int("a4",16),int("00",16),int("00",16))]	#a40000 

}

style = """
@media all {
body {
color:#2e3436; /* slate */
}

h1,h2,h3,h4,h5,h6 {
color:#888a85; /* slate */
font-family: helvetica, arial, sans-serif;
}

div.hwit_group {
padding:16px;
border:2px dotted #babdb6; /* aluminium */
}

div.hwit_group p {
margin-right:2em;
padding:20px 20px 20px 20px;
background-color:#fce94c; /* butter */
border-top: 1px dotted #edd400; /* butter */
border-left: 2px solid #c4a000; /* butter */
border-bottom: 3px solid #edd400; /* butter */
}

div.hwit_group dt{
font-weight:bold;
margin:6px 0px 0px 0px;
}

div.hwit_group dd{
width:60%;
height:1.6em;
margin:6px 0px 6px 0px;
}

div.hwit_group dd[hwit_edit=true] {
border:1px solid #babdb6; /* aluminium */
background-color: white;
}

div.hwit_group dd[hwit_fill=true] {
border:1px solid #ef2929; /* scarlet red */
}

div.hwit_group dd[hwit_fill=true]:before {
content:"* ";
color:#ef2929; /* scarlet red */
}

div.hwit_group dd[hwit_check] {
border-right:8px solid #8ae234; /* chameleon */
}

/* Tooltip */
div.hwit_group a.hwit_tip {
position:relative;
text-decoration:none;
padding:0.1em 0.3em 0.1em 0.3em;
border:2px solid #204a87; /* sky blue */
background-color:#729fcf; /* sky blue */
}

div.hwit_group a.hwit_tip:before {
content:"i";
color:white;
font-weight:bold;
font-family: serif;
}

div.hwit_group a.hwit_tip span {
display:none;
}

div.hwit_group a.hwit_tip:hover span {
display:inline;
position:absolute;
top:0.2em;
left:0.5em;
padding:0.2em 0.6em;
border:1px solid #204a87; /* sky blue */
background-color:#729fcf; /* sky blue */
color:white;
}
}

@media screen {
div.hwit_group p {
position:absolute;
right:0;
width:30%;}
}
"""

def htmlTone(name, shade = 1):
    return "#%s" % ''.join(
    ["%02x" % i for i in tones.get(name,"slate")[shade % 3]])

if __name__ == "__main__":
    for k in tones:
        for i,s in enumerate(("light","mid","shaded")):
            print "%s\t%s\t%s" % (s, k, htmlTone(k,i))

