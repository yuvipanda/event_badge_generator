#
#  Copyright (c) 2007 Silver Stripe Software Pvt Ltd
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#
#
#  Contributions and bug reports are welcome. Send an email to
#  siddharta at silverstripesoftware dot com
#

import Image, ImageDraw, ImageFont
from csvimport import CsvReader

class BadgeImage(object):
    def __init__(self, filename):
        self.img = Image.open(filename)
        self.draw = ImageDraw.Draw(self.img)
        self.width = int(self.img.size[0]*0.9)

    def drawAlignedText(self, pos, text, (font, color), xtransform, ytransform):
        width,height = font.getsize(text)
        xpos = xtransform(pos[0], width)
        ypos = ytransform(pos[1], height)
        self.draw.text((xpos, ypos), text, fill=color, font=font)

    def drawCenteredText(self, pos, text, font):
        self.drawAlignedText(pos, text, font, lambda x,w:x-w/2, lambda y,h:y-h/2)

    def getFitSize(self, startsize, text):
        size = startsize
        font = ImageFont.truetype("Trebucbd.ttf", size*300/72)
        textwidth, textheight = font.getsize(text)
        while textwidth > self.width:
            size -= 1
            font = ImageFont.truetype("Trebucbd.ttf", size*300/72)
            textwidth, textheight = font.getsize(text)
        return size

    def drawPerson(self, name):
        linepos = (self.img.size[0]/2, 240)
        line1pos = (self.img.size[0]/2, 150)
        line2pos = (self.img.size[0]/2, 320)
        size = self.getFitSize(45, name)
        if name.find(" ") >= 0:
            firstname, rest = name.split(" ", 1)
        else:
            firstname, rest = (name, "")
        if size < 45 and rest != "":
            personFont = ImageFont.truetype("Trebucbd.ttf", self.getFitSize(45, firstname)*300/72)
            self.drawCenteredText(line1pos, firstname, (personFont, "#ffffff"))
            personFont = ImageFont.truetype("Trebucbd.ttf", self.getFitSize(45, rest)*300/72)
            self.drawCenteredText(line2pos, rest, (personFont, "#ffffff"))
        else:
            personFont = ImageFont.truetype("Trebucbd.ttf", self.getFitSize(45, name)*300/72)
            self.drawCenteredText(linepos, name, (personFont, "#ffffff"))

    def drawCompany(self, name):
        pos = (self.img.size[0]/2, 500)
        font = ImageFont.truetype("Trebucbd.ttf", self.getFitSize(26, name)*300/72)
        self.drawCenteredText(pos, name, (font, "#0099ff"))

    def drawId(self, id):
        pos = (50, 50)
        font = ImageFont.truetype("Trebucbd.ttf", 8*300/72)
        self.drawCenteredText(pos, id, (font, "#ffffff"))

    def save(self, filename):
        newimg = Image.new("RGB", (self.img.size[0]*2+20, self.img.size[1]), "#000000")
        newimg.paste(self.img, (0,0))
        newimg.paste(self.img, (self.img.size[0]+20,0))
        newimg.save(filename)

class DataFileReader(object):
    def __init__(self, filename):
        fp = open(filename)
        self.content = fp.read()
        fp.close()

    def getData(self):
    reader = CsvReader(self.content)
    reader.setColumnAlias(0, "fname")
    reader.setColumnAlias(1, "lname")
    reader.setColumnAlias(2, "company")
    reader.setColumnAlias(3, "id")
    for row in reader.rows():
        name = row.fname + " " + row.lname
        company = row.company
        id = row.id
        name = name.title()
        # For company names that start with * we dont convert
        # to title case. This is helpful for acronym names.
        # Eg: IBM should not become Ibm, so we mark it as *IBM
        # in the file
        if not company.startswith("*"):
            company = company.title()
        else:
            # If name starts with * then remove the star and
            # take the rest as the company name
            company = company[1:]
        yield (id, name.title(), company)

import sys

if len(sys.argv) > 1:
    filenames = sys.argv[1:]
else:
    filenames = ["sample"]

count = 0
for filename in filenames:
    reader = DataFileReader(filename + ".csv")
    for id, name, company in reader.getData():
        print id, name, company
        badge = BadgeImage("badge_template.png")
        badge.drawPerson(name)
        badge.drawCompany(company)
        badge.drawId(id)
        badge.save(filename + "\\" + filename + "_badge_" + str(id) + ".png")
        count += 1
print "\n%d badges created" % (count)
