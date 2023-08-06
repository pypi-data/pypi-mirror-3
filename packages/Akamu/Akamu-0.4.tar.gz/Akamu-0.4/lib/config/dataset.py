# -*- encoding: utf-8 -*-
'''
Manage connection to and querying over an RDF dataset
for an Akara web application

Requires a configuration section, for example:

class dataset:
    mysqlDataset = {
        'type'         : "MySQL",
        'mysqldb'      : "[..]",
        'mysqluser'    : "[..]",
        'mysqlhost'    : "[..]",
        'mysqlpw'      : "[..]",
        'mysqlStoreId' : "[..]",
        'mysqlPort'    : "[..]"
    }

    sparqlQueryFiles = "/path/to/query/files"
    nsPrefixes       = { "..prefix.." : rdflib.Namespace  }

    sqlLiteralProps  = [ .., .., .. ]
    sqlResourceProps = [ .., .., .. ]
'''

import os, akara
from akara import registry
from rdflib import plugin, URIRef
from rdflib.store import Store, NO_STORE
from rdflib.Graph import Graph, ConjunctiveGraph

def ReplaceGraph(datasetOrName,graphUri,srcStream,format='xml',storeName=True):
    #TODO: do a lazy replace (only the diff - ala 4Suite repository)
    store = ConnectToDataset(datasetOrName) if storeName else datasetOrName
    g = Graph(store, graphUri)
    g.remove((None, None, None))
    g.parse(srcStream)
    store.commit()

def ClearGraph(datasetOrName,graphUri,storeName=True):
    #TODO: do a lazy replace (only the diff - ala 4Suite repository)
    store = ConnectToDataset(datasetOrName) if storeName else datasetOrName
    g = Graph(store, graphUri)
    g.remove((None, None, None))
    store.commit()

def DestroyOrCreateDataset(datasetName):
    """
    Initialize dataset (if exists) or create it if it doesn't
    """
    datasetConfig = akara.module_config().get(datasetName)
    assert datasetConfig is not None, datasetName
    if datasetConfig['type'] == 'MySQL':
        configStr = 'user=%s,password=%s,db=%s,port=%s,host=%s' % (
            datasetConfig.get('mysqluser'),
            datasetConfig.get('mysqlpw'),
            datasetConfig.get('mysqldb'),
            datasetConfig.get('mysqlPort',3306),
            datasetConfig.get('mysqlhost')
            )
        store = plugin.get('MySQL', Store)(datasetConfig.get('mysqlStoreId'))
        rt = store.open(configStr,create=False)
        if rt == NO_STORE:
            store.open(configStr,create=True)
        else:
            store.destroy(configStr)
            store.open(configStr,create=True)
        return store
    else:
        raise NotImplementedError("Only dataset supported by Akamu is MySQL")


def ConnectToDataset(datasetName):
    """
    Return rdflib store corresponding to the named dataset, whose connection
    parameters are specified in the configuration file
    """
    datasetConfig = akara.module_config().get(datasetName)
    assert datasetConfig is not None
    if datasetConfig['type'] == 'MySQL':
        configStr = 'user=%s,password=%s,db=%s,port=%s,host=%s' % (
            datasetConfig.get('mysqluser'),
            datasetConfig.get('mysqlpw'),
            datasetConfig.get('mysqldb'),
            datasetConfig.get('mysqlPort',3306),
            datasetConfig.get('mysqlhost')
        )
        store = plugin.get('MySQL', Store)(datasetConfig.get('mysqlStoreId'))
        store.open(configStr, create=False)
        store.literal_properties.update(
            map(URIRef,akara.module_config().get("sqlLiteralProps",[]))
        )
        store.resource_properties.update(
            map(URIRef,akara.module_config().get("sqlResourceProps",[]))
        )
        return store
    else:
        raise NotImplementedError("Only dataset supported by Akamu is MySQL")

def Query(queryFile,datasetName,graphUri=None,params=None):
    """
    Evaluate a query (stored in a SPARQL file in the location indicated in the
    configuration) against the given dataset (and optional named graph within it)
    using the optional parameters given
    """
    store = ConnectToDataset(datasetName)
    g     = ConjunctiveGraph(store) if graphUri is None else Graph(store,graphUri)
    qFile = os.path.join(akara.module_config().get("sparqlQueryFiles"),queryFile)
    query = open(qFile).read()
    query = query if params is None else query % params
    initNs = dict([ (k,URIRef(v)) for k,v in akara.module_config().get("nsPrefixes",{})])
    for rt in g.query(
        query,
        initNs=initNs):
        yield rt