# -*- coding: utf-8 -*-
'''
Created on Tue 16 Aug 2011

@author: leewei
'''
# ==============================================================================
# Copyright© 2011 LShift - Lee Wei <leewei@lshift.net>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from __future__  import with_statement
from trac.ticket import Ticket
import random
import time
import datetime
# 0.12 stores timestamps in microseconds
from trac.util.datefmt import utc
try:
    from trac.util.datefmt import from_utimestamp as from_timestamp
except ImportError:
    def from_timestamp(ts):
        return datetime.fromtimestamp(ts, utc)

# globals
today        = datetime.date.today()
this_day     = today.day

def day_to_epoch(day=this_day):
    """
        Given specific day (2011-08-dd 11:34:56Z),
        returns equivalent epoch in microseconds
        (appended with current time's microseconds).

        Default value: today
    """
    incoming_dt = '2011-08-' + str(day) + ' 12:34:56'
    pattern     = '%Y-%m-%d %H:%M:%S'
    epoch       = int(time.mktime(time.strptime(incoming_dt, pattern)))
    current_us  = time.time() - long(time.time())
    epoch_us    = (epoch + current_us) * 1E6
    return int(epoch_us)

class TestHarness(object):
    def __init__(self, env, estimation_field='estimatedtime'):
        self.env = env
        self.estimation_field = estimation_field

    ############################################################################
    # Milestones CRUD methods #
    ############################################################################
    def milestone_get(self, milestone_no=None):
        """ Returns specific milestone_no (all milestones if not supplied). """

        if not milestone_no:
            result = self._do_SQL('SELECT name FROM milestone')
            result = set([(i, elem[0]) for i, elem in enumerate(result)])
        else:
            result = self._do_SQL('SELECT id FROM ticket WHERE milestone=?',
                    (milestone_no,), single_result=True)

        return result

    ############################################################################
    # TracTicket CRUD methods #
    ############################################################################
    def tix_get_estimatedtime(self, tkt_id):
        result = self._do_SQL(
            'SELECT value FROM ticket_custom WHERE ticket=%s AND name=%s',
            (tkt_id, self.estimation_field), single_result=True
        )

        if result:
            return result[0]
        else:
            raise RuntimeError('Error: supplied id#%d invalid!' % tkt_id)

        return None

    def tix_set_estimatedtime(self, tkt_id, new_estimatedtime):
        self._do_SQL(
            'UPDATE ticket_custom SET value=%s WHERE ticket=%s AND name=%s',
            (new_estimatedtime, tkt_id, self.estimation_field)
        )

    def tix_create_single(self, options={}, when=None, estimatedtime=0):
        """ Creates a single TracTicket (updated with options) at when. """

        ticket = Ticket(self.env)
        ticket_fields = {
            'milestone': None,
            'status'   : 'new',
            'reporter' : 'lshift',
            'summary'  : 'Ticket',
            self.estimation_field: str(estimatedtime)
        }
        ticket_fields.update(options)
        ticket.populate(ticket_fields)
        ticket.insert(when)

    def create_random_nonzero_tickets(self, milestone_names=['milestone2']):
        if isinstance(milestone_names, str):
            milestone_names = [ milestone_names ]

        for milestone in milestone_names:
            num_tickets = random.sample(range(1,16), 1)[0]
            self.tix_create(num_tickets, milestone, ['1h', '1d'])

        return num_tickets

    def tix_create(self, num_tickets=1, milestone=None, estimatedtimes=[]):
        """
            Creates num_tickets of TracTickets for a particular milestone,
            optionally specifying estimatedtimes for these Tickets.
        """

        tix_fields = { 'milestone': milestone }
        tix_id     = self._last_tix_id()
        for offset in range(num_tickets):
            if offset < len(estimatedtimes):
                estimatedtime = estimatedtimes[offset]
            else:
                estimatedtime = random.sample(range(60), 1)[0]

            tix_fields.update({
                'summary': 'Ticket #%s' % tix_id
            })
            self.tix_create_single(tix_fields, estimatedtime=estimatedtime)

            tix_id += 1

    def tix_delete_all(self):
        """ Deletes all TracTickets from DB. """

        self._do_SQL('DELETE FROM ticket_change')
        num_tickets = self._num_tix()
        for tix_id in range(num_tickets + 1):
            try:
                Ticket(self.env, tkt_id=tix_id).delete()
            except:
                pass

    ############################################################################
    # TracTicket helper methods #
    ############################################################################
    def _all_tix(self):
        """ Query DB for a list of all current TracTickets. """

        results = self._do_SQL("""
            SELECT ticket, summary, milestone, estimatedtime, created, modified
            FROM (
              SELECT
                t.id AS ticket, summary AS summary,
                component, version, severity, milestone, status,
                CASE WHEN
                  estimatedtime.value = '' OR estimatedtime.value IS NULL THEN 0
                  ELSE estimatedtime.value END as estimatedtime,
                CASE WHEN
                  estimatedtime.value = '' OR estimatedtime.value IS NULL THEN 0
                  ELSE CAST( estimatedtime.value AS DECIMAL ) END
                as estimatedtime_number,
                time AS created, changetime AS modified,
                description AS _description_,
                changetime AS _changetime, reporter AS _reporter, 0 as _ord
                FROM ticket as t
                LEFT JOIN ticket_custom as estimatedtime
                    ON estimatedtime.name='estimatedtime'
                    AND estimatedtime.Ticket = t.Id
            )  as tbl
            ORDER BY  _ord ASC, ticket
        """)
        tickets = [ ('ticket_id', 'summary', 'milestone', 'estimatedtime',
                     'created', 'modified') ]
        for row in results:
            tickets.append(row)

        print '\n', '\n'.join(
            [ '\t\t'.join([str(col) for col in row]) for row in tickets ]
        )

        return tickets

    def _last_tix_id(self):
        """ Query DB for highest TracTicket ID used (or 1 if None). """

        value = self._do_SQL('SELECT MAX(id) FROM ticket', single_result=True)
        return int(value[0]) + 1 if value[0] else 1

    def _num_tix(self):
        """ Query DB for number of TracTickets. """

        return self._do_SQL('SELECT COUNT(id) FROM ticket', single_result=True)[0]

    def _do_SQL(self, sql, params=None, single_result=False):
        """ Idiomatically executes given SQL string (& optionally params). """

        cursor = None
        result = []

        if sql.upper().strip().startswith('SELECT'):
            # read
            conn = self.env.get_read_db()
            cursor = conn.cursor()

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            if single_result:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()

        else:
            # write
            @self.env.with_transaction()
            def implementation(db):
                cursor = db.cursor()

                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                cursor.execute("VACUUM;")

        # cleanup
        if cursor:
            cursor.close()
        cursor = None
        del cursor

        return result
