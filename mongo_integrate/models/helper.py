#!/usr/bin/env python3
import time
import pymongo
from pymongo.cursor import _QUERY_OPTIONS
from pymongo.errors import AutoReconnect
from bson.timestamp import Timestamp
from pymongo.cursor import CursorType
from pymongo import MongoClient
from threading import Thread

MONGODB_ATLAS_URL = 'mongodb://admin:2444666668888888@35.213.153.122:27017,34.87.163.171:27017,35.185.180.53:27017/?authSource=admin&replicaSet=rs&readPreference=primary&ssl=false'
DATABASE = 'bankdatabase'
COLLECTION = 'accounts'


class BaseMongo(object):
    def connection_db(self):
        from datetime import datetime,timedelta

        client = MongoClient(MONGODB_ATLAS_URL)
        oplog = client.local.oplog.rs
        query = {
            'ns': {'$in': ['marketplace_stg_order_v2.order', 'marketplace_stg_order_v2.order_item']},
            'op': {'$in': ['i', 'u']},
            # 'ts': {'$gt': ts},
            # 'ts': {'$gt': Timestamp(1648802554, 187)}
        }
        # covert ts to datetime: ts.as_datetime()
        first = oplog.find(query).limit(-1).sort('$natural', pymongo.ASCENDING).next()
        print(f"first ===== {first}")
        ts = first['ts']
        print(f"ts ===== {ts} - {ts.as_datetime()}")
        index = 0
        while True:
            cursor = oplog.find({ 'ns': {'$in': ['marketplace_stg_order_v2.order', 'marketplace_stg_order_v2.order_item']},
                                 'op': {'$in': ['i', 'u']}},
                                cursor_type=pymongo.CursorType.TAILABLE_AWAIT,
                                oplog_replay=True)
            while cursor.alive:
                for doc in cursor:
                    ts = doc['ts']
                    index += 1
                    print(f"Processed ============: {index}")
                    print(f"DOC ==================: {ts.as_datetime()} - {doc['ui']} - {doc['ns']}\n")

BaseMongo().connection_db()


class MongoDocsExam(object):
    def log(self):
        log = """
        {
            "_id" : {
                "_data" : "8262467574000001712B022C0100296E5A10046B2F03CE0ED54151B813A3261543B0DF46645F69640064624569B0358B9852EFD0C4D60004"
            },
            "operationType" : "update",
            "clusterTime" : Timestamp(1648784756, 369),
            "fullDocument" : {
                "_id" : ObjectId("624569b0358b9852efd0c4d6"),
                "cart_no" : "LGPFW961",
                "price" : 14846000,
                "source" : "thuocsi-web",
                "total_item" : 4,
                "created_time" : ISODate("2022-03-31T08:43:28.688Z"),
                "last_action_time" : ISODate("2022-03-31T08:55:10.482Z"),
                "customer_code" : "HCUXQK7X",
                "region_codes" : [
                    "MN_ADM",
                    "MIENNAM",
                    "73XF1R94ABC"
                ],
                "status" : "DRAFT",
                "total_price" : 14846000,
                "ref_cart_item" : NumberLong("1648716208688891471"),
                "total_quantity" : 4,
                "cart_id" : NumberLong(515521),
                "account_id" : NumberLong(11368),
                "customer_id" : NumberLong(2450),
                "province_code" : "93",
                "district_code" : "930",
                "last_updated_time" : ISODate("2022-04-01T03:45:56.540Z"),
                "region_code" : "107TQTAR1Y7G",
                "sub_price" : 14846000,
                "ward_code" : "31321",
                "customer_address_code" : "6Q9K49CA",
                "customer_district_code" : "777",
                "customer_name" : "Anh Tran QC",
                "customer_phone" : "0923567663",
                "customer_province_code" : "79",
                "customer_region_code" : "107TQTAR1Y7G",
                "customer_shipping_address" : "ABC street",
                "customer_ward_code" : "27457",
                "delivery_method" : "DELIVERY_PLATFORM_NORMAL",
                "invoice" : {
                    "invoice_request" : true,
                    "company_name" : "Pharmacy",
                    "tax_code" : "0212730426-018",
                    "company_address" : "12 Street, phương 4 quận 11",
                    "email" : "abcd89@gmail.com"
                },
                "payment_method" : "PAYMENT_METHOD_NORMAL",
                "redeem_code" : [ ],
                "customer_email" : "abcd89@gmail.com",
                "total_fee" : 726000
            },
            "ns" : {
                "db" : "marketplace_stg_order_v2",
                "coll" : "cart"
            },
            "documentKey" : {
                "_id" : ObjectId("624569b0358b9852efd0c4d6")
            },
            "updateDescription" : {
                "updatedFields" : {
                    "last_updated_time" : ISODate("2022-04-01T03:45:56.540Z")
                },
                "removedFields" : [ ]
            }
        }
        """
        return log
