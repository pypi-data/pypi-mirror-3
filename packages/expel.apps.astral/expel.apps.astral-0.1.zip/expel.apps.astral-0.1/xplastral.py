# Copyright (c) 2009-2011 Simon Kennedy <code@sffjunkie.co.uk>.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import datetime
from optparse import OptionGroup

from expel.lib.looper import xPLLooper
from expel.message.xpl import xPLMessage, xPLTrigger

from astral import Astral, City

__all__ = ['xPLAstral']

DEFAULT_CITY = 'London'

class xPLAstral(xPLLooper):
    """xPL Astral"""
    
    MODE_ASTRAL = 'astral'
    MODE_DAWNDUSK = 'dawndusk'
    
    EVENT_DAWN = 0
    EVENT_SUNRISE = 1
    EVENT_NOON = 2
    EVENT_SUNSET = 3
    EVENT_DUSK = 4
    EVENT_RAHUKAALAM_START = 5
    EVENT_RAHUKAALAM_END = 6
    
    def __init__(self):
        xPLLooper.__init__(self)

        self.vendor = 'sffj'
        self.device = 'astral'
        self.title = 'xPL Astral'
        
        self._first_pass = True

        self.MessageReceived += self.message_received
        self.ConfigChanged += self.config_changed
        self.StateChanged += self.state_changed

    def state_changed(self, *args, **kwargs):
        if args[1] == xPLLooper.PROBE_FOR_HUB:
            self.reactor.call_later(0.1, self._loop)
        
    def add_options(self, parser):
        astral_opt = OptionGroup(parser, "%s options" % self.title)
        astral_opt.add_option("-s", "--schema", dest="schema",
            choices=(xPLAstral.MODE_DAWNDUSK, xPLAstral.MODE_ASTRAL),
            default=xPLAstral.MODE_DAWNDUSK,
            help="Select schema to output either 'dawndusk' or 'astral'.", 
            metavar='SCHEMA')
            
        astral_opt.add_option("-c", "--city", dest="city_name",
            default='',
            help="Select CITY to emit times for.", metavar='CITY')
    
        astral_opt.add_option("-l", "--list",
            dest="list_cities", action='store_true', default=False,
            help="Show list of cities.")
    
        astral_opt.add_option("-t", "--time",
            dest="show_times", action='store_true', default=False,
            help="Show the times of the sun.")

        parser.add_option_group(astral_opt)

    def configure(self):
        if self.options.list_cities == True:
            astral = Astral()
            text = ''
            cities = sorted(astral.cities)
            for city in cities:
                text += '%s, ' % city
            text = text[:-2]
            print(text)
            sys.exit()
            
        if self.options.show_times == True:
            astral = Astral()
            city = astral[self.options.city]
            sun = city.sun()
            print('Times calculated for %s' % self.options.city)
            print('Dawn:    %s' % sun['dawn'])
            print('Sunrise: %s' % sun['sunrise'])
            print('Noon:    %s' % sun['noon'])
            print('Sunset:  %s' % sun['sunset'])
            print('Dusk:    %s' % sun['dusk'])
            sys.exit()

        self.schema = self.options.schema
        self._astral = Astral()
        
        if self.options.city_name != '':
            try:
                self.city = self._astral[self.options.city_name]
                self.config['city'] = self.options.city_name
            except KeyError:
                self.logger.error('%s: Unknown city \'%s\' specified' % \
                    (self.title, self.options.city_name))
                sys.exit()
        else:
            city_name = self.config['city'].value
            if len(city_name) == 0:
                self.city = self._astral[DEFAULT_CITY]
            else:
                try:
                    country = self.config['country'].value
                    if country != '':
                        city_name += ',%s' % country
                    self.city = self._astral[city_name]
                except KeyError:
                    country = ''
                
                try:
                    latitude = self.config['latitude'].value
                    longitude = self.config['longitude'].value
                    timezone = self.config['timezone'].value
                except:
                    latitude = ''
                    longitude = ''
                    timezone = 'UTC'
            
                if country != '' and latitude != '' and longitude != '' and timezone != '':
                    try:
                        self.city = City([city_name, country, latitude,
                            longitude, timezone])
                    except:
                        self.city = self._astral[DEFAULT_CITY]
                else:
                    self.city = self._astral[city_name]
        
        try:
            self.logger.info('%s: Times calculated for %s, %s' % (self.title,
                self.city.name, self.city.country))
            self._new_day()
        except:
            self.logger.error('%s: Sun does not rise and set today, at this location' % \
                self.title)
            sys.exit()

    def message_received(self, msg, *args, **kwargs):
        msg_type = msg.message_type.lower()
        schema_class = msg.schema_class.lower()
        schema_type = msg.schema_type.lower()

        if msg_type == 'cmnd' and (schema_class == 'dawndusk' or \
                                   schema_class == 'astral') and schema_type == 'request':
            command = msg.get('command', '').strip().lower()
            query = msg.get('query', '').strip().lower()
            
            if command == 'status' and query == 'daynight':
                msg_raw = xPLMessage.XPL_STAT_RAW % self.looper.source
                msg_raw = msg_raw + '%s.basic\n{\n' % schema_class
                
                now = datetime.datetime.now(self._city.tz).time()
                    
                if now >= self._sun['dusk'].time():
                    msg_raw += 'status=night\n'
                elif now >= self._sun['dawn'].time():
                    msg_raw += 'status=day\n'
                
                msg_raw = msg_raw + '}\n'
                
                self.broadcast_message(msg_raw)

    def config_changed(self, msg, *args, **kwargs):
        city = self.config['city'].value
        country = self.config['country'].value
        
        if country != '':
            full_name = '%s, %s' % (city, country)
        else:
            full_name = city
            
        longitude = self.config['longitude'].value
        if longitude == '':
            longitude = 0.0
        else:
            longitude = float(longitude)
            
        latitude = self.config['latitude'].value
        if latitude == '':
            latitude = 0.0
        else:
            latitude = float(latitude)
            
        timezone = self.config['timezone'].value
        
        c = None
        try:
            c = self._astral[full_name]
            city = c.name
            country = c.country
        except:
            info = (city, country, latitude, longitude, timezone)
            c = City(info)

        if c is not None:
            self.logger.info('%s: Times re-calculated for %s, %s' % (self.title,
                                                                     city, country))
            self.city = c
            self._new_day()
            self._first_pass = True
        
    def _loop(self):
        first_pass = self._first_pass
        if self._first_pass:
            self._first_pass = False

        now = datetime.datetime.now(self.city.tz)
            
        if self._event_status[xPLAstral.EVENT_DAWN] == False and \
        now >= self._sun['dawn']:
            if not first_pass:
                self.logger.info('%s: Dawn Event at %s' % (self.title, now))
                self._send_msg(xPLAstral.EVENT_DAWN)
            self._event_status[xPLAstral.EVENT_DAWN] = True
            
        if self._event_status[xPLAstral.EVENT_SUNRISE] == False and \
        now >= self._sun['sunrise']:
            if not first_pass:
                self.logger.info('%s: Sunrise Event at %s' % (self.title, now))
                self._send_msg(xPLAstral.EVENT_SUNRISE)
            self._event_status[xPLAstral.EVENT_SUNRISE] = True
            
        if self._event_status[xPLAstral.EVENT_NOON] == False and \
        now >= self._sun['noon']:
            if not first_pass:
                self.logger.info('%s: Noon Event at %s' % (self.title, now))
                self._send_msg(xPLAstral.EVENT_NOON)
            self._event_status[xPLAstral.EVENT_NOON] = True

        if self._event_status[xPLAstral.EVENT_SUNSET] == False and \
        now >= self._sun['sunset']:
            if not first_pass:
                self.logger.info('%s: Sunset Event at %s' % (self.title, now))
                self._send_msg(xPLAstral.EVENT_SUNSET)
            self._event_status[xPLAstral.EVENT_SUNSET] = True

        if self._event_status[xPLAstral.EVENT_DUSK] == False and \
        now >= self._sun['dusk']:
            if not first_pass:
                self.logger.info('%s: Dusk Event at %s' % (self.title, now))
                self._send_msg(xPLAstral.EVENT_DUSK)
            self._event_status[xPLAstral.EVENT_DUSK] = True
        
        date = now.date()
        if date > self._date:
            self._new_day()

        self.reactor.call_later(10, self._loop)

    def _new_day(self):
        self._sun = self.city.sun(local=True)
        self._date = datetime.date.today()
        self._event_status = [False, False, False, False, False, False, False]

        self.logger.info('%s: Dawn:    %s' % (self.title, self._sun['dawn']))
        
        if self.schema == xPLAstral.MODE_ASTRAL:
            self.logger.info('%s: Sunrise: %s' % (self.title, self._sun['sunrise']))
            self.logger.info('%s: Noon:    %s' % (self.title, self._sun['noon']))
            self.logger.info('%s: Sunset:  %s' % (self.title, self._sun['sunset']))
            
        self.logger.info('%s: Dusk:    %s' % (self.title, self._sun['dusk']))

    def _send_msg(self, event):
        msg = None
        if self.schema == xPLAstral.MODE_DAWNDUSK and \
            (event == xPLAstral.EVENT_DAWN or event == xPLAstral.EVENT_DUSK):
                
            msg = self._dawndusk_message(event)

        elif self.schema == xPLAstral.MODE_ASTRAL:
            msg = self._astral_message(event)

        if msg is not None:
            self.broadcast_message(msg)

    def _dawndusk_message(self, event):
        msg = xPLTrigger(self.source)
        msg.schema_class = 'dawndusk'
        msg.schema_type = 'basic'
        msg['type'] = 'dawndusk'
        
        if event == xPLAstral.EVENT_DAWN:
            msg['status'] = 'dawn' 
        elif event == xPLAstral.EVENT_DUSK:
            msg['status'] = 'dusk' 
        
        return msg

    def _astral_message(self, event):
        msg = xPLTrigger(self.source)
        msg.schema_class = 'astral'
        msg.schema_type = 'basic'
        msg['type'] = 'astral'
        
        if event == xPLAstral.EVENT_DAWN:
            msg['status'] = 'dawn' 
        elif event == xPLAstral.EVENT_SUNRISE:
            msg['status'] = 'sunrise' 
        elif event == xPLAstral.EVENT_NOON:
            msg['status'] = 'noon' 
        elif event == xPLAstral.EVENT_SUNSET:
            msg['status'] = 'sunset' 
        elif event == xPLAstral.EVENT_DUSK:
            msg['status'] = 'dusk' 
        elif event == xPLAstral.EVENT_RAHUKAALAM_START:
            msg['status'] = 'rahukaalam_start' 
        elif event == xPLAstral.EVENT_RAHUKAALAM_END:
            msg['status'] = 'rahukaalam_end' 
        
        return msg

if __name__ == '__main__':
    x = xPLAstral()
    x()
