# Name:      lokai/lk_login/newpass.py
# Purpose:   Generate a random pass phrase
# Copyright: 2011: Database Associates Ltd.
#
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
#    See the License for the specific language governing permissions and
#    limitations under the License.

#-----------------------------------------------------------------------

import sys
import string
import random

#-----------------------------------------------------------------------

random.seed()

def make_password(out_len):
    letter_set=string.letters+string.digits
    r_letter_set=[' ']*len(letter_set)
    for i in range(len(letter_set)):
        r_letter_set[i]=letter_set[i]

    random.shuffle(r_letter_set)
    out = ''
    for i in range(out_len):
        out=out+random.choice(r_letter_set)
    return out

if __name__ == "__main__":
    if len(sys.argv) <> 2:
        print "Usage: %s length"%sys.argv[0]
        print "          length = the number of characters for the password"
    else:
        try:
            out_len = int(eval(sys.argv[1]))
        except:
            print "Given lenght must be a number"
            out_len = 0
        if out_len > 0:
            out = make_password(out_len)
            print out

#-----------------------------------------------------------------------
