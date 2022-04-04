# -*- coding: utf-8 -*-
import textwrap
import logging
import os
import sys
import ast
import json
import psycopg2
import ast
import pymongo
import datetime
from typing import List, Union
from timeit import default_timer as timer
from pymongo import MongoClient
from threading import Thread
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo import api, fields, models, tools, _
# from datetime import datetime,timedelta
_logger = logging.getLogger(__name__)

# region configuration
# MONGO CONFIG
MONGODB_ATLAS_URL = 'mongodb://admin:2444666668888888@35.213.153.122:27017,34.87.163.171:27017,35.185.180.53:27017/?authSource=admin&replicaSet=rs&readPreference=primary&ssl=false'
DATABASE = 'bankdatabase'
COLLECTION = 'accounts'
# endregion configuration


class BaseMongo(object):
    def __init__(self, database=DATABASE, collection=COLLECTION):
        self.cr = self.connection_db(database, collection)

    def connection_db(self, database, collection):
        mongo_client = MongoClient(MONGODB_ATLAS_URL)
        print(f"MongoDBClient connect ==== {mongo_client}")
        db = mongo_client[database]
        cr = db[collection]
        return cr


class BasePostgres(object):

    def __init__(self):
        # start cr when new BasePostgres
        self.cursor = None
        self.connection = None

    def connect(self):
        """ Connect to the PostgreSQL database server """
        conn = None
        try:
            # read connection parameters
            #params = config()
            host = '34.87.169.53'
            database = 'postgres'
            user = 'pgadmin'
            password = 'ffCvE6Cx7Cdj'

            # connect to the PostgresSQL server
            print('Connecting to the PostgreSQL database...')
            #conn = psycopg2.connect(**params)
            conn = psycopg2.connect(host=host,
                                    database=database,
                                    user=user,
                                    password=password)

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            print('Database connected.')
            return conn

    def execute_sql(self, query, mode='insert'):
        try:
            # open new connection
            if not self.connection:
                connection = self.connect()
                self.connection = connection
            else:
                connection = self.connection
            cursor = connection.cursor()
            cursor.execute(query)
            self.connection = connection
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            return cursor


# ENUMS
class STATES(object):
    NEW = 'new'
    FAILED = 'failed'
    DONE = 'done'


STATES = [
    (STATES.NEW, 'New'),
    (STATES.FAILED, 'Failed'),
    (STATES.DONE, 'Done'),
]
IGNORE_TEXT = ['delete', 'alter table']


class ChangeEventLog(models.Model):
    _name = "change.event.log"

    # region odoo fields
    # for oplog
    oplog_id = fields.Char("Oplog ID")
    ts = fields.Datetime("Oplog Timestamp")
    full_oplog = fields.Text('Full Oplog')
    prevOpTime = fields.Char('Prevouse OpTime')

    # for documents
    mongo_document_id = fields.Char("Mongo Document Id")
    mongo_name_space = fields.Char("Name Space")
    type = fields.Char("Operation Type")
    change_event_values = fields.Text("Change Event Value")


    # track this change document is updated to PostgresDB
    status = fields.Selection(STATES, string="Document State")
    mapping_id = fields.Many2one('model.mapping', string='Model Mapping')
    res_id = fields.Char('Record ID')
    error_msg = fields.Text('Error Messages')
    sql_executed = fields.Text('Sql Executed')
    # endregion

    # region for CRUD
    def write(self, vals):
        res = super(ChangeEventLog, self).write(vals)
        return res
    # endregion

    # region to collect events
    def collect_change_stream(self, db, collection, type=None):
        _logger.info(f"Collect change stream: running ............with db={db}, collection={collection}")
        mongo_base = BaseMongo(db, collection)
        accounts_collection = mongo_base.cr
        # Change stream pipeline
        pipeline = [
            # {'$match': {'operationType': 'insert'}},
            # {'$match': {'fullDocument.accounts.type': 'checking'}},
            # {'$match': {'fullDocument.accounts.balance': {"$lt": 0}}}
        ]
        index = self._context.get('index', 0)
        print(f"index ===== {index}")
        try:
            cr = accounts_collection.watch(pipeline=pipeline, full_document='updateLookup')
            index = 0
            while cr.alive:
                # index = 1
                self.with_context(index=index)
                _logger.info("Collecting ............")
                next_change = cr.next()
                if next_change:
                    db = next_change.get('ns', {}).get('db', '').strip()
                    coll = next_change.get('ns', {}).get('coll', '').strip()
                    vals = {
                        'oplog_id': next_change.get('_id', {}).get('_data', '').strip(),
                        'mongo_document_id': next_change.get('fullDocument', {}).get('_id', ''),
                        'mongo_name_space': f"{db}.{coll}",  # format: database_name.collection_name
                        'type': next_change.get('operationType', ''),
                        'change_event_values': next_change.get('fullDocument', ''),
                        'full_oplog': str(next_change),
                        'status': 'new',
                    }
                    msg = f"===== Current stream ======: value to creat = {vals}"
                    _logger.info(msg)

                    # add new record
                    self.create(vals)
                    self._cr.commit()
        except KeyboardInterrupt:
            self.keyboard_shutdown()

    def collect_events_from_oplog(self, mode=None):
        client = MongoClient(MONGODB_ATLAS_URL)
        oplog = client.local.oplog.rs
        query = {
            'ns': {'$in': ['marketplace_stg_order_v2.order', 'marketplace_stg_order_v2.order_item']},
            # 'ns': {'$in': ['bankdatabase.accounts']},
            'op': {'$in': ['i']}
            # 'ts': {'$gt': ts},
        }
        # covert ts to datetime: ts.as_datetime()

        try:
            print(f"FIND QUERY============== :{query}")
            first = oplog.find(query).limit(-1).sort('$natural', pymongo.ASCENDING).next()
            ts = first['ts']
            print(f"ts ===== {ts} - {ts.as_datetime()}")
            index = 0
            while True:
                cursor_query = {
                    'ts': {'$gt': ts},
                    'ns': {'$in': ['marketplace_stg_order_v2.order', 'marketplace_stg_order_v2.order_item']},
                    'op': {'$in': ['i', 'u']}
                }
                cursor = oplog.find(cursor_query, cursor_type=pymongo.CursorType.TAILABLE_AWAIT, oplog_replay=True)
                while cursor.alive:
                    for next_change in cursor:
                        index += 1
                        ts = next_change['ts']
                        print(f"Processing ============: record number={index} , ts={ts}")

                        # parse params
                        ns = next_change.get('ns', '')
                        db = ns.split('.')[0]
                        coll =  ns.split('.')[1]
                        op = next_change.get('op', '').strip()
                        mongo_document_id = next_change.get('o', {}).get('_id', '') or next_change.get('o2', {}).get('_id', '')
                        change_event_values = next_change.get('o', {})
                        if op == 'i':
                            operationType = 'insert'
                        elif op == 'u':
                            operationType = 'update'
                        else:
                            operationType = op
                        vals = {
                            # oplog
                            'oplog_id': str(next_change.get('lsid', {}).get('id', '')),
                            'full_oplog': str(next_change),
                            # 'ts': ts.as_datetime if ts else False,
                            'prevOpTime': str(next_change.get('prevOpTime', {})),

                            # doc
                            'mongo_document_id': str(mongo_document_id).strip(),
                            'mongo_name_space': ns,
                            'type': operationType,
                            'change_event_values': str(change_event_values),
                            'status': 'new',
                        }
                        msg = f"===== Current oplog ======: value={vals}"
                        _logger.info(msg)

                        # add new record
                        self.create(vals)
                        self._cr.commit()
        except StopIteration:
            msg = "Can not found any records on oplog"
            logging.error(msg)
            print(msg)
        except Exception as error:
            msg = f"Exception === {error}"
            logging.error(msg)
            print(msg)
        return True

    def keyboard_shutdown(self):
        print('Interrupted ========== \n')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    # endregion collect events

    # region for process events
    def process_event_logs(self, mode=None):
        print('====================================================')
        get_valid_model_mapping = self.env['model.mapping'].get_valid_tables()
        for mapping in get_valid_model_mapping:
            self.process_a_name_space(mapping)
        return True

    def process_a_name_space(self, mapping):
        try:
            ns = f"{mapping.mongo_database}.{mapping.collection_name}"
            events = self.search([('mongo_name_space', '=', ns), ('status', 'in', ['new']), ('type', 'in', ['insert'])])
            base_pg = BasePostgres()
            mapping_docs = ast.literal_eval(mapping.fields_mapping)
            pg_column_names = self.env['model.mapping'].get_table_column_name(mapping.postgres_table_name)
            start = timer()
            for event in events:
                kw = {
                    'mapping_docs': mapping_docs,
                    'mapping': mapping,
                    'base_pg':base_pg,
                    'pg_column_names': pg_column_names
                }
                self.process_a_event(event=event, **kw)
            end = timer()

            print('====================================================')
            print('Total Time Elapsed (in seconds): ' + str(end - start))
            print('====================================================')
            return True

        except Exception as error:
            print(f"print Exception ====: {error}")

    def process_a_event(self, event, **kwargs):
        keys_to_insert = []
        values_to_insert = []
        mapping_docs, mapping, base_pg = kwargs.get('mapping_docs'), kwargs.get('mapping'), kwargs.get('base_pg')
        pg_column_names = kwargs.get('pg_column_names', []) or []
        assert type(pg_column_names) is list, f"pg_column_names must be a list"
        try:
            event_value = event.change_event_values
            document = covert_document_string_to_dict(event_value)
            if event.type == 'insert' and document:
                for mongo_key, pg_key in mapping_docs.items():
                    if pg_key[0] in pg_column_names:
                        # append column postgres to list
                        keys_to_insert.append(pg_key[0])

                        # append column value to list
                        # format value as data_type which is defined in Model Mapping
                        value = convert_data(
                            data=document.get(mongo_key, ''),
                            data_type=pg_key[1]
                        )
                        values_to_insert.append(value)

            # make insert sql
            assert type(keys_to_insert) is list and keys_to_insert, f"keys_to_insert is empty"

            print(f'=========:  keys_to_insert={keys_to_insert}, values_to_insert={values_to_insert}')
            keys = ','.join(keys_to_insert)
            # values = "'" +  "','".join(values_to_insert) + "'"
            values = str(tuple(values_to_insert)).replace('None', 'null')
            print(f'=========:  keys={keys}, values={values}')
            sql_to_insert = f"INSERT INTO {mapping.postgres_table_name}({keys}) VALUES {values} returning id;"
            print(f'=========:  sql_to_insert={sql_to_insert}')

            # insert to postgresDB
            new_row_id = insert_sql(sql_to_insert, base_pg)

            # update new_row_id of postgres to event
            event.status = 'done'
            event.sql_executed = sql_to_insert
            event.res_id = f'{mapping.postgres_table_name}.{new_row_id}'
            self._cr.commit()
            return True

        except Exception as error:
            print(f"print Exception ====: {str(error)}")
            event.error_msg = str(error)
            self._cr.commit()
    # endregion for process events


class ModelMapping(models.Model):
    _name = 'model.mapping'

    # region for fields
    @api.depends('mongo_database', 'collection_name')
    def _compute_name(self):
        for rec in self:
            rec.name = f'{rec.mongo_database or ""}.{rec.collection_name or ""}/{rec.postgres_table_name}'

    name = fields.Char(string='Name', compute='_compute_name')
    # mongo
    mongo_database = fields.Char('Mongo Database Name')
    collection_name = fields.Char(string='Mongo Collection Name')
    fields_mapping = fields.Text('Fields Mapping', help='Defines as key:value\n Key is column name\n Value is colum data type')

    # postgres
    postgres_table_name = fields.Char('Postgres Table Name')
    create_table = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes', string="Run sql to create new table")
    sql_execute = fields.Text('SQL Execute',
                              help='This fields will run and create new table on Postgres if it"s not existing')
    is_executed = fields.Boolean('Is executed SQL')
    option = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], string='Option', default='inactive')
    # endregion

    # region for validation
    def validate_fields(self, vals):
        sql_execute = vals.get('sql_execute') if vals.get('sql_execute') else self.sql_execute or ''
        if sql_execute:
            for text in IGNORE_TEXT:
                if text in sql_execute.lower():
                    raise UserError(_(f"You can not use keywords in {IGNORE_TEXT}"))
        fields_mapping = vals.get('fields_mapping', '') if vals.get('fields_mapping', '') else self.fields_mapping
        try:
            fields_mapping_dict = ast.literal_eval(fields_mapping)
            pg_keys = self.get_pg_colum_name_from_field_mapping(fields_mapping)
            assert len(pg_keys) > 0, f"Can not found any columns in fields_mapping {fields_mapping}"
        except Exception as e:
            raise UserError(_(f"fields_mapping field should be json"))

    def get_pg_colum_name_from_field_mapping(self, fields_mapping):
        if fields_mapping:
            fields_mapping_dict = ast.literal_eval(fields_mapping)
            pg_keys = []
            for mongo_key, pg in fields_mapping_dict.items():
                assert type(pg) is list and len(pg) == 2, f"value {pb} must be a list and there's 2 items"
                pg_keys.append(pg[0])
            return pg_keys
        else:
            raise UserError(_(f"Can not found fields_mapping"))

    def get_valid_tables(self):
        """
        Steps:
        - Get records in model.mapping
        - Check its table name:
          + If table name is existing in postgres -> append to valid_records
          + else ==> pass
        :return: list of model.mapping which is valid (aka valid_records)
        """
        # get all table from postgres
        query = textwrap.dedent(f'''
            select table_name from information_schema.tables 
            where table_schema = 'public';
        ''').replace('\n', '')
        base_pg = BasePostgres()
        cr = base_pg.execute_sql(query)
        rows = cr.fetchall()
        pg_tables = [rec[0] for rec in rows]

        # check
        mappings = self.search([])
        valid_tables = []
        for rec in mappings:
            if rec.postgres_table_name and rec.postgres_table_name in pg_tables:
                valid_tables.append(rec)

        print(f"valid_tables ==={valid_tables}")
        return valid_tables
    # endregion for validation

    # region for CRUD
    @api.model
    def create(self, vals):
        self.validate_fields(vals)
        return super(ModelMapping, self).create(vals)

    def write(self, vals):
        self.validate_fields(vals)
        res = super(ModelMapping, self).write(vals)

        # run other after record is written
        return res
    # endregion for CRUD
    
    # region for action and features
    def action_create_new_table(self):
        try:
            base_pg = BasePostgres()
            for rec in self:
                sql_execute = rec.sql_execute
                print(f"sql_execute ==== {sql_execute}")
                if sql_execute:
                    base_pg.execute_sql(sql_execute)
                    base_pg.connection.commit()
                    rec.is_executed = True
                else:
                    logging.info("No SQL to run =========")
        except Exception as error:
            raise UserError(_(str(error)))
            close_pg_connection(base_pg)
        finally:
            close_pg_connection(base_pg)

    def get_table_column_name(self, table_name):
        try:
            base_pg = BasePostgres()
            sql = f"SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}';"
            cursor = base_pg.execute_sql(sql)
            recs = cursor.fetchall()
            
            # get table names
            table_names = []
            for rec in recs:
                table_names.append(rec[0])
            return table_names
        except Exception as error:
            raise UserError(_(str(error)))
            close_pg_connection(base_pg)
        finally:
            close_pg_connection(base_pg)

    def action_audit(self):
        self.ensure_one()

        # compare postgres fields in Fields Mapping to columns in postgres
        postgres_table_name = self.postgres_table_name
        column_names = self.get_table_column_name(postgres_table_name)
        assert column_names, f"Can not found any conlums in table {postgres_table_name}"

        pg_mapping_columns = self.get_pg_colum_name_from_field_mapping(fields_mapping)
        invalid_column = []
        for column in pg_mapping_columns:
            if column not in column_names:
                invalid_column.append(column)
        if invalid_column:
            raise UserError(_(f"Columns {invalid_column} are not in table {postgres_table_name}"))
        fields_mapping_is_ok = True

        # check sql_type is yes -> check is_executed_sql

        if self.sql_type == 'yes':
            if self.is_executed is False:
                raise UserError(_("SQL to create table is not run"))
        self.option = True
    # endregion for action and features


# region base
def close_pg_connection(base_pg):
    if base_pg and base_pg.connection:
        if base_pg.cursor:
            base_pg.cursor.close()
        base_pg.connection.close()


def convert_data(data, data_type):
    data_type = data_type.lower() if data_type else None
    if data_type == 'boolean':
        return True if data else False
    if data_type in ['str', 'char', 'text', 'character', 'datetime', 'date', 'timestamp']:
        return str(data) if data else None
    elif data_type == 'float':
        return float(data) if data else None
    elif data_type == 'int':
        return int(data) if data else None
    else:
        msg = 'Data type is not supported'
        raise msg


def insert_sql(sql_to_insert, base_pg=None):
    if base_pg is None:
        base_pg = BasePostgres()
    cursor = base_pg.execute_sql(sql_to_insert)
    new_row_id = cursor.fetchone()[0]
    base_pg.connection.commit()
    print(f"new_row_id ==== {new_row_id}")
    return new_row_id

def covert_document_string_to_dict(document):
    """
    :param document: "{'id': ObjectId('623d')}"
    :return: {'id': '623d'}
    """
    document =  document.replace('ObjectId(', '').replace("')", "'")
    try:
        document = ast.literal_eval(document)
    except:
        document = eval(document)
    print(f"document ==== {document}")
    return document

# endregion base