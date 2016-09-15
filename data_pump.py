"""
Script that continuously posts Chatter threads using a dataset from a Facebook
group. See README.md for more details.
"""

import os
import random
import sqlite3
import time

from simple_salesforce import Salesforce

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


# You need to download the dataset from https://www.kaggle.com/mchirico/cheltenham-s-facebook-group.
# (Free Kaggle account required. Download cheltenham-s-facebook-group.zip and extract the sqlite file.)
CONN = sqlite3.connect('cheltenham-facebook-group.sqlite')

# You may want to set a delay here to avoid hitting rate limits.
DELAY = os.environ.get('DELAY_BETWEEN_POSTS') or 0

# If RECONSTRUCT_THREADS is True, we'll post random feed items with all of their
# comments from the original Facebook threads. If it's False, we'll post random
# feed items with random comments.
RECONSTRUCT_THREADS = os.environ.get('RECONSTRUCT_THREADS') or True

# If RECONSTRUCT_THREADS is False, these settings control how many comments get posted.
MIN_COMMENTS = os.environ.get('MIN_COMMENTS') or 3
MAX_COMMENTS = os.environ.get('MAX_COMMENTS') or 5

class SalesforceHelper(object):

    def __init__(self):
        self.sf = Salesforce(password=os.environ.get('SFDC_PASSWORD'),
                             username=os.environ.get('SFDC_USERNAME'),
                             security_token=os.environ.get('SFDC_TOKEN'))

        # Cache the possible ParentIds that we'll post Chatter feed items to.
        # For the purposes of our demonstration, We'll use Users, Groups, and Accounts only.
        self.parent_ids = []
        soql_queries = ["SELECT Id FROM User WHERE IsActive = True AND UserType = 'Standard'",
                        "SELECT Id FROM CollaborationGroup WHERE CollaborationType = 'Public' AND IsArchived = False AND NetworkId = null",
                        "SELECT Id FROM Account",
                       ]
        for query in soql_queries:
            result = self.sf.query(query)
            ids = [x['Id'] for x in result['records']]
            self.parent_ids.extend(ids)

            # Also store the user IDs.
            if " FROM User " in query:
                self.user_ids = ids

    def get_random_parent(self):
        return random.choice(self.parent_ids)

    def get_random_user(self):
        return random.choice(self.user_ids)

    def post_feed_item(self, data):
        return self.sf.FeedItem.create(data)

    def post_comment(self, data):
        return self.sf.FeedComment.create(data)


def replace_special_chars(msg):
    s = msg.replace('{COMMA}', ',')
    s = s.replace('{APOST}', "'")
    s = s.replace('{RET}', "\n")
    return s


def post_random_thread(sf):
    for (pid, post_body) in CONN.execute("SELECT pid, msg FROM post ORDER BY random() LIMIT 1"):
        post_body = replace_special_chars(post_body)

        print post_body

        random_parent = sf.get_random_parent()
        random_user = sf.get_random_user()

        feed_item = {'Body': post_body,
                     'ParentId': random_parent,
                     'CreatedById': random_user,
                    }

        result = sf.post_feed_item(data=feed_item)

        if result['success']:
            feed_item_id = result['id']
        else:
            print "Error posting feed item: {}, input: {}".format(result['errors'], feed_item)
            continue

        time.sleep(DELAY)

        # Post comments.

        if RECONSTRUCT_THREADS:
            query, params = "SELECT cid, msg FROM comment WHERE pid=? ORDER BY timeStamp", [pid]
        else:
            num_comments = random.randint(MIN_COMMENTS, MAX_COMMENTS)
            query, params = "SELECT cid, msg FROM comment ORDER BY random() LIMIT ?", [num_comments]

        for (cid, comment_body) in CONN.execute(query, params):
            comment_body = replace_special_chars(comment_body)
            print "  ", comment_body

            random_user = sf.get_random_user()
            comment = {'CommentBody': comment_body,
                       'FeedItemId': feed_item_id,
                       'CreatedById': random_user,
                      }
            result = sf.post_comment(data=comment)
            if not result['success']:
                print "Error posting comment: {}, input: {}".format(result['errors'], comment)
                continue

            time.sleep(DELAY)


if __name__ == '__main__':
    sf = SalesforceHelper()
    while True:
        try:
            post_random_thread(sf)
        except Exception as e:
            print e
