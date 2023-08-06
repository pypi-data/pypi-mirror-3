# Slideshow Screensaver
# Copyright (C) 2012 James Adney
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import random
import mimetypes

class Pictures():

    def __init__(self, pics_root=os.path.expanduser("~/Pictures")):

        self.pics_root = pics_root

        self.generate_list()

    def generate_list(self):

        self.pics = []
        for d in os.walk(self.pics_root):
            directory = d[0]

            for filename in d[2]:
                filepath = os.path.join(directory, filename)
                if mimetypes.guess_type(filepath)[0] == 'image/jpeg':
                    self.pics.append(filepath)
        print "{0} pictures found".format(len(self.pics))

    def get_random(self):

        random_pic = random.choice(self.pics)
        return random_pic
